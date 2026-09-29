"""Views, the Jev player, the local table, and a full match."""

import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from schnapsen.cards import Card, full_pack
from schnapsen.keyfile import CHAT_KEY_PATH, KEY_PATH, read_api_key, read_chat_api_key, read_chat_settings
from schnapsen.engine import (
    apply_action,
    legal_action_ids,
    match_with_deal,
    new_match,
    record_game_points,
    start_deal,
)
from schnapsen.jev_player import _HeldClient, close_jev_client
from schnapsen.llm_player import LlmPlayer
from schnapsen.random_player import RandomPlayer
from schnapsen.turn import take_ai_turn
from schnapsen.rules_text import RULES
from schnapsen.server import Table, make_server
from schnapsen import server as server_module
from schnapsen.view import human_view, jev_state


class FakeClient:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def system_one(self, state, questions):
        self.calls.append({"state": state, "questions": questions})
        item = self.answers.pop(0)
        if isinstance(item, Exception):
            raise item
        return SimpleNamespace(choices={"play": SimpleNamespace(choice=item)})


class ChoosingClient:
    def __init__(self):
        self.calls = []

    def system_one(self, state, questions):
        self.calls.append({"state": state, "questions": questions})
        action_id = sorted(questions["play"].criteria)[0]
        return SimpleNamespace(choices={"play": SimpleNamespace(choice=action_id)})


def card(suit, rank):
    return Card(suit, rank)


def seated(leader, human, computer, trump, talon):
    match = match_with_deal("computer", full_pack())
    deal = match.deal
    deal.hands = {"human": list(human), "computer": list(computer)}
    deal.talon = list(talon)
    deal.trump_card = trump
    deal.trump_suit = trump.suit if trump else "Herz"
    deal.leader = leader
    deal.to_play = leader
    deal.current_trick = []
    deal.tricks = {"human": [], "computer": []}
    deal.won_trick = {"human": False, "computer": False}
    deal.marriage_eyes = {"human": 0, "computer": 0}
    deal.phase = "play"
    deal.closed = False
    deal.closed_by = None
    deal.computer_action = None
    return match


def require_key():
    key = read_api_key()
    if not key:
        raise unittest.SkipTest("jef.api is missing")
    return key


class PageSourceTests(unittest.TestCase):
    def test_player_choices_and_bound_turn_request(self):
        page = Path("schnapsen/page.html").read_text(encoding="utf-8")
        self.assertIn("Mensch", page)
        self.assertIn("Jev", page)
        self.assertIn("Zufall", page)
        left = page.split('id="left-player"', 1)[1].split("</select>", 1)[0]
        self.assertNotIn("Mensch", left)
        self.assertIn("Jev", left)
        self.assertIn("Zufall", left)
        self.assertIn("LLM", left)
        self.assertIn('value="random"', page)
        self.assertIn('value="llm"', page)
        self.assertIn(">LLM<", page)
        self.assertNotIn('value="stub"', page)
        self.assertIn('state.missingChatKey && kind === "llm"', page)
        self.assertIn("players[state.toPlay]", page)
        self.assertNotIn('toPlay === "computer"', page)


