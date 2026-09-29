"""Play every AI against every other AI and write an HTML report."""

import argparse
import json
import re
from datetime import datetime
from html import escape
from pathlib import Path

from schnapsen.engine import counting_eyes, new_match, start_deal
from schnapsen.keyfile import CHAT_MODEL, read_api_key, read_chat_api_key
from schnapsen.llm_player import LlmPlayer
from schnapsen.random_player import RandomPlayer
from schnapsen.turn import close_match_clients, take_ai_turn

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "reports" / "ai-rounds.html"
PAIRINGS = (
    ("jev", "random"),
    ("jev", "llm"),
    ("random", "llm"),
)
NAMES = {"jev": "Jev", "random": "Random", "llm": "LLM"}
TURN_CAP = 80
_RUN_FILE = re.compile(r"-\d{8}T\d{6}(?:-\d+)?\.json$")


class HarnessError(Exception):
    """A round did not finish, so no success report is written."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play AI Schnapsen rounds and write HTML.")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not read_api_key().strip() or not read_chat_api_key().strip():
        return 1
    try:
        play_rounds(args.rounds, Path(args.report))
    except HarnessError:
        return 1
    return 0


def play_rounds(
    rounds: int,
    report: Path,
    *,
    client: object | None = None,
    random_player: RandomPlayer | None = None,
    llm_player: LlmPlayer | None = None,
) -> None:
    totals = {kind: _blank() for kind in NAMES}
    pairings = []
    for left, right in PAIRINGS:
        pairings.append(
            _play_pairing(rounds, left, right, totals, client, random_player, llm_player)
        )
    run = {
        "played_at": _now().isoformat(timespec="seconds"),
        "model": CHAT_MODEL,
        "rounds_per_pairing": rounds,
        "players": totals,
        "pairings": pairings,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    _write_run(report, run)
    report.write_text(render_html(run, _load_runs(report)), encoding="utf-8")


def render_html(last: dict, runs: list[dict]) -> str:
    overall_players = _sum_players(runs)
    overall_pairings = [pairing for run in runs for pairing in run["pairings"]]
    played = str(last["played_at"]).replace("T", " ")
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>AI rounds</title><style>"
        "body{font-family:sans-serif;margin:24px}"
        "table{border-collapse:collapse;margin:0 0 24px}"
        "td,th{border:1px solid #ccc;padding:4px 8px;text-align:left}"
        "</style></head><body>"
        "<h1>AI rounds</h1>"
        f"<p>Model {escape(str(last['model']))}.</p>"
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


def _result_section(section_id, title, intro, players, pairings, details: bool) -> str:
    body = (
        f'<section id="{section_id}">'
        f"<h2>{escape(title)}</h2>"
        f"<p>{intro}</p>"
        "<h3>Players</h3>"
        + _player_table(players)
        + "<h3>Pairings</h3>"
        + _pairing_table(pairings)
    )
    if details:
        body += _round_sections(pairings)
    return body + "</section>"


def _player_table(totals: dict[str, dict]) -> str:
    rows = []
    for kind in ("jev", "random", "llm"):
        item = totals[kind]
        rows.append(
            f'<tr data-player="{kind}">'
            f"<td>{NAMES[kind]}</td>"
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
        "<tr><th>Player</th><th>Deals won</th><th>Matches won</th>"
        "<th>Game points</th><th>Counting eyes</th><th>Bummerl charges</th>"
        "<th>Marriages</th><th>Trump exchanges</th><th>Talon closes</th>"
        "<th>Replaced turns</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def _pairing_table(pairings: list[dict]) -> str:
    rows = []
    for row in _pairing_totals(pairings):
        left, right = row["left"], row["right"]
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
        title = f"{NAMES[pairing['left']]} vs {NAMES[pairing['right']]}"
        rows = []
        for index, round_row in enumerate(pairing["rounds"], start=1):
            winner = NAMES.get(round_row["winner"], "")
            rows.append(
                "<tr class=\"round\">"
                f"<td>{index}</td>"
                f"<td>{escape(winner)}</td>"
                f"<td>{round_row['eyes'][pairing['left']]}</td>"
                f"<td>{round_row['eyes'][pairing['right']]}</td>"
                f"<td>{round_row['game_points']}</td>"
                f"<td>{_moves_html(round_row['moves'])}</td>"
                "</tr>"
            )
        sections.append(
            f"<h3>{escape(title)}</h3>"
            "<table>"
            "<tr><th>Round</th><th>Winner</th>"
            f"<th>{escape(NAMES[pairing['left']])} eyes</th>"
            f"<th>{escape(NAMES[pairing['right']])} eyes</th>"
            "<th>Game points</th><th>Special moves</th></tr>"
            + "".join(rows)
            + "</table>"
        )
    return "".join(sections)


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
    totals = {kind: _blank() for kind in NAMES}
    for run in runs:
        players = run.get("players", {})
        for kind in NAMES:
            item = players.get(kind, {})
            for field in totals[kind]:
                totals[kind][field] += int(item.get(field, 0))
    return totals


def _pairing_totals(pairings: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], dict] = {}
    order: list[tuple[str, str]] = []
    for pairing in pairings:
        key = (pairing["left"], pairing["right"])
        if key not in grouped:
            grouped[key] = {
                "left": key[0],
                "right": key[1],
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
    return [grouped[key] for key in order]


def _now() -> datetime:
    return datetime.now().astimezone().replace(microsecond=0)


def _play_pairing(rounds, left, right, totals, client, random_player, llm_player):
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
                    _print_round(left, right, played, row, totals)
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
                take_ai_turn(match, client, random_player, llm_player)
                moves.extend(_special_moves(match, totals))
                turns += 1
                if match.choice_replaced:
                    totals[kind]["replaced"] += 1
                if match.notice in ("missing-key", "missing-chat-key") or _fingerprint(match) == before:
                    raise HarnessError("turn did not play")
        finally:
            close_match_clients(match)
    return {"left": left, "right": right, "rounds": recorded}


def _print_round(left, right, number, row, totals) -> None:
    score = ", ".join(f"{NAMES[kind]} {totals[kind]['deals_won']}" for kind in ("jev", "random", "llm"))
    print(
        f"{NAMES[left]} vs {NAMES[right]}  round {number}: {row['winner']} wins, "
        f"{NAMES[left]} {row['eyes'][left]} eyes, {NAMES[right]} {row['eyes'][right]} eyes, "
        f"{row['game_points']} points. "
        f"Moves: {', '.join(row['moves']) if row['moves'] else 'none'}. "
        f"Deals won: {score}",
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


def _moves_html(moves: list[str]) -> str:
    if not moves:
        return "none"
    return "<br>".join(escape(move) for move in moves)


def _record_deal(match, left, right, totals, moves):
    deal = match.deal
    eyes = {
        left: counting_eyes(deal, "computer"),
        right: counting_eyes(deal, "human"),
    }
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


def _blank():
    return {
        "deals_won": 0,
        "matches_won": 0,
        "game_points": 0,
        "eyes": 0,
        "bummerl": 0,
        "marriages": 0,
        "exchanges": 0,
        "closes": 0,
        "replaced": 0,
    }


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
