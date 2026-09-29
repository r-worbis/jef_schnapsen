"""Ask ChatGPT which legal action the seat to play should take. Does not apply it."""

import http.client
import json
import urllib.error
import urllib.request
from urllib.parse import urlparse
from weakref import WeakKeyDictionary

from schnapsen.cards import parse_card
from schnapsen.engine import Deal, Match, Seat, legal_action_ids, parse_action
from schnapsen.keyfile import read_chat_settings
from schnapsen.rules_text import RULES
from schnapsen.view import jev_parts

_INSTRUCTION = (
    "You play weiches Schnapsen. Choose exactly one legal action id. "
    "The id names the card to play, for example play:Herz-Ass."
)
SYSTEM = f"{RULES}\n\n{_INSTRUCTION}"
_CONN = "_chat_connection"


class _DealKey:
    """Identity key so a deal's transcript dies with that deal.

    Deal compares equal by its cards, so it cannot itself be a weak-key.
    """

    __slots__ = ("__weakref__",)


class LlmPlayer:
    def __init__(self, key: str | None = None, reply=None) -> None:
        self.key = key
        self.reply = reply
        self.raw: str | None = None
        self._pending: tuple[Deal, Seat, str] | None = None
        self._threads: WeakKeyDictionary = WeakKeyDictionary()

    def propose(self, match: Match) -> tuple[str | None, bool]:
        """Return the action id, and whether the call failed."""
        legal = legal_action_ids(match)
        if self.reply is not None:
            try:
                text = self.reply(match)
            except Exception:
                return None, True
            if not isinstance(text, str):
                return None, True
            return interpret_reply(text, legal), False
        deal = match.deal
        if deal is None:
            return None, True
        seat = deal.to_play
        user = jev_parts(match)[1]
        self._pending = (deal, seat, user)
        self.raw = None
        messages = [
            {"role": "system", "content": SYSTEM},
            *self._completed(deal, seat),
            {"role": "user", "content": user},
        ]
        url, model, file_key = read_chat_settings()
        key = file_key if self.key is None else self.key
        if not key.strip():
            return None, True
        body = json.dumps(
            {
                "model": model,
                "messages": messages,
                "response_format": _action_schema(legal),
                "prompt_cache_key": f"{id(deal)}:{seat}",
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            response = send(match, request)
            status = getattr(response, "status", 200)
            raw = response.read()
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, http.client.HTTPException):
            return None, True
        if status != 200:
            return None, True
        try:
            payload = json.loads(raw.decode("utf-8"))
            text = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError, UnicodeError):
            return None, True
        if not isinstance(text, str):
            return None, True
        self.raw = text
        return read_choice(text, legal), False

    def commit(self, match: Match, seat: Seat, assistant_text: str) -> None:
        """Append the request just sent and the play that was applied."""
        pending = self._pending
        deal = match.deal
        if pending is None or deal is None:
            return
        pending_deal, pending_seat, user = pending
        if pending_deal is not deal or pending_seat != seat:
            return
        thread = self._bucket(deal).setdefault(seat, [])
        thread.append({"role": "user", "content": user})
        thread.append({"role": "assistant", "content": assistant_text})
        self._pending = None

    def _completed(self, deal: Deal, seat: Seat) -> list[dict[str, str]]:
        return list(self._bucket(deal).get(seat, []))

    def _bucket(self, deal: Deal) -> dict[Seat, list[dict[str, str]]]:
        key = getattr(deal, "_llm_key", None)
        if key is None:
            key = _DealKey()
            setattr(deal, "_llm_key", key)
        bucket = self._threads.get(key)
        if bucket is None:
            bucket = {}
            self._threads[key] = bucket
        return bucket


def send(match: Match, request: urllib.request.Request):
    """Post one ChatGPT request on the match's connection."""
    parsed = urlparse(request.full_url)
    connection = _chat_connection(match, parsed.hostname or "", parsed.port)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    headers = {
        "Authorization": request.get_header("Authorization") or "",
        "Content-Type": request.get_header("Content-type") or "application/json",
    }
    connection.request(request.get_method(), path, body=request.data, headers=headers)
    response = connection.getresponse()
    return _Reply(getattr(response, "status", 200), response.read())


def close_chat_connection(match: Match) -> None:
    """Close the ChatGPT connection this match opened."""
    connection = getattr(match, _CONN, None)
    if connection is None:
        return
    delattr(match, _CONN)
    connection.close()


class _Reply:
    def __init__(self, status: int, raw: bytes) -> None:
        self.status = status
        self._raw = raw

    def read(self) -> bytes:
        return self._raw


def _chat_connection(match: Match, host: str, port: int | None):
    connection = getattr(match, _CONN, None)
    if connection is not None:
        return connection
    connection = http.client.HTTPSConnection(host, port) if port else http.client.HTTPSConnection(host)
    setattr(match, _CONN, connection)
    return connection


def _action_schema(legal: list[str]) -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "play",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"action": {"type": "string", "enum": legal}},
                "required": ["action"],
                "additionalProperties": False,
            },
        },
    }


def read_choice(text: str, legal: list[str]) -> str | None:
    try:
        payload = json.loads(text)
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        action = payload.get("action")
        if isinstance(action, str) and action in legal:
            return action
    return interpret_reply(text, legal)


def interpret_reply(text: str, legal: list[str]) -> str | None:
    line = next((part.strip() for part in text.splitlines() if part.strip()), "")
    if len(line) >= 2 and line[0] == line[-1] and line[0] in "\"'":
        line = line[1:-1].strip()
    if line.endswith("."):
        line = line[:-1].strip()
    if line in legal:
        return line
    card = parse_card(line)
    if card is None and " " in line:
        suit, _, rank = line.partition(" ")
        card = parse_card(f"{suit}-{rank}")
    if card is None:
        return None
    matches = []
    for action_id in legal:
        plan = parse_action(action_id)
        if plan is not None and plan.card == card:
            matches.append(action_id)
    if len(matches) == 1:
        return matches[0]
    return None