class KeyfileTests(unittest.TestCase):
    def test_gitignore_lists_jef_api(self):
        listed = Path(".gitignore").read_text(encoding="utf-8")
        self.assertIn("jef.api", listed)

    def test_gitignore_lists_chat_api(self):
        lines = Path(".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("chat.api", lines)

    def test_helper_reads_a_temporary_chat_key(self):
        self.assertEqual(CHAT_KEY_PATH.name, "chat.api")
        missing = Path(tempfile.gettempdir()) / "chat-api-missing-for-tests"
        self.assertEqual(read_chat_api_key(missing), "")
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        try:
            handle.write("  temp-chat-key\n")
            handle.close()
            self.assertEqual(read_chat_api_key(Path(handle.name)), "temp-chat-key")
        finally:
            Path(handle.name).unlink(missing_ok=True)
        labeled = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        try:
            labeled.write(
                "url=https://api.openai.com/v1/chat/completions\n"
                "model=gpt-6-sol\n"
                "key=temp-chat-key\n"
            )
            labeled.close()
            self.assertEqual(read_chat_api_key(Path(labeled.name)), "temp-chat-key")
            url, model, key = read_chat_settings(Path(labeled.name))
            self.assertEqual(url, "https://api.openai.com/v1/chat/completions")
            self.assertEqual(model, "gpt-6-sol")
            self.assertEqual(key, "temp-chat-key")
        finally:
            Path(labeled.name).unlink(missing_ok=True)

    def test_helper_reads_jef_api_and_treats_missing_as_empty(self):
        self.assertEqual(KEY_PATH.name, "jef.api")
        missing = Path(tempfile.gettempdir()) / "jef-api-missing-for-tests"
        self.assertEqual(read_api_key(missing), "")
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        try:
            handle.write("  \n")
            handle.close()
            self.assertEqual(read_api_key(Path(handle.name)), "")
        finally:
            Path(handle.name).unlink(missing_ok=True)
        self.assertTrue(bool(read_api_key()))


class RulesAndViewTests(unittest.TestCase):
    def test_rules_cover_the_game_and_are_not_a_wikipedia_copy(self):
        lowered = RULES.lower()
        for topic in ("trump", "marriage", "exchange", "clos", "66", "last trick", "bummerl"):
            self.assertIn(topic, lowered)
        self.assertIn("no declaration", lowered)
        self.assertNotIn("wikipedia", lowered)

    def test_missing_chat_key_is_separate_and_hides_the_llm_hand(self):
        match = seated(
            "computer",
            [card("Herz", "Ass"), card("Herz", "König")],
            [card("Pik", "Dame"), card("Pik", "Bube")],
            card("Kreuz", "Zehner"),
            [card("Karo", "Ass")],
        )
        match.players = {"human": "llm", "computer": "random"}
        match.notice = "missing-chat-key"
        view = human_view(match)
        self.assertTrue(view["missingChatKey"])
        self.assertFalse(view["missingKey"])
        payload = json.dumps({key: value for key, value in view.items() if key != "jev"})
        for held in match.deal.hands["human"] + match.deal.hands["computer"]:
            self.assertNotIn(held.label, payload)

    def test_fresh_human_view_hides_the_computer_hand_and_the_talon(self):
        match = match_with_deal("computer", full_pack())
        payload = json.dumps(human_view(match))
        view = json.loads(payload)
        self.assertEqual(len(view["yourHand"]), 5)
        self.assertEqual(view["opponentCount"], 5)
        self.assertEqual(view["trump"], "Karo Zehner")
        self.assertEqual(view["talonCount"], 9)
        self.assertEqual(view["pointsNeeded"], {"human": 7, "computer": 7})
        self.assertEqual(view["bummerl"], {"human": 0, "computer": 0})
        hidden = match.deal.hands["computer"] + match.deal.talon
        for hidden_card in hidden:
            self.assertNotIn(hidden_card.label, payload)
        self.assertEqual(view["jev"], {"rules": "", "cards": "", "answers": [], "failed": False})

    def test_requested_computer_card_is_only_in_the_jev_cards_text(self):
        match = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )
        take_ai_turn(match, FakeClient(["play:Karo-König"]))
        view = human_view(match)
        held = "Herz Bube"
        self.assertIn(held, [item.label for item in match.deal.hands["computer"]])
        self.assertIn(held, view["jev"]["cards"])
        rest = dict(view)
        rest["jev"] = {**view["jev"], "cards": ""}
        self.assertNotIn(held, json.dumps(rest))

    def test_two_game_points_count_down_from_seven(self):
        match = match_with_deal("computer", full_pack())
        record_game_points(match, "human", 2)
        view = human_view(match)
        self.assertEqual(view["pointsNeeded"]["human"], 5)
        self.assertEqual(view["pointsNeeded"]["computer"], 7)

    def test_jev_state_has_the_computer_hand_rules_and_legal_ids_only(self):
        match = match_with_deal("computer", full_pack())
        match.deal.to_play = "computer"
        state = jev_state(match)
        for held in match.deal.hands["computer"]:
            self.assertIn(held.label, state)
        self.assertIn(RULES, state)
        self.assertIn("Talon count: 9", state)
        self.assertIn("Trump suit: Karo", state)
        self.assertIn("Bummerl:", state)
        self.assertIn("play:Herz-Dame", state)
        for hidden_card in match.deal.hands["human"] + match.deal.talon:
            self.assertNotIn(hidden_card.label, state)

    def test_jev_state_lists_every_awarded_trick_and_still_hides_the_human_hand(self):
        match = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )
        first = [card("Pik", "Zehner"), card("Herz", "König")]
        second = [card("Karo", "Ass"), card("Herz", "Zehner")]
        computer_won = [card("Kreuz", "König"), card("Pik", "Dame")]
        match.deal.tricks = {"human": [first, second], "computer": [computer_won]}
        match.deal.won_trick = {"human": True, "computer": True}
        match.deal.hands["human"] = [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Bube"), card("Kreuz", "Ass")]
        match.deal.to_play = "computer"
        state = jev_state(match)
        self.assertIn("Pik Zehner", state)
        self.assertIn("Herz König", state)
        self.assertIn("Karo Ass", state)
        self.assertIn("Herz Zehner", state)
        self.assertIn("Kreuz König", state)
        self.assertIn("Pik Dame", state)
        self.assertIn("Opponent tricks:", state)
        self.assertIn("Your tricks:", state)
        self.assertIn(RULES, state)
        for held in match.deal.hands["computer"]:
            self.assertIn(held.label, state)
        self.assertNotIn("Pik Ass", state)
        self.assertNotIn("Pik König", state)
        self.assertNotIn("Kreuz Zehner", state)

    def test_human_view_still_shows_only_the_computer_first_trick(self):
        match = seated(
            "human",
            [card("Pik", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König")],
            card("Herz", "Ass"),
            [],
        )
        first = [card("Herz", "Zehner"), card("Pik", "Bube")]
        later = [card("Karo", "Ass"), card("Kreuz", "Ass")]
        match.deal.tricks = {"human": [], "computer": [first, later]}
        view = human_view(match)
        self.assertEqual(view["opponentFirstTrick"], [["Herz Zehner", "Pik Bube"]])
        payload = json.dumps({k: v for k, v in view.items() if k != "jev"})
        self.assertNotIn("Karo Ass", payload)
        self.assertNotIn("Kreuz Ass", payload)


class PlayerTests(unittest.TestCase):
    def setUp(self):
        require_key()
        self.match = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )

    def test_chosen_action_is_the_only_one_applied(self):
        client = FakeClient(["play:Karo-König"])
        take_ai_turn(self.match, client)
        state = client.calls[0]["state"]
        self.assertIn("Herz Bube", state)
        self.assertIn("Karo König", state)
        self.assertIn(RULES, state)
        self.assertEqual(self.match.deal.trump_card, card("Herz", "Ass"))
        self.assertIn(card("Herz", "Bube"), self.match.deal.hands["computer"])
        self.assertEqual(self.match.deal.current_trick, [("computer", card("Karo", "König"))])
        self.assertFalse(self.match.choice_replaced)

    def test_illegal_answer_is_retried_then_fallback_and_missing_key_stops(self):
        legal = sorted(legal_action_ids(self.match))
        retry = FakeClient(["nope", "play:Karo-König"])
        take_ai_turn(self.match, retry)
        self.assertEqual(len(retry.calls), 2)
        self.assertEqual(self.match.deal.current_trick[0][1], card("Karo", "König"))
        self.assertFalse(self.match.choice_replaced)

        fresh = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )
        failed = FakeClient(["nope", "still-nope"])
        take_ai_turn(fresh, failed)
        self.assertEqual(len(failed.calls), 2)
        self.assertTrue(fresh.choice_replaced)
        self.assertEqual(fresh.deal.current_trick[0][1].token, legal[0].split(":")[-1])

        errored = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )
        broken = FakeClient([RuntimeError("down")])
        take_ai_turn(errored, broken)
        self.assertEqual(len(broken.calls), 1)
        self.assertTrue(errored.choice_replaced)
        self.assertEqual(len(errored.deal.current_trick), 1)

        untouched = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )
        quiet = FakeClient(["play:Karo-König"])
        with patch("schnapsen.turn.read_api_key", return_value=""):
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": "env-key"}):
                take_ai_turn(untouched, quiet)
        self.assertEqual(quiet.calls, [])
        self.assertEqual(untouched.deal.current_trick, [])
        self.assertEqual(untouched.notice, "missing-key")

    def test_live_client_receives_jef_api_key(self):
        key = require_key()
        captured = {}

        class FakeLive:
            def __init__(self, **kwargs):
                captured.update(kwargs)
                self.enters = 0
                self.exits = 0

            def __enter__(self):
                self.enters += 1
                return FakeClient(["play:Karo-König"])

            def __exit__(self, *args):
                self.exits += 1
                return False

        with patch("typesafe_sdk.TypeSafeClient", FakeLive):
            take_ai_turn(self.match)
        self.assertTrue(captured.get("api_key") == key)
        live = getattr(self.match, "_jev_client")
        self.assertEqual(live.owner.enters, 1)
        self.assertEqual(live.owner.exits, 0)
        self.assertEqual(self.match.deal.current_trick[0][1], card("Karo", "König"))
        close_jev_client(self.match)
        self.assertEqual(live.owner.exits, 1)
        self.assertFalse(hasattr(self.match, "_jev_client"))

    def _fresh_seat(self):
        return seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )

    def test_one_jev_client_lasts_for_the_match(self):
        made = []
        script = []

        class FakeLive:
            def __init__(self, **kwargs):
                self.exits = 0
                self.calls = 0
                made.append(self)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.exits += 1
                return False

            def system_one(self, state, questions):
                self.calls += 1
                item = script.pop(0) if script else sorted(questions["play"].criteria)[0]
                return SimpleNamespace(choices={"play": SimpleNamespace(choice=item)})

        def both_jev(match):
            match.players = {"human": "jev", "computer": "jev"}
            return match

        with patch("typesafe_sdk.TypeSafeClient", FakeLive):
            match = both_jev(self.match)
            take_ai_turn(match)
            take_ai_turn(match)
            self.assertEqual(len(made), 1)
            self.assertEqual(made[0].calls, 2)
            self.assertEqual(made[0].exits, 0)

            retry = both_jev(self._fresh_seat())
            legal = sorted(legal_action_ids(retry))
            script[:] = ["nope", legal[0]]
            take_ai_turn(retry)
            self.assertEqual(len(made), 2)
            self.assertEqual(made[1].calls, 2)
            self.assertEqual(made[1].exits, 0)
            self.assertTrue(retry.deal.current_trick)

            later = both_jev(self._fresh_seat())
            take_ai_turn(later)
            start_deal(later)
            take_ai_turn(later)
            self.assertEqual(len(made), 3)
            self.assertGreaterEqual(made[2].calls, 2)
            close_jev_client(later)
            self.assertEqual(made[2].exits, 1)
            follow = both_jev(self._fresh_seat())
            take_ai_turn(follow)
            self.assertEqual(len(made), 4)
            self.assertIsNot(made[2], made[3])

            quiet = self._fresh_seat()
            quiet.players = {"human": "random", "computer": "random"}
            before = len(made)
            take_ai_turn(quiet, random_player=RandomPlayer(lambda hand: hand[0]))
            self.assertEqual(len(made), before)

            supplied = FakeClient(["play:Karo-König"])
            supplied.exits = 0

            def leave(*args):
                supplied.exits += 1
                return False

            supplied.__exit__ = leave
            owned = both_jev(self._fresh_seat())
            take_ai_turn(owned, supplied)
            close_jev_client(owned)
            self.assertEqual(len(supplied.calls), 1)
            self.assertEqual(supplied.exits, 0)
            self.assertEqual(len(made), before)

    def test_kept_exchange_records_answers_failures_and_survives_a_missing_key(self):
        key = require_key()
        client = FakeClient(["play:Karo-König"])
        take_ai_turn(self.match, client)
        exchange = self.match.jev_exchange
        self.assertIsNotNone(exchange)
        self.assertEqual(exchange.rules, RULES)
        self.assertIn("Herz Bube", exchange.cards)
        self.assertIn("Karo König", exchange.cards)
        self.assertEqual(exchange.answers, ["play:Karo-König"])
        self.assertFalse(exchange.failed)
        self.assertNotIn(key, exchange.rules)
        self.assertNotIn(key, exchange.cards)
        self.assertNotIn(key, "".join(exchange.answers))
        self.assertIn(RULES, client.calls[0]["state"])
        self.assertIn("Herz Bube", client.calls[0]["state"])
        self.assertEqual(self.match.deal.current_trick, [("computer", card("Karo", "König"))])

        retried = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )
        take_ai_turn(retried, FakeClient(["nope", "play:Karo-König"]))
        self.assertEqual(retried.jev_exchange.answers, ["nope", "play:Karo-König"])
        self.assertFalse(retried.jev_exchange.failed)
        self.assertEqual(retried.jev_exchange.rules, RULES)
        self.assertIn("Your cards:", retried.jev_exchange.cards)
        self.assertEqual(retried.deal.current_trick[0][1], card("Karo", "König"))

        errored = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Kreuz", "Ass")],
            [card("Herz", "Bube"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube"), card("Kreuz", "König")],
            card("Herz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")],
        )
        legal = sorted(legal_action_ids(errored))
        take_ai_turn(errored, FakeClient([RuntimeError("down")]))
        self.assertEqual(errored.jev_exchange.answers, [])
        self.assertTrue(errored.jev_exchange.failed)
        self.assertTrue(errored.choice_replaced)
        self.assertEqual(errored.deal.current_trick[0][1].token, legal[0].split(":")[-1])

        kept = errored.jev_exchange
        errored.deal.to_play = "computer"
        with patch("schnapsen.turn.read_api_key", return_value=""):
            take_ai_turn(errored, FakeClient(["play:Karo-König"]))
        self.assertIs(errored.jev_exchange, kept)
        self.assertEqual(errored.jev_exchange.answers, [])
        self.assertTrue(errored.jev_exchange.failed)

    def test_jev_on_the_right_is_shown_that_hand_only(self):
        match = seated(
            "human",
            [card("Herz", "Bube"), card("Karo", "König")],
            [card("Pik", "Ass")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner")],
        )
        match.players = {"human": "jev", "computer": "random"}
        state = jev_state(match)
        self.assertIn("Herz Bube", state)
        self.assertIn("Karo König", state)
        self.assertNotIn("Pik Ass", state)


class StubTests(unittest.TestCase):
    def test_one_legal_card_is_a_plain_play_and_does_not_call_jev(self):
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Karo", "König"), card("Herz", "Bube")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "König")],
        )
        match.players = {"human": "human", "computer": "random"}
        client = FakeClient(["play:Karo-König"])
        take_ai_turn(match, client, RandomPlayer(lambda hand: card("Karo", "König")))
        self.assertEqual(client.calls, [])
        self.assertEqual(match.deal.current_trick, [("computer", card("Karo", "König"))])
        action = match.deal.last_action
        self.assertFalse(action.exchange)
        self.assertFalse(action.closed)
        self.assertIsNone(action.marriage)
        self.assertFalse(match.choice_replaced)

    def test_illegal_card_is_unchanged_until_the_second_proposal(self):
        match = seated(
            "human",
            [card("Karo", "König")],
            [card("Karo", "Bube"), card("Herz", "Ass")],
            card("Pik", "Ass"),
            [],
        )
        match.deal.trump_card = None
        apply_action(match, "play:Karo-König")
        match.players["computer"] = "random"
        seen = []

        def choose(hand):
            seen.append(len(match.deal.current_trick))
            if len(seen) == 1:
                return card("Herz", "Ass")
            self.assertEqual(match.deal.current_trick, [("human", card("Karo", "König"))])
            self.assertEqual(match.deal.to_play, "computer")
            return card("Karo", "Bube")

        take_ai_turn(match, random_player=RandomPlayer(choose))
        self.assertEqual(seen, [1, 1])
        self.assertEqual(match.deal.current_trick[-1][1], card("Karo", "Bube"))
        self.assertFalse(match.choice_replaced)

    def test_two_illegal_cards_use_the_predetermined_action(self):
        match = seated(
            "human",
            [card("Karo", "König")],
            [card("Karo", "Bube"), card("Herz", "Ass")],
            card("Pik", "Ass"),
            [],
        )
        match.deal.trump_card = None
        apply_action(match, "play:Karo-König")
        match.players["computer"] = "random"
        legal = sorted(legal_action_ids(match))
        take_ai_turn(match, random_player=RandomPlayer(lambda hand: card("Herz", "Ass")))
        self.assertTrue(match.choice_replaced)
        self.assertEqual(match.deal.current_trick[-1][1].token, legal[0].split(":")[-1])

    def test_two_stubs_award_a_trick_without_seen(self):
        match = seated(
            "computer",
            [card("Karo", "Ass")],
            [card("Pik", "Ass")],
            card("Herz", "Bube"),
            [card("Kreuz", "Ass"), card("Kreuz", "Zehner")],
        )
        match.players = {"human": "random", "computer": "random"}
        planned = [card("Pik", "Ass"), card("Karo", "Ass")]
        client = FakeClient([])
        stub = RandomPlayer(lambda hand: planned.pop(0))
        take_ai_turn(match, client, stub)
        take_ai_turn(match, client, stub)
        self.assertEqual(client.calls, [])
        self.assertEqual(match.deal.current_trick, [])
        self.assertNotIn("seen", legal_action_ids(match))
        self.assertEqual(match.deal.tricks["computer"][-1], [card("Pik", "Ass"), card("Karo", "Ass")])

    def test_stub_turn_leaves_the_kept_jev_exchange(self):
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Karo", "König"), card("Herz", "Bube")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "König")],
        )
        take_ai_turn(match, FakeClient(["play:Karo-König"]))
        kept = match.jev_exchange
        match.deal.phase = "play"
        match.deal.to_play = "computer"
        match.players["computer"] = "random"
        take_ai_turn(match, random_player=RandomPlayer(lambda hand: hand[0]))
        self.assertIs(match.jev_exchange, kept)
        self.assertEqual(kept.answers, ["play:Karo-König"])


