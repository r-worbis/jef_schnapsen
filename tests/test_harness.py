"""Round-robin AI matches write an HTML report without calling the network."""

import json
import re
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from schnapsen.cards import Card, full_pack
from schnapsen.engine import apply_action, legal_action_ids, match_with_deal
from schnapsen.harness import DEFAULT_REPORT, HarnessError, _blank, _special_moves, parse_args, play_rounds
from schnapsen.harness import main, render_html
from schnapsen.keyfile import CHAT_KEY_PATH, KEY_PATH
from schnapsen.llm_player import LlmPlayer
from schnapsen.random_player import RandomPlayer


class _RejectLive:
    def __init__(self, **kwargs):
        raise AssertionError("opened a TypeSafe client")


class ChoosingClient:
    def __init__(self):
        self.calls = []

    def system_one(self, state, questions):
        self.calls.append(state)
        action_id = sorted(questions["play"].criteria)[0]
        choice = type("Choice", (), {"choice": action_id})()
        return type("Response", (), {"choices": {"play": choice}})()


def scripted_llm():
    def reply(match):
        return sorted(legal_action_ids(match))[0]

    return LlmPlayer(key="present", reply=reply)


class HarnessTests(unittest.TestCase):
    def test_defaults_are_ten_rounds_and_the_report_path(self):
        args = parse_args([])
        self.assertEqual(args.rounds, 10)
        self.assertEqual(Path(args.report), DEFAULT_REPORT)
        self.assertTrue(str(DEFAULT_REPORT).endswith("reports/ai-rounds.html"))

    def test_one_round_of_each_pairing_stays_offline(self):
        client = ChoosingClient()
        called = []

        def opener(request, timeout=None):
            called.append(request)
            raise urllib.error.URLError("offline")

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "rounds.html"
            prior = {
                "played_at": "2000-01-01T00:00:00+00:00",
                "model": "gpt-6-sol",
                "rounds_per_pairing": 1,
                "players": {
                    "jev": {**_blank(), "deals_won": 4},
                    "random": _blank(),
                    "llm": _blank(),
                },
                "pairings": [],
            }
            (Path(directory) / "rounds-20000101T000000.json").write_text(
                json.dumps(prior), encoding="utf-8"
            )
            console = StringIO()
            with (
                patch("schnapsen.llm_player.send", opener),
                patch("typesafe_sdk.TypeSafeClient", _RejectLive),
                patch("schnapsen.turn.read_api_key", return_value="present"),
                patch("schnapsen.turn.read_chat_api_key", return_value="present"),
                patch("schnapsen.harness._now", return_value=datetime.fromisoformat("2026-09-29T15:15:31+02:00")),
                redirect_stdout(console),
            ):
                play_rounds(
                    1,
                    report,
                    client=client,
                    random_player=RandomPlayer(lambda hand: hand[0]),
                    llm_player=scripted_llm(),
                )
            text = report.read_text(encoding="utf-8")
            saved = json.loads((Path(directory) / "rounds-20260929T151531.json").read_text(encoding="utf-8"))
            output = console.getvalue()
        self.assertEqual(saved["rounds_per_pairing"], 1)
        self.assertEqual(len(saved["pairings"]), 3)
        self.assertEqual(_deals(text, "overall", "jev"), _deals(text, "last", "jev") + 4)
        self.assertIn("Last run", text)
        self.assertIn("Overall", text)
        self.assertIn("Pairings", text)
        self.assertIn("Jev vs Random", output)
        self.assertIn("wins", output)
        self.assertIn("Deals won:", output)
        self.assertEqual(called, [])
        self.assertIn("gpt-6-sol", text)
        self.assertIn("Rounds per pairing: 1.", text)
        self.assertNotIn("<script", text)
        self.assertNotIn("http", text)
        for title in ("Jev vs Random", "Jev vs LLM", "Random vs LLM"):
            self.assertIn(title, text)
        for title in ("Random vs Jev", "LLM vs Jev", "LLM vs Random"):
            self.assertNotIn(title, text)
        self.assertEqual(text.count('class="round"'), 3)
        for label in (
            "Deals won",
            "Matches won",
            "Game points",
            "Counting eyes",
            "Bummerl charges",
            "Marriages",
            "Trump exchanges",
            "Talon closes",
            "Special moves",
            "Replaced turns",
        ):
            self.assertIn(label, text)
        self._assert_keys_absent(text)

    def test_overall_adds_earlier_runs_and_pairing_totals(self):
        earlier = {
            "played_at": "2026-09-29T10:00:00+02:00",
            "model": "gpt-6-sol",
            "rounds_per_pairing": 1,
            "players": {
                "jev": {**_blank(), "deals_won": 1, "game_points": 2, "eyes": 70},
                "random": {**_blank(), "eyes": 29},
                "llm": _blank(),
            },
            "pairings": [
                {
                    "left": "jev",
                    "right": "random",
                    "rounds": [
                        {"winner": "jev", "eyes": {"jev": 70, "random": 29}, "game_points": 2, "moves": []}
                    ],
                }
            ],
        }
        last = {
            "played_at": "2026-09-29T15:15:31+02:00",
            "model": "gpt-6-sol",
            "rounds_per_pairing": 1,
            "players": {
                "jev": {**_blank(), "deals_won": 1, "game_points": 3, "eyes": 80},
                "random": _blank(),
                "llm": {**_blank(), "eyes": 10},
            },
            "pairings": [
                {
                    "left": "jev",
                    "right": "llm",
                    "rounds": [
                        {"winner": "jev", "eyes": {"jev": 80, "llm": 10}, "game_points": 3, "moves": []}
                    ],
                }
            ],
        }
        text = render_html(last, [earlier, last])
        self.assertEqual(_deals(text, "last", "jev"), 1)
        self.assertEqual(_deals(text, "overall", "jev"), 2)
        self.assertEqual(_deals(text, "overall", "random"), 0)
        last_section = text.split('id="overall"', 1)[0]
        overall = text.split('id="overall"', 1)[1]
        self.assertIn('data-pairing="jev-llm"', last_section)
        self.assertNotIn('data-pairing="jev-random"', last_section)
        self.assertIn("<td>Jev</td><td>Random</td><td>1</td><td>0</td><td>2</td><td>0</td><td>70</td><td>29</td>", overall)
        self.assertIn("<td>Jev</td><td>LLM</td><td>1</td><td>0</td><td>3</td><td>0</td><td>80</td><td>10</td>", overall)
        self.assertIn("Deals won A", overall)
        self.assertIn("Counting eyes B", overall)
        self.assertIn('data-pairing="jev-random"', overall)
        self.assertIn('data-pairing="jev-llm"', overall)
        self.assertEqual(text.count('class="round"'), 1)

    def test_a_marriage_exchange_and_close_are_recorded(self):
        match = match_with_deal("computer", full_pack())
        deal = match.deal
        deal.hands = {
            "computer": [Card("Herz", "König"), Card("Herz", "Dame"), Card("Herz", "Bube")],
            "human": [Card("Pik", "Ass")],
        }
        deal.talon = [Card("Kreuz", "Ass"), Card("Kreuz", "Zehner"), Card("Karo", "Ass")]
        deal.trump_card = Card("Herz", "Ass")
        deal.trump_suit = "Herz"
        deal.leader = "computer"
        deal.to_play = "computer"
        deal.current_trick = []
        match.players = {"computer": "jev", "human": "random"}
        self.assertTrue(apply_action(match, "exchange-close-marry:Herz:Herz-König"))
        totals = {kind: _blank() for kind in ("jev", "random", "llm")}
        notes = _special_moves(match, totals)
        self.assertEqual(totals["jev"]["marriages"], 1)
        self.assertEqual(totals["jev"]["exchanges"], 1)
        self.assertEqual(totals["jev"]["closes"], 1)
        text = " ".join(notes)
        self.assertIn("Jev married in Herz (40)", text)
        self.assertIn("Jev exchanged the trump jack for Herz Ass", text)
        self.assertIn("Jev closed the talon", text)

    def test_a_missing_chat_key_writes_no_report(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "rounds.html"
            with (
                patch("schnapsen.harness.read_api_key", return_value="present"),
                patch("schnapsen.harness.read_chat_api_key", return_value=""),
            ):
                code = main(["--rounds", "1", "--report", str(report)])
            self.assertEqual(code, 1)
            self.assertFalse(report.exists())

    def test_a_missing_jev_key_writes_no_report(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "rounds.html"
            with (
                patch("schnapsen.harness.read_api_key", return_value=""),
                patch("schnapsen.harness.read_chat_api_key", return_value="present"),
            ):
                code = main(["--rounds", "1", "--report", str(report)])
            self.assertEqual(code, 1)
            self.assertFalse(report.exists())

    def test_each_match_opens_one_client_per_player_and_closes_it(self):
        events = []

        class FakeLive:
            def __init__(self, **kwargs):
                events.append("jev-open")

            def __enter__(self):
                return self

            def __exit__(self, *args):
                events.append("jev-close")
                return False

            def system_one(self, state, questions):
                action = sorted(questions["play"].criteria)[0]
                return SimpleNamespace(choices={"play": SimpleNamespace(choice=action)})

        class FakeConn:
            def __init__(self, host, port=None, **kwargs):
                events.append("chat-open")

            def request(self, method, path, body=None, headers=None):
                self.body = json.loads(body)

            def getresponse(self):
                action = self.body["response_format"]["json_schema"]["schema"]["properties"]["action"]["enum"][0]
                content = json.dumps({"action": action})
                raw = json.dumps({"choices": [{"message": {"content": content}}]}).encode()
                return SimpleNamespace(status=200, read=lambda: raw)

            def close(self):
                events.append("chat-close")

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "rounds.html"
            with (
                patch("typesafe_sdk.TypeSafeClient", FakeLive),
                patch("schnapsen.llm_player.http.client.HTTPSConnection", FakeConn),
                patch("schnapsen.turn.read_api_key", return_value="present"),
                patch("schnapsen.jev_player.read_api_key", return_value="present"),
                patch("schnapsen.turn.read_chat_api_key", return_value="present"),
                redirect_stdout(StringIO()),
            ):
                play_rounds(1, report, random_player=RandomPlayer(lambda hand: hand[0]), llm_player=LlmPlayer(key="present"))
        self.assertEqual(self._spans(events, "jev-open", "jev-close"), 2)
        self.assertEqual(self._spans(events, "chat-open", "chat-close"), 2)

        failed = []

        class Opening:
            def __init__(self, **kwargs):
                failed.append("open")

            def __enter__(self):
                return self

            def __exit__(self, *args):
                failed.append("close")
                return False

        def explode(match, client, random_player, llm_player):
            from schnapsen.jev_player import live_client

            live_client(match, None)
            raise HarnessError("turn did not play")

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "rounds.html"
            with (
                patch("typesafe_sdk.TypeSafeClient", Opening),
                patch("schnapsen.harness.take_ai_turn", explode),
                patch("schnapsen.jev_player.read_api_key", return_value="present"),
                redirect_stdout(StringIO()),
            ):
                with self.assertRaises(HarnessError):
                    play_rounds(1, report)
        self.assertEqual(failed, ["open", "close"])

    def _spans(self, events, opened, closed) -> int:
        depth = 0
        count = 0
        for event in events:
            if event == opened:
                self.assertEqual(depth, 0)
                depth = 1
                count += 1
            elif event == closed:
                self.assertEqual(depth, 1)
                depth = 0
        self.assertEqual(depth, 0)
        return count

    def _assert_keys_absent(self, text: str) -> None:
        for path in (KEY_PATH, CHAT_KEY_PATH):
            try:
                secret = path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if secret and secret in text:
                self.fail("report contains a key file")


def _deals(html: str, section: str, player: str) -> int:
    chunk = html.split(f'id="{section}"', 1)[1].split("<section", 1)[0]
    row = chunk.split(f'data-player="{player}"', 1)[1].split("</tr>", 1)[0]
    return int(re.findall(r"<td>(\d+)</td>", row)[0])
