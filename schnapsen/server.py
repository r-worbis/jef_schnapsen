"""Local Schnapsen table.

Start the server with the TypeSafe API key in jef.api at the repository root:

    python -m schnapsen

The server binds to 127.0.0.1 on port 8765. The key is read from jef.api
and is never written to disk. Card drawings for review are at
http://127.0.0.1:8765/static/cards/preview.html
"""

from __future__ import annotations

import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from schnapsen.engine import Match, apply_action, new_match
from schnapsen.turn import close_match_clients, take_ai_turn
from schnapsen.view import human_view

ROOT = Path(__file__).resolve().parent
PAGE = (ROOT / "page.html").read_text(encoding="utf-8")
STATIC = (ROOT / "static").resolve()


class Table:
    """One in-memory match and the client used for the computer seat."""

    def __init__(self, match: Match, client: object | None = None) -> None:
        self.match = match
        self.client = client
        self.random_player = None
        self.llm_player = None
        self.lock = threading.Lock()


def submit_action(table: Table, action_id: str) -> tuple[bool, dict[str, object]]:
    with table.lock:
        applied = apply_action(table.match, action_id)
        if applied:
            take_ai_turn(table.match, table.client, table.random_player, table.llm_player)
        payload = human_view(table.match)
        payload["applied"] = applied
        return applied, payload


def advance_computer(table: Table) -> dict[str, object]:
    with table.lock:
        take_ai_turn(table.match, table.client, table.random_player, table.llm_player)
        return human_view(table.match)


_KINDS = {"human": {"human", "jev", "random", "llm"}, "computer": {"jev", "random", "llm"}}


def start_match(table: Table, human: object, computer: object) -> tuple[int, dict[str, object]]:
    with table.lock:
        if human not in _KINDS["human"] or computer not in _KINDS["computer"]:
            return 400, human_view(table.match)
        close_match_clients(table.match)
        match = new_match()
        match.players = {"human": human, "computer": computer}
        table.match = match
        return 200, human_view(match)


def read_state(table: Table) -> dict[str, object]:
    with table.lock:
        return human_view(table.match)


def make_server(table: Table, port: int = 0) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = unquote(self.path.split("?", 1)[0])
            if path == "/api/state":
                self._json(200, read_state(table))
                return
            if path in ("/", "/index.html"):
                body = PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path.startswith("/static/"):
                self._static(path)
                return
            self.send_error(404)

        def _static(self, path: str) -> None:
            relative = path[len("/static/") :]
            if not relative or ".." in Path(relative).parts:
                self.send_error(404)
                return
            target = (STATIC / relative).resolve()
            try:
                target.relative_to(STATIC)
            except ValueError:
                self.send_error(404)
                return
            if not target.is_file():
                self.send_error(404)
                return
            data = target.read_bytes()
            mime, _ = mimetypes.guess_type(target.name)
            if target.suffix == ".svg":
                mime = "image/svg+xml"
            self.send_response(200)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self) -> None:
            path = self.path.split("?", 1)[0]
            if path == "/api/computer":
                self._json(200, advance_computer(table))
                return
            if path == "/api/match":
                human, computer = _player_pair(self)
                status, payload = start_match(table, human, computer)
                self._json(status, payload)
                return
            if path == "/api/action":
                action_id = _action_id(self)
                applied, payload = submit_action(table, action_id)
                self._json(200 if applied else 400, payload)
                return
            self.send_error(404)

        def log_message(self, fmt: str, *args: object) -> None:
            return

        def _json(self, status: int, payload: dict[str, object]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server


def _body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    raw = handler.rfile.read(length) if length else b""
    try:
        data = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _action_id(handler: BaseHTTPRequestHandler) -> str:
    action_id = _body(handler).get("id", "")
    return action_id if isinstance(action_id, str) else ""


def _player_pair(handler: BaseHTTPRequestHandler) -> tuple[object, object]:
    data = _body(handler)
    return data.get("human"), data.get("computer")


def main() -> None:
    table = Table(new_match())
    server = make_server(table, 8765)
    print("Schnapsen table at http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    finally:
        close_match_clients(table.match)