def serve(table):
    httpd = make_server(table, 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    return httpd, f"http://{host}:{port}"


def stop(httpd):
    httpd.shutdown()
    httpd.server_close()


def request(url, payload=None, decode="json"):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="GET" if payload is None else "POST")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read()
            status = response.status
    except urllib.error.HTTPError as error:
        body = error.read()
        status = error.code
        error.close()
    if decode == "json":
        return status, json.loads(body.decode())
    return status, body


class ServerTests(unittest.TestCase):
    def test_get_does_not_call_jev_and_post_applies_or_refuses(self):
        self.assertIn("jef.api", server_module.__doc__)
        self.assertNotIn("TYPESAFE_API_KEY", server_module.__doc__)
        self.assertIn("python -m schnapsen", server_module.__doc__)
        match = match_with_deal("computer", full_pack())
        client = FakeClient(["play:Herz-Dame"])
        table = Table(match, client)
        httpd, base = serve(table)
        try:
            status, page = request(base + "/", decode="bytes")
            self.assertEqual(status, 200)
            self.assertIn(b"your-hand", page)
            self.assertIn(b"jef.api", page)
            self.assertIn(b"Jev anzeigen", page)
            self.assertIn(b"Jev ausblenden", page)
            self.assertIn("Spielregeln".encode("utf-8"), page)
            self.assertIn("Karten und Optionen".encode("utf-8"), page)
            self.assertIn("Ergebnis".encode("utf-8"), page)
            self.assertIn("Noch keine Anfrage.".encode("utf-8"), page)
            self.assertIn("Die Anfrage ist fehlgeschlagen.".encode("utf-8"), page)
            self.assertNotIn(b"TYPESAFE_API_KEY", page)
            status, view = request(base + "/api/state")
            self.assertEqual(status, 200)
            self.assertEqual(client.calls, [])
            self.assertEqual(len(view["yourHand"]), 5)
            self.assertEqual(view["players"], {"human": "human", "computer": "jev"})
            before = list(match.deal.hands["human"])
            status, refused = request(base + "/api/action", {"id": "play:No-Such"})
            self.assertEqual(status, 400)
            self.assertFalse(refused["applied"])
            self.assertEqual(match.deal.hands["human"], before)
            self.assertEqual(client.calls, [])
            status, played = request(base + "/api/action", {"id": "play:Herz-Ass"})
            self.assertEqual(status, 200)
            self.assertTrue(played["applied"])
            self.assertTrue(any(item["card"] == "Herz Ass" for item in played["trick"]) or _card_was_played(match, "Herz Ass"))
        finally:
            stop(httpd)

    def test_match_binding_hides_two_stubs_and_refuses_a_person_on_the_left(self):
        match = match_with_deal("computer", full_pack())
        table = Table(match)
        httpd, base = serve(table)
        try:
            status, before = request(base + "/api/state")
            self.assertEqual(status, 200)
            self.assertEqual(len(before["yourHand"]), 5)
            status, denied = request(base + "/api/match", {"human": "jev", "computer": "human"})
            self.assertEqual(status, 400)
            self.assertEqual(denied["yourHand"], before["yourHand"])
            self.assertEqual(denied["trump"], before["trump"])
            self.assertIs(table.match, match)
            status, unknown = request(base + "/api/match", {"human": "wizard", "computer": "jev"})
            self.assertEqual(status, 400)
            self.assertIs(table.match, match)
            status, old_kind = request(base + "/api/match", {"human": "stub", "computer": "random"})
            self.assertEqual(status, 400)
            self.assertIs(table.match, match)
            status, started = request(base + "/api/match", {"human": "random", "computer": "random"})
            self.assertEqual(status, 200)
            self.assertEqual(started["players"], {"human": "random", "computer": "random"})
            self.assertEqual(started["yourHand"], [])
            self.assertEqual(started["yourCount"], 5)
            self.assertEqual(started["opponentCount"], 5)
            payload = json.dumps(started)
            hidden = (
                table.match.deal.hands["human"]
                + table.match.deal.hands["computer"]
                + table.match.deal.talon
            )
            for hidden_card in hidden:
                self.assertNotIn(hidden_card.label, payload)
        finally:
            stop(httpd)

    def test_stub_turn_plays_when_the_key_file_is_missing(self):
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Karo", "König")],
            card("Herz", "Bube"),
            [card("Kreuz", "Ass"), card("Kreuz", "Zehner")],
        )
        match.players = {"human": "random", "computer": "random"}
        client = FakeClient(["play:Karo-König"])
        table = Table(match, client)
        table.random_player = RandomPlayer(lambda hand: card("Karo", "König"))
        httpd, base = serve(table)
        try:
            with patch("schnapsen.turn.read_api_key", return_value=""):
                status, view = request(base + "/api/computer", {})
            self.assertEqual(status, 200)
            self.assertEqual(client.calls, [])
            self.assertFalse(view["missingKey"])
            self.assertEqual(view["trick"], [{"seat": "computer", "card": "Karo König"}])
        finally:
            stop(httpd)

    def test_computer_answer_stays_until_seen(self):
        trump = card("Herz", "Bube")
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König")]
        human = [card("Karo", "Ass"), card("Pik", "Dame"), card("Pik", "König"), card("Pik", "Zehner"), card("Pik", "Bube")]
        computer = [card("Karo", "König"), card("Pik", "Ass"), card("Herz", "Zehner"), card("Karo", "Dame"), card("Karo", "Bube")]
        match = seated("human", human, computer, trump, talon)
        client = FakeClient(["play:Karo-König"])
        table = Table(match, client)
        httpd, base = serve(table)
        try:
            status, played = request(base + "/api/action", {"id": "play:Karo-Ass"})
            self.assertEqual(status, 200)
            self.assertEqual(
                [(item["seat"], item["card"]) for item in played["trick"]],
                [("human", "Karo Ass"), ("computer", "Karo König")],
            )
            self.assertEqual(played["eyes"], {"human": 0, "computer": 0})
            self.assertTrue(played["yourTurn"])
            self.assertEqual(played["toPlay"], "human")
            self.assertEqual(played["actions"], [{"id": "seen", "label": "Gesehen"}])
            self.assertEqual(len(client.calls), 1)

            status, again = request(base + "/api/state")
            self.assertEqual(status, 200)
            self.assertEqual(again["trick"], played["trick"])
            self.assertEqual(again["actions"], [{"id": "seen", "label": "Gesehen"}])

            status, idle = request(base + "/api/computer", {})
            self.assertEqual(status, 200)
            self.assertEqual(len(client.calls), 1)
            self.assertEqual(idle["trick"], played["trick"])

            status, seen = request(base + "/api/action", {"id": "seen"})
            self.assertEqual(status, 200)
            self.assertEqual(seen["eyes"]["human"], 15)
            self.assertEqual(seen["trick"], [])
        finally:
            stop(httpd)

    def test_state_keeps_the_jev_exchange_after_a_computer_turn(self):
        trump = card("Herz", "Bube")
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König")]
        human = [card("Karo", "Ass"), card("Pik", "Dame"), card("Pik", "König"), card("Pik", "Zehner"), card("Pik", "Bube")]
        computer = [card("Karo", "König"), card("Pik", "Ass"), card("Herz", "Zehner"), card("Karo", "Dame"), card("Karo", "Bube")]
        match = seated("human", human, computer, trump, talon)
        client = FakeClient(["play:Karo-König"])
        table = Table(match, client)
        httpd, base = serve(table)
        try:
            status, played = request(base + "/api/action", {"id": "play:Karo-Ass"})
            self.assertEqual(status, 200)
            jev = played["jev"]
            self.assertEqual(jev["rules"], RULES)
            self.assertIn("Karo König", jev["cards"])
            self.assertEqual(jev["answers"], ["play:Karo-König"])
            self.assertFalse(jev["failed"])
            status, again = request(base + "/api/state")
            self.assertEqual(status, 200)
            self.assertEqual(again["jev"], jev)
        finally:
            stop(httpd)

    def test_computer_payloads_for_exchange_marriage_close_declare_key_and_replacement(self):
        trump = card("Herz", "Ass")
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König"), card("Kreuz", "Dame")]
        human = [card("Pik", "Ass"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube"), card("Pik", "Zehner")]
        computer = [card("Herz", "Bube"), card("Herz", "König"), card("Herz", "Dame"), card("Karo", "Ass"), card("Karo", "König")]
        match = seated("computer", human, computer, trump, talon)
        client = FakeClient(["exchange:Karo-Ass"])
        self._expect_action(match, client, exchange=True, card="Karo Ass")

        match = seated("computer", human, computer, trump, talon)
        client = FakeClient(["marry:Herz:Herz-König"])
        view = self._expect_action(match, client, marriage="Herz", card="Herz König")
        self.assertEqual(view["computerAction"]["marriage"], "Herz")

        match = seated("computer", human, computer, trump, talon)
        client = FakeClient(["close:Karo-Ass"])
        view = self._expect_action(match, client, closed=True, card="Karo Ass")
        self.assertTrue(view["closed"])

        match = seated("human", human, computer, trump, talon)
        match.deal.tricks["computer"].append(
            [
                card("Herz", "Zehner"), card("Karo", "Zehner"), card("Pik", "Zehner"), card("Kreuz", "Zehner"),
                card("Herz", "König"), card("Karo", "König"), card("Pik", "König"), card("Kreuz", "König"),
                card("Herz", "Dame"), card("Karo", "Dame"),
                card("Pik", "Bube"), card("Kreuz", "Bube"),
            ]
        )
        match.deal.won_trick["computer"] = True
        client = FakeClient(["play:Herz-Bube"])
        table = Table(match, client)
        httpd, base = serve(table)
        try:
            status, played = request(base + "/api/action", {"id": "play:Pik-Ass"})
            self.assertEqual(status, 200)
            status, seen = request(base + "/api/action", {"id": "seen"})
            self.assertEqual(status, 200)
            self.assertTrue(seen["dealOver"])
            self.assertEqual(seen["dealWinner"], "computer")
            self.assertEqual(seen["gamePoints"], 3)
            self.assertGreaterEqual(seen["eyes"]["computer"], 66)
            self.assertTrue(seen["canNextDeal"])
            self.assertNotIn("declare", [item["id"] for item in seen["actions"]])
            self.assertNotIn("continue", [item["id"] for item in seen["actions"]])
        finally:
            stop(httpd)

        match = seated("computer", human, computer, trump, talon)
        client = FakeClient(["play:Karo-Ass"])
        table = Table(match, client)
        httpd, base = serve(table)
        try:
            with patch("schnapsen.turn.read_api_key", return_value=""):
                with patch.dict(os.environ, {"TYPESAFE_API_KEY": "env-key"}):
                    status, view = request(base + "/api/computer", {})
            self.assertEqual(status, 200)
            self.assertTrue(view["missingKey"])
            self.assertEqual(client.calls, [])
            self.assertEqual(view["trick"], [])
        finally:
            stop(httpd)

        match = seated("computer", human, computer, trump, talon)
        client = FakeClient(["nope", "nope"])
        view = self._expect_action(match, client)
        self.assertTrue(view["choiceReplaced"])
        self.assertTrue(view["trick"] or view["computerAction"]["card"])

    def _expect_action(self, match, client, **flags):
        require_key()
        table = Table(match, client)
        httpd, base = serve(table)
        try:
            status, view = request(base + "/api/computer", {})
            self.assertEqual(status, 200)
            action = view["computerAction"]
            self.assertIsNotNone(action)
            for key, value in flags.items():
                self.assertEqual(action[key], value)
            return view
        finally:
            stop(httpd)


def _card_was_played(match, label):
    deal = match.deal
    for trick in deal.tricks["human"] + deal.tricks["computer"]:
        if any(item.label == label for item in trick):
            return True
    return any(item.label == label for _, item in deal.current_trick)


def forehand_pack():
    return [
        card("Herz", "König"), card("Herz", "Dame"), card("Herz", "Ass"),
        card("Karo", "Ass"), card("Karo", "Zehner"), card("Karo", "König"),
        card("Herz", "Bube"),
        card("Herz", "Zehner"), card("Pik", "Bube"),
        card("Karo", "Dame"), card("Karo", "Bube"),
        card("Pik", "Ass"), card("Pik", "Zehner"), card("Pik", "König"), card("Pik", "Dame"),
        card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König"), card("Kreuz", "Dame"), card("Kreuz", "Bube"),
    ]


def dealer_pack():
    return [
        card("Karo", "Ass"), card("Karo", "Zehner"), card("Karo", "König"),
        card("Herz", "König"), card("Herz", "Dame"), card("Herz", "Ass"),
        card("Herz", "Bube"),
        card("Karo", "Dame"), card("Karo", "Bube"),
        card("Herz", "Zehner"), card("Pik", "Bube"),
        card("Pik", "Ass"), card("Pik", "Zehner"), card("Pik", "König"), card("Pik", "Dame"),
        card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König"), card("Kreuz", "Dame"), card("Kreuz", "Bube"),
    ]


def human_choice(view):
    ids = [item["id"] for item in view["actions"]]
    if "marry:Herz:Herz-König" in ids:
        return "marry:Herz:Herz-König"
    for rank in ("Ass", "Zehner", "König", "Dame", "Bube"):
        action_id = f"play:Herz-{rank}"
        if action_id in ids:
            return action_id
    for action_id in ids:
        if action_id.startswith("play:"):
            return action_id
    return ids[0]


    def test_a_new_match_closes_both_clients(self):
        jev = []
        chat = []

        class FakeLive:
            def __init__(self, **kwargs):
                self.exits = 0
                jev.append(self)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.exits += 1
                return False

            def system_one(self, state, questions):
                action = sorted(questions["play"].criteria)[0]
                return SimpleNamespace(choices={"play": SimpleNamespace(choice=action)})

        class FakeConn:
            def __init__(self, host, port=None, **kwargs):
                self.closed = False
                chat.append(self)

            def request(self, method, path, body=None, headers=None):
                self.body = json.loads(body)

            def getresponse(self):
                action = self.body["response_format"]["json_schema"]["schema"]["properties"]["action"]["enum"][0]
                content = json.dumps({"action": action})
                raw = json.dumps({"choices": [{"message": {"content": content}}]}).encode()
                return SimpleNamespace(status=200, read=lambda: raw)

            def close(self):
                self.closed = True

        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Herz", "Ass")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner")],
        )
        match.players = {"human": "llm", "computer": "jev"}
        table = Table(match)
        player = LlmPlayer(key="present")
        with (
            patch("typesafe_sdk.TypeSafeClient", FakeLive),
            patch("schnapsen.llm_player.http.client.HTTPSConnection", FakeConn),
            patch("schnapsen.turn.read_api_key", return_value="present"),
            patch("schnapsen.jev_player.read_api_key", return_value="present"),
            patch("schnapsen.turn.read_chat_api_key", return_value="present"),
        ):
            take_ai_turn(table.match, llm_player=player)
            take_ai_turn(table.match, llm_player=player)
            self.assertEqual(len(jev), 1)
            self.assertEqual(len(chat), 1)
            status, _payload = server_module.start_match(table, "llm", "jev")
            self.assertEqual(status, 200)
            self.assertEqual(jev[0].exits, 1)
            self.assertTrue(chat[0].closed)
            seen = set()
            for _ in range(4):
                deal = table.match.deal
                if deal is None or deal.phase != "play":
                    break
                seen.add(table.match.players[deal.to_play])
                take_ai_turn(table.match, llm_player=player)
                if seen >= {"jev", "llm"}:
                    break
        self.assertEqual(seen, {"jev", "llm"})
        self.assertEqual(len(jev), 2)
        self.assertEqual(len(chat), 2)
        self.assertEqual(jev[1].exits, 0)
        self.assertFalse(chat[1].closed)

    def test_stopping_the_server_closes_both_clients(self):
        holder = {}

        class Owner:
            def __init__(self):
                self.exits = 0

            def __exit__(self, *args):
                self.exits += 1
                return False

        class Conn:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        def init(table, match, client=None):
            table.match = match
            table.client = client
            table.random_player = None
            table.llm_player = None
            table.lock = threading.Lock()
            owner = Owner()
            conn = Conn()
            match._jev_client = _HeldClient(owner, owner)
            match._chat_connection = conn
            holder["owner"] = owner
            holder["conn"] = conn

        class Dummy:
            def serve_forever(self):
                raise KeyboardInterrupt

            def shutdown(self):
                return None

        with (
            patch("schnapsen.server.Table.__init__", init),
            patch("schnapsen.server.make_server", return_value=Dummy()),
        ):
            server_module.main()
        self.assertEqual(holder["owner"].exits, 1)
        self.assertTrue(holder["conn"].closed)


