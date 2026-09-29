"""Play the same logged deals with two Jev prompts against the random player."""

import argparse
import json
import random
from html import escape
from pathlib import Path

from schnapsen.cards import parse_card
from schnapsen.engine import counting_eyes, match_with_deal, new_match, other
from schnapsen.harness import HarnessError
from schnapsen.jev_player import INSTRUCTION
from schnapsen.keyfile import read_api_key, read_chat_api_key
from schnapsen.llm_player import LlmPlayer
from schnapsen.random_player import RandomPlayer
from schnapsen.turn import close_match_clients, take_ai_turn

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = ROOT / "reports" / "jev-random-deals.json"
DEFAULT_REPORT = ROOT / "reports" / "jev-random-prompt.html"
SWAPPED_LOG = ROOT / "reports" / "jev-random-swapped.json"
SWAPPED_REPORT = ROOT / "reports" / "jev-random-swapped.html"
LLM_LOG = ROOT / "reports" / "jev-llm-deals.json"
LLM_REPORT = ROOT / "reports" / "jev-llm-prompt.html"
LLM_SWAPPED_LOG = ROOT / "reports" / "jev-llm-swapped.json"
LLM_SWAPPED_REPORT = ROOT / "reports" / "jev-llm-swapped.html"
TURN_CAP = 80
ORIGINAL_SEATS = {"computer": "jev", "human": "random"}
SWAPPED_SEATS = {"computer": "random", "human": "jev"}
NAMES = {"jev": "Jev", "random": "Random", "llm": "LLM"}
OLD_INSTRUCTION = (
    "Which legal action gives you the best chance to reach 66 eyes before the opponent?"
)
RUNS = ("new", "old")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay logged deals with two Jev prompts.")
    parser.add_argument("--deals", type=int, default=50)
    parser.add_argument("--log", default=str(DEFAULT_LOG))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--from-log", default="")
    parser.add_argument("--swap", action="store_true")
    parser.add_argument("--opponent", choices=("random", "llm"), default="random")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not read_api_key().strip():
        return 1
    if args.opponent == "llm" and not read_chat_api_key().strip():
        return 1
    try:
        if args.opponent == "llm":
            source = Path(args.from_log) if args.from_log else DEFAULT_LOG
            replay_opponent(source, "llm")
            return 0
        if args.from_log:
            log = Path(args.log)
            report = Path(args.report)
            if args.swap and log == DEFAULT_LOG:
                log = SWAPPED_LOG
            if args.swap and report == DEFAULT_REPORT:
                report = SWAPPED_REPORT
            seats = SWAPPED_SEATS if args.swap else ORIGINAL_SEATS
            replay_logged(Path(args.from_log), log, report, players=seats)
        else:
            compare(args.deals, Path(args.log), Path(args.report))
    except HarnessError:
        return 1
    return 0


def compare(count: int, log: Path, report: Path, *, client: object | None = None, rng=None) -> dict:
    if client is not None:
        return _compare(count, log, report, client, rng)
    key = read_api_key()
    from typesafe_sdk import TypeSafeClient

    with TypeSafeClient(api_key=key) as held:
        return _compare(count, log, report, held, rng)


def _compare(count: int, log: Path, report: Path, client: object | None, rng) -> dict:
    deals = sample_deals(count, rng)
    document = {
        "deals": deals,
        "runs": {
            "new": {"instruction": INSTRUCTION, "deals": []},
            "old": {"instruction": OLD_INSTRUCTION, "deals": []},
        },
    }
    log.parent.mkdir(parents=True, exist_ok=True)
    _write(log, document)
    prompts = {"new": INSTRUCTION, "old": OLD_INSTRUCTION}
    for label in RUNS:
        print(f"{label}: {prompts[label]}", flush=True)
        for spec in deals:
            row = play_deal(spec, prompts[label], client)
            document["runs"][label]["deals"].append(row)
            _write(log, document)
            _print_deal(label, row, document["runs"][label]["deals"])
    report.write_text(render_html(document), encoding="utf-8")
    return document


