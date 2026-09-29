"""Play Jev wording variants against each other and write an HTML report."""

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from html import escape
from itertools import combinations
from pathlib import Path

from schnapsen.engine import counting_eyes, legal_action_ids, new_match, start_deal
from schnapsen.harness import HarnessError, _blank
from schnapsen.jev_player import ask, begin_request, live_client
from schnapsen.keyfile import read_api_key
from schnapsen.turn import _accept, _fallback, close_match_clients

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "reports" / "jev-wording.html"
TURN_CAP = 80
_RUN_FILE = re.compile(r"-\d{8}T\d{6}(?:-\d+)?\.json$")


@dataclass(frozen=True)
class Variant:
    id: str
    name: str
    change: str
    instructions: str


VARIANTS = (
    Variant(
        "which-reach",
        "Which reach",
        "which + reach",
        "Which legal action gives you the best chance to reach 66 eyes before the opponent?",
    ),
    Variant(
        "select-reach",
        "Select reach",
        "select + reach",
        "Select the legal action that gives you the best chance to reach 66 eyes before the opponent.",
    ),
    Variant(
        "which-get",
        "Which get to",
        "which + get to",
        "Which legal action gives you the best chance to get to 66 eyes before the opponent?",
    ),
    Variant(
        "select-get",
        "Select get to",
        "select + get to",
        "Select the legal action that gives you the best chance to get to 66 eyes before the opponent.",
    ),
    Variant(
        "select-count",
        "Select counting",
        "select + counting eyes",
        "Select the legal action that gives you the best chance to reach 66 counting eyes before the opponent.",
    ),
)
PROMPTS = {variant.id: variant.instructions for variant in VARIANTS}
NAMES = {variant.id: f"{variant.id.upper()} {variant.name}" for variant in VARIANTS}
PAIRINGS = tuple(combinations((variant.id for variant in VARIANTS), 2))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play Jev prompt variants against each other.")
    parser.add_argument("--rounds", type=int, default=15)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not read_api_key().strip():
        return 1
    try:
        play_prompts(args.rounds, Path(args.report))
    except HarnessError:
        return 1
    return 0


def play_prompts(rounds: int, report: Path, *, client: object | None = None) -> None:
    totals = {variant.id: _blank() for variant in VARIANTS}
    pairings = []
    for left, right in PAIRINGS:
        pairings.append(_play_pairing(rounds, left, right, totals, client))
    run = {
        "played_at": _now().isoformat(timespec="seconds"),
        "rounds_per_pairing": rounds,
        "variants": [
            {
                "id": variant.id,
                "name": variant.name,
                "change": variant.change,
                "instructions": variant.instructions,
            }
            for variant in VARIANTS
        ],
        "players": totals,
        "pairings": pairings,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    _write_run(report, run)
    report.write_text(render_html(run, _load_runs(report)), encoding="utf-8")


def render_html(last: dict, runs: list[dict]) -> str:
    played = str(last["played_at"]).replace("T", " ")
    overall_players = _sum_players(runs)
    overall_pairings = [pairing for run in runs for pairing in run["pairings"]]
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>Jev prompt variants</title><style>"
        "body{font-family:sans-serif;margin:24px}"
        "table{border-collapse:collapse;margin:0 0 24px}"
        "td,th{border:1px solid #ccc;padding:4px 8px;text-align:left}"
        "</style></head><body>"
        "<h1>Jev prompt variants</h1>"
        + _prompt_table(last["variants"])
        + _result_section(
            "last",
            "Last run",
            f"{escape(played)}. Rounds per pairing: {last['rounds_per_pairing']}.",
            last["players"],
            last["pairings"],
            details=True,
        )
        + _result_section(
            "overall",
            "Overall",
            f"Runs: {len(runs)}.",
            overall_players,
            overall_pairings,
            details=False,
        )
        + "</body></html>"
    )