class MatchTests(unittest.TestCase):
    def test_match_ends_at_two_bummerl_and_the_sample_script_stays(self):
        require_key()
        draw = [card("Pik", "Bube"), card("Pik", "Ass")]
        rest = [item for item in full_pack() if item not in draw]
        packs = [draw + rest, forehand_pack(), dealer_pack(), forehand_pack()]
        for pack in packs[1:]:
            self.assertEqual(len(pack), 20)
            self.assertEqual(len(set(pack)), 20)
        match = new_match(scripted=packs)
        client = ChoosingClient()
        table = Table(match, client)
        httpd, base = serve(table)
        try:
            view = None
            for _ in range(80):
                status, view = request(base + "/api/state")
                self.assertEqual(status, 200)
                if view["matchOver"]:
                    break
                if view["dealOver"]:
                    request(base + "/api/action", {"id": "next-deal"})
                    continue
                if view["toPlay"] == "computer":
                    request(base + "/api/computer", {})
                    continue
                request(base + "/api/action", {"id": human_choice(view)})
            else:
                self.fail(json.dumps(view))
            self.assertEqual(view["matchWinner"], "human")
            self.assertGreaterEqual(view["bummerl"]["computer"], 2)
        finally:
            stop(httpd)
        sample = Path("decide.py").read_text(encoding="utf-8")
        self.assertIn("SAMPLE", sample)
        self.assertIn("system_one", sample)