def sample_deals(count: int, rng: random.Random | None = None) -> list[dict]:
    source = rng or random.Random()
    sampled = []
    for index in range(1, count + 1):
        match = new_match(source)
        sampled.append(
            {
                "index": index,
                "dealer": match.dealer,
                "random_seed": index,
                "pack": pack_tokens(match),
            }
        )
    return sampled


def pack_tokens(match) -> list[str]:
    """Return the 20-card pack build_deal consumed, so the deal can be rebuilt."""
    deal = match.deal
    dealer = match.dealer
    forehand = other(dealer)
    pack = [""] * 20
    fore = deal.hands[forehand]
    back = deal.hands[dealer]
    pack[0], pack[1], pack[2], pack[7], pack[8] = (card.token for card in fore)
    pack[3], pack[4], pack[5], pack[9], pack[10] = (card.token for card in back)
    pack[6] = deal.trump_card.token
    for offset, card in enumerate(deal.talon):
        pack[11 + offset] = card.token
    return pack


def seats_for(opponent: str, swapped: bool) -> dict:
    if swapped:
        return {"computer": opponent, "human": "jev"}
    return {"computer": "jev", "human": opponent}


def replay_opponent(
    source: Path,
    opponent: str,
    *,
    client: object | None = None,
    llm_player: LlmPlayer | None = None,
) -> tuple[dict, dict]:
    """Play the logged deals, then the same deals with the seats swapped."""
    if opponent == "llm":
        paths = ((LLM_LOG, LLM_REPORT), (LLM_SWAPPED_LOG, LLM_SWAPPED_REPORT))
    else:
        paths = ((DEFAULT_LOG, DEFAULT_REPORT), (SWAPPED_LOG, SWAPPED_REPORT))
    if client is not None:
        return _replay_pair(source, opponent, paths, client, llm_player)
    key = read_api_key()
    from typesafe_sdk import TypeSafeClient

    with TypeSafeClient(api_key=key) as held:
        player = llm_player if opponent == "llm" else None
        if opponent == "llm" and player is None:
            player = LlmPlayer()
        return _replay_pair(source, opponent, paths, held, player)


def _replay_pair(source, opponent, paths, client, llm_player) -> tuple[dict, dict]:
    first = replay_logged(
        source,
        paths[0][0],
        paths[0][1],
        players=seats_for(opponent, False),
        client=client,
        llm_player=llm_player,
    )
    second = replay_logged(
        source,
        paths[1][0],
        paths[1][1],
        players=seats_for(opponent, True),
        client=client,
        llm_player=llm_player,
    )
    return first, second


def replay_logged(
    source: Path,
    log: Path,
    report: Path,
    *,
    players: dict | None = None,
    client: object | None = None,
    llm_player: LlmPlayer | None = None,
) -> dict:
    """Play the deals already stored in source. players binds each seat to a kind."""
    loaded = json.loads(source.read_text(encoding="utf-8"))
    seats = players or ORIGINAL_SEATS
    document = {
        "deals": loaded["deals"],
        "seats": seats,
        "runs": {
            label: {"instruction": loaded["runs"][label]["instruction"], "deals": []}
            for label in RUNS
        },
    }
    if client is not None:
        return _play_document(document, log, report, client, llm_player)
    key = read_api_key()
    from typesafe_sdk import TypeSafeClient

    with TypeSafeClient(api_key=key) as held:
        return _play_document(document, log, report, held, llm_player)


