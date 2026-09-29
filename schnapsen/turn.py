"""Ask the player bound to the seat to play, and apply the proposal only through the engine."""

from schnapsen.engine import Match, apply_action, legal_action_ids
from schnapsen.jev_player import ask, begin_request, close_jev_client, live_client
from schnapsen.keyfile import read_api_key, read_chat_api_key
from schnapsen.llm_player import LlmPlayer, close_chat_connection
from schnapsen.random_player import RandomPlayer


def close_match_clients(match: Match) -> None:
    """Close the Jev client and the ChatGPT connection this match opened."""
    close_jev_client(match)
    close_chat_connection(match)


def take_ai_turn(
    match: Match,
    client: object | None = None,
    random_player: RandomPlayer | None = None,
    llm_player: LlmPlayer | None = None,
    instructions: str | None = None,
) -> None:
    """Play one turn when the seat to play is Jev, the random player, or the LLM."""
    deal = match.deal
    if deal is None or deal.phase != "play" or match.match_winner is not None:
        return
    kind = match.players.get(deal.to_play)
    if kind not in ("jev", "random", "llm"):
        return
    legal = legal_action_ids(match)
    if not legal:
        return
    fallback = sorted(legal)[0]
    if kind == "jev":
        _jev_turn(match, client, legal, fallback, instructions)
        return
    if kind == "random":
        _random_turn(match, random_player or RandomPlayer(), fallback)
        return
    _llm_turn(match, llm_player or LlmPlayer(), fallback)


def _jev_turn(
    match: Match,
    client: object | None,
    legal: list[str],
    fallback: str,
    instructions: str | None = None,
) -> None:
    key = read_api_key()
    if not key:
        match.notice = "missing-key"
        match.choice_replaced = False
        return
    match.notice = None
    live = live_client(match, client)
    if live is None:
        match.notice = "missing-key"
        match.choice_replaced = False
        return
    _jev_with_client(match, live, legal, fallback, instructions)


def _jev_with_client(
    match: Match,
    client: object,
    legal: list[str],
    fallback: str,
    instructions: str | None = None,
) -> None:
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


def _random_turn(match: Match, player: RandomPlayer, fallback: str) -> None:
    match.notice = None
    if _accept(match, player.propose(match)):
        return
    if _accept(match, player.propose(match)):
        return
    _fallback(match, fallback)


def _llm_turn(match: Match, player: LlmPlayer, fallback: str) -> None:
    deal = match.deal
    if deal is None:
        return
    seat = deal.to_play
    live = player.reply is None
    if live:
        key = read_chat_api_key() if player.key is None else player.key
        if not key.strip():
            match.notice = "missing-chat-key"
            match.choice_replaced = False
            return
    match.notice = None
    choice, failed = player.propose(match)
    if failed:
        _fallback(match, fallback)
        _commit_live(player, match, seat, fallback, live)
        return
    if choice is not None and _accept(match, choice):
        _commit_live(player, match, seat, player.raw or choice, live)
        return
    choice, failed = player.propose(match)
    if failed or choice is None or not _accept(match, choice):
        _fallback(match, fallback)
        _commit_live(player, match, seat, fallback, live)
        return
    _commit_live(player, match, seat, player.raw or choice, live)


def _commit_live(player: LlmPlayer, match: Match, seat: str, text: str, live: bool) -> None:
    if live:
        player.commit(match, seat, text)


def _accept(match: Match, action_id: str) -> bool:
    if not apply_action(match, action_id):
        return False
    match.choice_replaced = False
    return True


def _fallback(match: Match, action_id: str) -> None:
    apply_action(match, action_id)
    match.choice_replaced = True