class DecideScriptTests(unittest.TestCase):
    def test_missing_file_exits_without_answers_even_when_env_is_set(self):
        from io import StringIO

        import decide

        with patch("decide.read_api_key", return_value=""):
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": "env-key"}):
                with patch("decide.TypeSafeClient") as client_cls:
                    with patch("sys.stdout", StringIO()) as out, patch("sys.stderr", StringIO()):
                        status = decide.main()
        self.assertNotEqual(status, 0)
        printed = out.getvalue()
        self.assertNotIn("urgency", printed)
        self.assertNotIn("team", printed)
        self.assertNotIn("frustration", printed)
        client_cls.assert_not_called()

    def test_constructs_client_with_jef_api_key(self):
        import decide

        key = require_key()
        captured = {}

        class FakeLive:
            def __init__(self, **kwargs):
                captured.update(kwargs)

            def __enter__(self):
                return SimpleNamespace(
                    system_one=lambda **kwargs: SimpleNamespace(
                        nouls={"is_urgent": SimpleNamespace(noul=0.5)},
                        choices={
                            "department": SimpleNamespace(
                                choice="technical",
                                probabilities={"billing": 0.1, "technical": 0.8, "sales": 0.1},
                            )
                        },
                        scores={
                            "frustration": SimpleNamespace(
                                score=1,
                                probabilities={0: 0.2, 1: 0.5, 2: 0.3},
                                legend={0: "Calm, just stating facts", 1: "Frustrated but civil", 2: "Very angry, strong language"},
                            )
                        },
                    )
                )

            def __exit__(self, *args):
                return False

        with patch("decide.TypeSafeClient", FakeLive):
            with patch("sys.stdout"):
                status = decide.main()
        self.assertEqual(status, 0)
        self.assertTrue(captured.get("api_key") == key)


if __name__ == "__main__":
    unittest.main()
