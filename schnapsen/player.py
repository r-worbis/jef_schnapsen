"""Ask Jev which legal action the computer seat should take."""

from typesafe_sdk import Choice

from schnapsen.engine import JevExchange, Match, action_label, apply_action, legal_action_ids
from schnapsen.keyfile import read_api_key
from schnapsen.view import jev_parts, jev_state


def computer_should_move(match: Match) -> bool:
    deal = match.deal
    return (
        deal is not None
        and deal.phase != "ended"
        and deal.to_play == "computer"
        and match.match_winner is None
    )


def perform_computer_turn(match: Match, client: object | None = None) -> None:
    """Apply one computer decision, or stop when the API key is missing.

    `client` is a TypeSafe-like object with `system_one`. When it is omitted and
    a key is present, the live `TypeSafeClient` is used.
    """
    if not computer_should_move(match):
        return
    key = read_api_key()
    if not key:
        match.notice = "missing-key"
        match.choice_replaced = False
        return
    match.notice = None
    if client is None:
        from typesafe_sdk import TypeSafeClient

        with TypeSafeClient(api_key=key) as live:
            _decide(match, live)
        return
    _decide(match, client)


def _decide(match: Match, client: object) -> None:
    legal = legal_action_ids(match)
    if not legal:
        return
    rules, cards = jev_parts(match)
    match.jev_exchange = JevExchange(rules=rules, cards=cards)
    fallback = sorted(legal)[0]
    choice, failed = _ask(match, client, legal)
    if failed or choice not in legal:
        if failed:
            _apply_fallback(match, fallback)
            return
        choice, failed = _ask(match, client, legal)
        if failed or choice not in legal:
            _apply_fallback(match, fallback)
            return
    match.choice_replaced = False
    apply_action(match, choice)


def _ask(match: Match, client: object, legal: list[str]) -> tuple[str | None, bool]:
    system_one = getattr(client, "system_one")
    try:
        response = system_one(
            state=jev_state(match),
            questions={
                "play": Choice(
                    instructions="Choose the legal action to play now.",
                    criteria={action_id: action_label(action_id) for action_id in legal},
                )
            },
        )
    except Exception:
        _exchange(match).failed = True
        return None, True
    try:
        choice = response.choices["play"].choice
    except Exception:
        _exchange(match).failed = True
        return None, True
    _exchange(match).answers.append(choice)
    return choice, False


def _exchange(match: Match) -> JevExchange:
    exchange = match.jev_exchange
    assert exchange is not None
    return exchange


def _apply_fallback(match: Match, action_id: str) -> None:
    apply_action(match, action_id)
    match.choice_replaced = True
