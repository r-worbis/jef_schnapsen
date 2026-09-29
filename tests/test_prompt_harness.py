"""Jev wording variants play each other without calling the network."""

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from schnapsen.jev_player import INSTRUCTION
from schnapsen.prompt_harness import DEFAULT_REPORT, PAIRINGS, VARIANTS, main, play_prompts


class _RejectLive:
    def __init__(self, **kwargs):
        raise AssertionError("opened a TypeSafe client")


class RecordingClient:
    def __init__(self):
        self.instructions = []

    def system_one(self, state, questions):
        question = questions["play"]
        self.instructions.append(question.instructions)
        action_id = sorted(question.criteria)[0]
        choice = type("Choice", (), {"choice": action_id})()
        return type("Response", (), {"choices": {"play": choice}})()


class PromptHarnessTests(unittest.TestCase):
    def test_the_wording_set_crosses_select_get_to_and_counting_eyes(self):
        by_id = {variant.id: variant.instructions for variant in VARIANTS}
        self.assertEqual(len(VARIANTS), 5)
        self.assertEqual(len(PAIRINGS), 10)
        self.assertEqual(
            by_id["which-reach"],
            "Which legal action gives you the best chance to reach 66 eyes before the opponent?",
        )
        self.assertNotEqual(by_id["which-reach"], INSTRUCTION)
        self.assertEqual(
            by_id["select-reach"],
            "Select the legal action that gives you the best chance to reach 66 eyes before the opponent.",
        )
        self.assertEqual(
            by_id["which-get"],
            "Which legal action gives you the best chance to get to 66 eyes before the opponent?",
        )
        self.assertEqual(
            by_id["select-get"],
            "Select the legal action that gives you the best chance to get to 66 eyes before the opponent.",
        )
        self.assertIn("counting eyes", by_id["select-count"])
        self.assertTrue(by_id["select-count"].startswith("Select "))

    def test_defaults_are_fifteen_rounds_and_the_wording_report(self):
        from schnapsen.prompt_harness import parse_args

        args = parse_args([])
        self.assertEqual(args.rounds, 15)
        self.assertEqual(Path(args.report), DEFAULT_REPORT)
        self.assertTrue(str(DEFAULT_REPORT).endswith("reports/jev-wording.html"))

    def test_one_round_uses_each_variants_prompt_and_no_other_player(self):
        client = RecordingClient()
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "jev-prompts.html"
            with (
                patch(
                    "schnapsen.prompt_harness._now",
                    return_value=datetime.fromisoformat("2026-09-29T15:40:00+02:00"),
                ),
                patch("typesafe_sdk.TypeSafeClient", _RejectLive),
                redirect_stdout(StringIO()),
            ):
                play_prompts(1, report, client=client)
            text = report.read_text(encoding="utf-8")
            saved = json.loads((Path(directory) / "jev-prompts-20260929T154000.json").read_text())
        self.assertEqual(saved["rounds_per_pairing"], 1)
        self.assertEqual(len(saved["pairings"]), 10)
        self.assertEqual(set(saved["players"]), {variant.id for variant in VARIANTS})
        self.assertEqual(set(client.instructions), {variant.instructions for variant in VARIANTS})
        self.assertIn("Seat A", text)
        self.assertIn("Deals won A", text)
        self.assertIn('data-player="which-reach"', text)
        self.assertIn('data-player="select-count"', text)
        self.assertNotIn('data-player="random"', text)
        self.assertNotIn('data-player="llm"', text)
        self.assertEqual(text.count('class="round"'), 10)

    def test_a_missing_jev_key_writes_no_report(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "jev-prompts.html"
            with patch("schnapsen.prompt_harness.read_api_key", return_value=""):
                code = main(["--rounds", "1", "--report", str(report)])
            self.assertEqual(code, 1)
            self.assertFalse(report.exists())
            self.assertEqual(list(Path(directory).glob("*.json")), [])

    def test_each_match_reuses_one_jev_client_and_opens_no_chat_connection(self):
        events = []

        class FakeLive:
            def __init__(self, **kwargs):
                events.append("open")

            def __enter__(self):
                return self

            def __exit__(self, *args):
                events.append("close")
                return False

            def system_one(self, state, questions):
                action = sorted(questions["play"].criteria)[0]
                return SimpleNamespace(choices={"play": SimpleNamespace(choice=action)})

        class FakeConn:
            def __init__(self, *args, **kwargs):
                raise AssertionError("opened a ChatGPT connection")

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "jev-prompts.html"
            with (
                patch("typesafe_sdk.TypeSafeClient", FakeLive),
                patch("schnapsen.llm_player.http.client.HTTPSConnection", FakeConn),
                patch("schnapsen.prompt_harness.read_api_key", return_value="present"),
                patch("schnapsen.jev_player.read_api_key", return_value="present"),
                redirect_stdout(StringIO()),
            ):
                play_prompts(1, report)
        depth = 0
        opened = 0
        for event in events:
            if event == "open":
                self.assertEqual(depth, 0)
                depth = 1
                opened += 1
            else:
                self.assertEqual(depth, 1)
                depth = 0
        self.assertEqual(depth, 0)
        self.assertEqual(opened, len(PAIRINGS))