def _play_document(
    document: dict,
    log: Path,
    report: Path,
    client: object,
    llm_player: LlmPlayer | None = None,
) -> dict:
    log.parent.mkdir(parents=True, exist_ok=True)
    _write(log, document)
    seats = document["seats"]
    for label in RUNS:
        instruction = document["runs"][label]["instruction"]
        print(f"{label}: {instruction}", flush=True)
        print(f"seats: computer={seats['computer']}, human={seats['human']}", flush=True)
        for spec in document["deals"]:
            row = play_deal(spec, instruction, client, players=seats, llm_player=llm_player)
            document["runs"][label]["deals"].append(row)
            _write(log, document)
            _print_deal(label, row, document["runs"][label]["deals"])
    report.write_text(render_html(document), encoding="utf-8")
    return document


def play_deal(
    spec: dict,
    instructions: str,
    client: object | None,
    players: dict | None = None,
    llm_player: LlmPlayer | None = None,
) -> dict:
    seats = players or ORIGINAL_SEATS
    pack = []
    for token in spec["pack"]:
        card = parse_card(token)
        if card is None:
            raise HarnessError("deal pack is not reproducible")
        pack.append(card)
    match = match_with_deal(spec["dealer"], pack)
    match.players = dict(seats)
    player = RandomPlayer(random.Random(spec["random_seed"]).choice)
    turns = 0
    try:
        while True:
            deal = match.deal
            if deal is None:
                raise HarnessError("no deal")
            if deal.phase == "ended":
                break
            if deal.phase != "play":
                raise HarnessError("unexpected phase")
            if turns >= TURN_CAP:
                raise HarnessError("deal exceeded 80 turns")
            before = _fingerprint(match)
            take_ai_turn(
                match,
                client,
                random_player=player,
                llm_player=llm_player,
                instructions=instructions,
            )
            turns += 1
            if match.notice in ("missing-key", "missing-chat-key") or _fingerprint(match) == before:
                raise HarnessError("turn did not play")
        deal = match.deal
        seat_of = {kind: seat for seat, kind in seats.items()}
        return {
            "index": spec["index"],
            "winner": match.players.get(deal.winner, ""),
            "winner_seat": deal.winner,
            "game_points": deal.game_points or 0,
            "eyes": {kind: counting_eyes(deal, seat) for kind, seat in seat_of.items()},
        }
    finally:
        close_match_clients(match)


def opening_influence(
    deals: list[dict],
    original_rows: list[dict],
    swapped_rows: list[dict],
    other: str = "random",
) -> dict:
    """Compare Jev-on-the-left with Jev-on-the-right for the same openings.

    A deal is counted for the cards when the same seat wins both ways.
    It is counted for the player when the same player wins from both seats.
    """
    cards = player = jev_both = other_both = 0
    dealer_cards = forehand_cards = 0
    jev_points = other_points = computer_points = human_points = 0
    jev_eyes = other_eyes = computer_eyes = human_eyes = 0
    for spec, left, right in zip(deals, original_rows, swapped_rows):
        seat_left = "computer" if left["winner"] == "jev" else "human"
        seat_right = "human" if right["winner"] == "jev" else "computer"
        if seat_left == seat_right:
            cards += 1
            if seat_left == spec["dealer"]:
                dealer_cards += 1
            else:
                forehand_cards += 1
        else:
            player += 1
            if left["winner"] == "jev":
                jev_both += 1
            else:
                other_both += 1
        jev_points += _points(left, "jev") + _points(right, "jev")
        other_points += _points(left, other) + _points(right, other)
        computer_points += _points(left, "jev") + _points(right, other)
        human_points += _points(left, other) + _points(right, "jev")
        jev_eyes += left["eyes"]["jev"] + right["eyes"]["jev"]
        other_eyes += left["eyes"][other] + right["eyes"][other]
        computer_eyes += left["eyes"]["jev"] + right["eyes"][other]
        human_eyes += left["eyes"][other] + right["eyes"]["jev"]
    return {
        "deals": cards + player,
        "cards": cards,
        "player": player,
        "jev_both": jev_both,
        "other": other,
        "other_both": other_both,
        f"{other}_both": other_both,
        "dealer_cards": dealer_cards,
        "forehand_cards": forehand_cards,
        "jev_points": jev_points,
        "other_points": other_points,
        f"{other}_points": other_points,
        "computer_points": computer_points,
        "human_points": human_points,
        "jev_eyes": jev_eyes,
        "other_eyes": other_eyes,
        f"{other}_eyes": other_eyes,
        "computer_eyes": computer_eyes,
        "human_eyes": human_eyes,
    }