def _prompt_table(variants: list[dict]) -> str:
    rows = []
    for variant in variants:
        rows.append(
            "<tr>"
            f"<td>{escape(NAMES[variant['id']])}</td>"
            f"<td>{escape(variant['change'])}</td>"
            f"<td>{escape(variant['instructions'])}</td>"
            "</tr>"
        )
    return (
        "<h2>Prompts</h2><table>"
        "<tr><th>Variant</th><th>Change</th><th>Instruction</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def _result_section(section_id, title, intro, players, pairings, details: bool) -> str:
    body = (
        f'<section id="{section_id}">'
        f"<h2>{escape(title)}</h2>"
        f"<p>{intro}</p>"
        + (f"<p>{_group_line(players)}</p>" if _group_line(players) else "")
        + "<h3>Players</h3>"
        + _player_table(players)
        + "<h3>Pairings</h3>"
        + _pairing_table(pairings)
    )
    if details:
        body += _round_sections(pairings)
    return body + "</section>"


def _group_line(players: dict[str, dict]) -> str:
    parts = []
    changes = []
    for variant in VARIANTS:
        if variant.change not in changes:
            changes.append(variant.change)
    for change in changes:
        ids = [variant.id for variant in VARIANTS if variant.change == change]
        if len(ids) < 2:
            continue
        deals = sum(players[item]["deals_won"] for item in ids) / len(ids)
        points = sum(players[item]["game_points"] for item in ids) / len(ids)
        parts.append(
            f"{change.capitalize()} prompts, mean deals won {deals:.1f}, "
            f"mean game points {points:.1f}."
        )
    return " ".join(parts)


def _player_table(players: dict[str, dict]) -> str:
    rows = []
    for variant in VARIANTS:
        item = players[variant.id]
        rows.append(
            f'<tr data-player="{variant.id}">'
            f"<td>{escape(NAMES[variant.id])}</td>"
            f"<td>{escape(variant.change)}</td>"
            f"<td>{item['deals_won']}</td>"
            f"<td>{item['matches_won']}</td>"
            f"<td>{item['game_points']}</td>"
            f"<td>{item['eyes']}</td>"
            f"<td>{item['bummerl']}</td>"
            f"<td>{item['marriages']}</td>"
            f"<td>{item['exchanges']}</td>"
            f"<td>{item['closes']}</td>"
            f"<td>{item['replaced']}</td>"
            "</tr>"
        )
    return (
        "<table>"
        "<tr><th>Player</th><th>Change</th><th>Deals won</th><th>Matches won</th>"
        "<th>Game points</th><th>Counting eyes</th><th>Bummerl charges</th>"
        "<th>Marriages</th><th>Trump exchanges</th><th>Talon closes</th>"
        "<th>Replaced turns</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def _pairing_table(pairings: list[dict]) -> str:
    grouped: dict[tuple[str, str], dict] = {}
    order: list[tuple[str, str]] = []
    for pairing in pairings:
        key = (pairing["left"], pairing["right"])
        if key not in grouped:
            grouped[key] = {
                "deals": {key[0]: 0, key[1]: 0},
                "points": {key[0]: 0, key[1]: 0},
                "eyes": {key[0]: 0, key[1]: 0},
            }
            order.append(key)
        row = grouped[key]
        for item in pairing["rounds"]:
            row["eyes"][key[0]] += int(item["eyes"][key[0]])
            row["eyes"][key[1]] += int(item["eyes"][key[1]])
            winner = item["winner"]
            if winner in row["deals"]:
                row["deals"][winner] += 1
                row["points"][winner] += int(item["game_points"])
    rows = []
    for left, right in order:
        row = grouped[(left, right)]
        rows.append(
            f'<tr data-pairing="{left}-{right}">'
            f"<td>{escape(NAMES[left])}</td>"
            f"<td>{escape(NAMES[right])}</td>"
            f"<td>{row['deals'][left]}</td>"
            f"<td>{row['deals'][right]}</td>"
            f"<td>{row['points'][left]}</td>"
            f"<td>{row['points'][right]}</td>"
            f"<td>{row['eyes'][left]}</td>"
            f"<td>{row['eyes'][right]}</td>"
            "</tr>"
        )
    return (
        "<table>"
        "<tr><th>Seat A</th><th>Seat B</th>"
        "<th>Deals won A</th><th>Deals won B</th>"
        "<th>Game points A</th><th>Game points B</th>"
        "<th>Counting eyes A</th><th>Counting eyes B</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def _round_sections(pairings: list[dict]) -> str:
    sections = []
    for pairing in pairings:
        left, right = pairing["left"], pairing["right"]
        rows = []
        for index, round_row in enumerate(pairing["rounds"], start=1):
            rows.append(
                "<tr class=\"round\">"
                f"<td>{index}</td>"
                f"<td>{escape(NAMES.get(round_row['winner'], ''))}</td>"
                f"<td>{round_row['eyes'][left]}</td>"
                f"<td>{round_row['eyes'][right]}</td>"
                f"<td>{round_row['game_points']}</td>"
                f"<td>{_moves_html(round_row['moves'])}</td>"
                "</tr>"
            )
        sections.append(
            f"<h3>{escape(NAMES[left])} vs {escape(NAMES[right])}</h3>"
            "<table>"
            "<tr><th>Round</th><th>Winner</th>"
            f"<th>{escape(NAMES[left])} eyes</th>"
            f"<th>{escape(NAMES[right])} eyes</th>"
            "<th>Game points</th><th>Special moves</th></tr>"
            + "".join(rows)
            + "</table>"
        )
    return "".join(sections)


def _play_pairing(rounds, left, right, totals, client):
    recorded = []
    played = 0
    print(f"{NAMES[left]} vs {NAMES[right]}", flush=True)
    while played < rounds:
        match = new_match()
        match.players = {"computer": left, "human": right}
        try:
            turns = 0
            moves: list[str] = []
            while played < rounds and match.match_winner is None:
                deal = match.deal
                if deal is None:
                    raise HarnessError("no deal")
                if deal.phase == "ended":
                    row = _record_deal(match, left, right, totals, moves)
                    recorded.append(row)
                    played += 1
                    _print_round(left, right, played, row)
                    turns = 0
                    moves = []
                    if match.match_winner is not None:
                        _record_match(match, totals)
                        break
                    if played < rounds and not start_deal(match):
                        raise HarnessError("next deal did not start")
                    continue
                if deal.phase != "play":
                    raise HarnessError("unexpected phase")
                if turns >= TURN_CAP:
                    raise HarnessError("deal exceeded 80 turns")
                kind = match.players[deal.to_play]
                before = _fingerprint(match)
                _jev_turn(match, client, PROMPTS[kind])
                moves.extend(_special_moves(match, totals))
                turns += 1
                if match.choice_replaced:
                    totals[kind]["replaced"] += 1
                if match.notice == "missing-key" or _fingerprint(match) == before:
                    raise HarnessError("turn did not play")
        finally:
            close_match_clients(match)
    return {"left": left, "right": right, "rounds": recorded}


def _jev_turn(match, client, instructions: str) -> None:
    legal = legal_action_ids(match)
    if not legal:
        raise HarnessError("no legal action")
    fallback = sorted(legal)[0]
    if client is None:
        key = read_api_key()
        if not key:
            match.notice = "missing-key"
            match.choice_replaced = False
            return
    live = live_client(match, client)
    if live is None:
        match.notice = "missing-key"
        match.choice_replaced = False
        return
    _ask_or_fallback(match, live, legal, fallback, instructions)


def _ask_or_fallback(match, client, legal, fallback, instructions: str) -> None:
    begin_request(match)
    choice, failed = ask(match, client, legal, instructions)
    if failed:
        _fallback(match, fallback)
        return
    if choice is not None and _accept(match, choice):
        return
    choice, failed = ask(match, client, legal, instructions)
    if failed or choice is None or not _accept(match, choice):
        _fallback(match, fallback)


def _print_round(left, right, number, row) -> None:
    print(
        f"{NAMES[left]} vs {NAMES[right]}  round {number}: {NAMES.get(row['winner'], '')} wins, "
        f"{NAMES[left]} {row['eyes'][left]} eyes, {NAMES[right]} {row['eyes'][right]} eyes, "
        f"{row['game_points']} points. "
        f"Moves: {', '.join(row['moves']) if row['moves'] else 'none'}.",
        flush=True,
    )


def _special_moves(match, totals) -> list[str]:
    deal = match.deal
    action = None if deal is None else deal.last_action
    if action is None or not (action.exchange or action.closed or action.marriage):
        return []
    kind = match.players[action.seat]
    who = NAMES[kind]
    notes = []
    if action.exchange:
        totals[kind]["exchanges"] += 1
        took = action.took or "the face-up trump"
        notes.append(f"{who} exchanged the trump jack for {took}")
    if action.closed:
        totals[kind]["closes"] += 1
        notes.append(f"{who} closed the talon")
    if action.marriage:
        totals[kind]["marriages"] += 1
        eyes = 40 if action.marriage == deal.trump_suit else 20
        notes.append(f"{who} married in {action.marriage} ({eyes})")
    return notes


def _record_deal(match, left, right, totals, moves):
    deal = match.deal
    eyes = {left: counting_eyes(deal, "computer"), right: counting_eyes(deal, "human")}
    for kind, amount in eyes.items():
        totals[kind]["eyes"] += amount
    winner = deal.winner
    points = deal.game_points or 0
    if winner is not None:
        kind = match.players[winner]
        totals[kind]["deals_won"] += 1
        totals[kind]["game_points"] += points
    return {
        "winner": match.players.get(winner, "") if winner is not None else "",
        "eyes": eyes,
        "game_points": points,
        "moves": list(moves),
    }


def _record_match(match, totals):
    for seat, kind in match.players.items():
        totals[kind]["bummerl"] += match.bummerl[seat]
        if seat == match.match_winner:
            totals[kind]["matches_won"] += 1


def _moves_html(moves: list[str]) -> str:
    if not moves:
        return "none"
    return "<br>".join(escape(move) for move in moves)


def _write_run(report: Path, run: dict) -> Path:
    stamp = datetime.fromisoformat(str(run["played_at"])).strftime("%Y%m%dT%H%M%S")
    path = report.parent / f"{report.stem}-{stamp}.json"
    suffix = 2
    while path.exists():
        path = report.parent / f"{report.stem}-{stamp}-{suffix}.json"
        suffix += 1
    path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    return path


def _load_runs(report: Path) -> list[dict]:
    runs = []
    for path in sorted(report.parent.glob(f"{report.stem}-*.json")):
        if not _RUN_FILE.search(path.name):
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(payload, dict) and "players" in payload and "pairings" in payload:
            runs.append(payload)
    runs.sort(key=lambda item: str(item.get("played_at", "")))
    return runs


def _sum_players(runs: list[dict]) -> dict[str, dict]:
    totals = {variant.id: _blank() for variant in VARIANTS}
    for run in runs:
        players = run.get("players", {})
        for variant in VARIANTS:
            item = players.get(variant.id, {})
            for field in totals[variant.id]:
                totals[variant.id][field] += int(item.get(field, 0))
    return totals


def _now() -> datetime:
    return datetime.now().astimezone().replace(microsecond=0)


def _fingerprint(match):
    deal = match.deal
    return (
        deal.phase,
        deal.to_play,
        tuple((seat, card.token) for seat, card in deal.current_trick),
        tuple(card.token for card in deal.hands["human"]),
        tuple(card.token for card in deal.hands["computer"]),
        len(deal.talon),
        deal.closed,
        deal.marriage_eyes["human"],
        deal.marriage_eyes["computer"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
