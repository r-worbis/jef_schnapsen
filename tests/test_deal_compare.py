import json
import random
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from schnapsen.engine import legal_action_ids
from schnapsen.llm_player import LlmPlayer
from schnapsen.deal_compare import (
    OLD_INSTRUCTION,
    SWAPPED_SEATS,
    compare,
    opening_influence,
    pack_tokens,
    play_deal,
    replay_logged,
    sample_deals,
)
from schnapsen.engine import match_with_deal
from schnapsen.cards import parse_card
from schnapsen.jev_player import INSTRUCTION


class ChoosingClient:
    def __init__(self):
        self.instructions = []

    def system_one(self, state, questions):
        self.instructions.append(questions["play"].instructions)
        action_id = sorted(questions["play"].criteria)[0]
        return SimpleNamespace(choices={"play": SimpleNamespace(choice=action_id)})


class DealCompareTests(unittest.TestCase):
    def test_logged_pack_rebuilds_the_opening(self):
        spec = sample_deals(1, random.Random(4))[0]
        original = match_with_deal(spec["dealer"], [parse_card(token) for token in spec["pack"]])
        self.assertEqual(pack_tokens(original), spec["pack"])
        self.assertEqual(len(spec["pack"]), 20)
        self.assertEqual(len(set(spec["pack"])), 20)

    def test_both_prompts_play_the_same_logged_deal(self):
        client = ChoosingClient()
        with tempfile.TemporaryDirectory() as folder:
            log = Path(folder) / "deals.json"
            report = Path(folder) / "report.html"
            document = compare(1, log, report, client=client, rng=random.Random(7))
            saved = json.loads(log.read_text(encoding="utf-8"))
            page = report.read_text(encoding="utf-8")
        self.assertEqual(saved["deals"], document["deals"])
        self.assertEqual(saved["runs"]["new"]["instruction"], INSTRUCTION)
        self.assertEqual(saved["runs"]["old"]["instruction"], OLD_INSTRUCTION)
        self.assertEqual(document["runs"]["new"]["deals"][0]["winner"], document["runs"]["old"]["deals"][0]["winner"])
        self.assertIn(INSTRUCTION, client.instructions)
        self.assertIn(OLD_INSTRUCTION, client.instructions)
        self.assertIn("New winner", page)

    def test_swapped_seats_put_jev_on_the_human_hand(self):
        spec = sample_deals(1, random.Random(3))[0]
        row = play_deal(spec, INSTRUCTION, ChoosingClient(), players=SWAPPED_SEATS)
        self.assertEqual(row["winner"] == "jev", row["winner_seat"] == "human")

    def test_replay_uses_the_logged_pack_and_swapped_seats(self):
        spec = sample_deals(1, random.Random(9))[0]
        source = {
            "deals": [spec],
            "runs": {
                "new": {"instruction": INSTRUCTION, "deals": []},
                "old": {"instruction": OLD_INSTRUCTION, "deals": []},
            },
        }
        with tempfile.TemporaryDirectory() as folder:
            src = Path(folder) / "source.json"
            src.write_text(json.dumps(source), encoding="utf-8")
            document = replay_logged(
                src,
                Path(folder) / "out.json",
                Path(folder) / "out.html",
                players=SWAPPED_SEATS,
                client=ChoosingClient(),
            )
        self.assertEqual(document["deals"][0]["pack"], spec["pack"])
        self.assertEqual(document["seats"], SWAPPED_SEATS)
        self.assertEqual(document["runs"]["new"]["deals"][0]["winner_seat"] == "human",
                         document["runs"]["new"]["deals"][0]["winner"] == "jev")

    def test_same_seat_counts_as_cards_and_same_player_as_player(self):
        deals = [{"index": 1, "dealer": "computer"}, {"index": 2, "dealer": "human"}]
        original = [
            {"winner": "jev", "game_points": 2, "eyes": {"jev": 70, "random": 10}},
            {"winner": "random", "game_points": 1, "eyes": {"jev": 20, "random": 66}},
        ]
        swapped = [
            {"winner": "random", "game_points": 3, "eyes": {"jev": 0, "random": 80}},
            {"winner": "random", "game_points": 1, "eyes": {"jev": 30, "random": 66}},
        ]
        result = opening_influence(deals, original, swapped)
        self.assertEqual(result["cards"], 1)
        self.assertEqual(result["player"], 1)
        self.assertEqual(result["random_both"], 1)
        self.assertEqual(result["dealer_cards"], 1)
        self.assertEqual(result["jev_points"], 2)
        self.assertEqual(result["computer_points"], 6)

    def test_llm_opponent_is_recorded_on_the_human_seat(self):
        spec = sample_deals(1, random.Random(5))[0]
        player = LlmPlayer(reply=lambda match: sorted(legal_action_ids(match))[0])
        row = play_deal(
            spec,
            INSTRUCTION,
            ChoosingClient(),
            players={"computer": "jev", "human": "llm"},
            llm_player=player,
        )
        self.assertEqual(row["winner"] == "llm", row["winner_seat"] == "human")
        self.assertIn("llm", row["eyes"])


if __name__ == "__main__":
    unittest.main()