def _points(row: dict, kind: str) -> int:
    return row["game_points"] if row["winner"] == kind else 0


def render_html(document: dict) -> str:
    rows = []
    for spec in document["deals"]:
        cells = [f"<td>{spec['index']}</td>", f"<td>{escape(spec['dealer'])}</td>"]
        for label in RUNS:
            played = _row(document, label, spec["index"])
            if played is None:
                cells.append("<td></td><td></td><td></td>")
                continue
            opponent = _opponent(document)
            cells.append(
                f"<td>{escape(played['winner'])}</td>"
                f"<td>{played['game_points']}</td>"
                f"<td>{played['eyes']['jev']} / {played['eyes'][opponent]}</td>"
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>Jev prompt on the same deals</title><style>"
        "body{font-family:sans-serif;margin:24px}"
        "table{border-collapse:collapse;margin:0 0 24px}"
        "td,th{border:1px solid #ccc;padding:4px 8px;text-align:left}"
        "</style></head><body>"
        "<h1>Jev prompt on the same deals</h1>"
        + "".join(_summary(document, label) for label in RUNS)
        + "<h2>Deals</h2><table>"
        "<tr><th>Deal</th><th>Dealer</th>"
        f"<th>New winner</th><th>New points</th><th>New eyes Jev / {escape(NAMES[_opponent(document)])}</th>"
        f"<th>Old winner</th><th>Old points</th><th>Old eyes Jev / {escape(NAMES[_opponent(document)])}</th></tr>"
        + "".join(rows)
        + "</table></body></html>"
    )


def _summary(document: dict, label: str) -> str:
    opponent = _opponent(document)
    played = document["runs"][label]["deals"]
    deals = sum(1 for row in played if row["winner"] == "jev")
    points = sum(row["game_points"] for row in played if row["winner"] == "jev")
    other_deals = sum(1 for row in played if row["winner"] == opponent)
    other_points = sum(row["game_points"] for row in played if row["winner"] == opponent)
    return (
        f"<h2>{escape(label)}</h2>"
        f"<p>{escape(document['runs'][label]['instruction'])}</p>"
        "<table><tr><th>Player</th><th>Deals won</th><th>Game points</th></tr>"
        f"<tr><td>Jev</td><td>{deals}</td><td>{points}</td></tr>"
        f"<tr><td>{escape(NAMES[opponent])}</td><td>{other_deals}</td><td>{other_points}</td></tr>"
        "</table>"
    )


def _opponent(document: dict) -> str:
    seats = document.get("seats") or ORIGINAL_SEATS
    for kind in seats.values():
        if kind != "jev":
            return kind
    return "random"


def _row(document: dict, label: str, index: int) -> dict | None:
    for row in document["runs"][label]["deals"]:
        if row["index"] == index:
            return row
    return None


def _print_deal(label: str, row: dict, played: list[dict]) -> None:
    opponent = next(kind for kind in row["eyes"] if kind != "jev")
    jev = sum(1 for item in played if item["winner"] == "jev")
    other_wins = sum(1 for item in played if item["winner"] == opponent)
    print(
        f"{label}  deal {row['index']}: {row['winner']} wins, "
        f"Jev {row['eyes']['jev']} eyes, {NAMES[opponent]} {row['eyes'][opponent]} eyes, "
        f"{row['game_points']} points. Deals won: Jev {jev}, {NAMES[opponent]} {other_wins}",
        flush=True,
    )


def _write(path: Path, document: dict) -> None:
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


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
    )


if __name__ == "__main__":
    raise SystemExit(main())
