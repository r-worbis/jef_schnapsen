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
from schnapsen.engine import legal_action_ids, match_with_deal, new_match, record_game_points
from schnapsen.keyfile import KEY_PATH, read_api_key
from schnapsen.player import perform_computer_turn
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


class KeyfileTests(unittest.TestCase):
    def test_gitignore_lists_jef_api(self):
        listed = Path(".gitignore").read_text(encoding="utf-8")
        self.assertIn("jef.api", listed)

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
        perform_computer_turn(match, FakeClient(["play:Karo-König"]))
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
        perform_computer_turn(self.match, client)
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
        perform_computer_turn(self.match, retry)
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
        perform_computer_turn(fresh, failed)
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
        perform_computer_turn(errored, broken)
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
        with patch("schnapsen.player.read_api_key", return_value=""):
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": "env-key"}):
                perform_computer_turn(untouched, quiet)
        self.assertEqual(quiet.calls, [])
        self.assertEqual(untouched.deal.current_trick, [])
        self.assertEqual(untouched.notice, "missing-key")

    def test_live_client_receives_jef_api_key(self):
        key = require_key()
        captured = {}

        class FakeLive:
            def __init__(self, **kwargs):
                captured.update(kwargs)

            def __enter__(self):
                return FakeClient(["play:Karo-König"])

            def __exit__(self, *args):
                return False

        with patch("typesafe_sdk.TypeSafeClient", FakeLive):
            perform_computer_turn(self.match)
        self.assertTrue(captured.get("api_key") == key)

    def test_kept_exchange_records_answers_failures_and_survives_a_missing_key(self):
        key = require_key()
        client = FakeClient(["play:Karo-König"])
        perform_computer_turn(self.match, client)
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
        perform_computer_turn(retried, FakeClient(["nope", "play:Karo-König"]))
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
        perform_computer_turn(errored, FakeClient([RuntimeError("down")]))
        self.assertEqual(errored.jev_exchange.answers, [])
        self.assertTrue(errored.jev_exchange.failed)
        self.assertTrue(errored.choice_replaced)
        self.assertEqual(errored.deal.current_trick[0][1].token, legal[0].split(":")[-1])

        kept = errored.jev_exchange
        errored.deal.to_play = "computer"
        with patch("schnapsen.player.read_api_key", return_value=""):
            perform_computer_turn(errored, FakeClient(["play:Karo-König"]))
        self.assertIs(errored.jev_exchange, kept)
        self.assertEqual(errored.jev_exchange.answers, [])
        self.assertTrue(errored.jev_exchange.failed)


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
            with patch("schnapsen.player.read_api_key", return_value=""):
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
