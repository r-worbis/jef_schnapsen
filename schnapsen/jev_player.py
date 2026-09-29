"""Ask Jev which legal action the seat to play should take. Does not apply it."""

from typesafe_sdk import Choice

from schnapsen.engine import JevExchange, Match, action_label
from schnapsen.keyfile import read_api_key
from schnapsen.view import jev_parts, jev_state

_HELD = "_jev_client"


INSTRUCTION = (
    "Select the legal action that gives you the best chance "
    "to get to 66 eyes before the opponent."
)


class _HeldClient:
    """The context manager that was entered, and the object its enter returned."""

    __slots__ = ("owner", "client")

    def __init__(self, owner: object, client: object) -> None:
        self.owner = owner
        self.client = client


def live_client(match: Match, supplied: object | None) -> object | None:
    """Return the match's Jev client, opening it on the first request.

    A supplied client is used as given and is not stored. A missing key
    opens nothing.
    """
    if supplied is not None:
        return supplied
    held = getattr(match, _HELD, None)
    if isinstance(held, _HeldClient):
        return held.client
    key = read_api_key()
    if not key.strip():
        return None
    from typesafe_sdk import TypeSafeClient

    owner = TypeSafeClient(api_key=key)
    entered = owner.__enter__()
    setattr(match, _HELD, _HeldClient(owner, entered))
    return entered


def close_jev_client(match: Match) -> None:
    """Exit the client this match opened. A supplied client is not stored."""
    held = getattr(match, _HELD, None)
    if not isinstance(held, _HeldClient):
        return
    delattr(match, _HELD)
    held.owner.__exit__(None, None, None)


def begin_request(match: Match) -> None:
    rules, cards = jev_parts(match)
    match.jev_exchange = JevExchange(rules=rules, cards=cards)


def ask(
    match: Match,
    client: object,
    legal: list[str],
    instructions: str | None = None,
) -> tuple[str | None, bool]:
    system_one = getattr(client, "system_one")
    try:
        response = system_one(
            state=jev_state(match),
            questions={
                "play": Choice(
                    instructions=INSTRUCTION if instructions is None else instructions,
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
