"""The ChatGPT player proposes a legal action and does not apply it."""

import json
import unittest
import urllib.error
from types import SimpleNamespace
from unittest.mock import patch

from schnapsen.cards import Card, full_pack
from schnapsen.engine import apply_action, legal_action_ids, match_with_deal, start_deal
from schnapsen.jev_player import close_jev_client
from schnapsen.llm_player import (
    SYSTEM,
    LlmPlayer,
    close_chat_connection,
    interpret_reply,
    read_choice,
)
from schnapsen.random_player import RandomPlayer
from schnapsen.rules_text import RULES
from schnapsen.turn import take_ai_turn
from schnapsen.view import jev_parts


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


class Response:
    def __init__(self, content, status=200):
        self.status = status
        self._raw = json.dumps(
            {"choices": [{"message": {"content": content}}]}
        ).encode("utf-8")

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ProposalTests(unittest.TestCase):
    def match(self):
        return seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Herz", "Ass")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner")],
        )

    def test_request_uses_the_jev_state_and_gpt_6_sol(self):
        match = self.match()
        secret = "temp-chat-secret"
        seen = {}

        def opener(match, request):
            seen["url"] = request.full_url
            seen["auth"] = request.get_header("Authorization")
            seen["body"] = json.loads(request.data.decode("utf-8"))
            return Response('{"action":"play:Herz-Ass"}')

        with patch("schnapsen.llm_player.send", opener):
            action, failed = LlmPlayer(key=secret).propose(match)
        self.assertFalse(failed)
        self.assertEqual(action, "play:Herz-Ass")
        self.assertEqual(seen["auth"], "Bearer " + secret)
        self.assertEqual(seen["url"], "https://api.openai.com/v1/chat/completions")
        self.assertEqual(seen["body"]["model"], "gpt-6-sol")
        self.assertNotIn("temperature", seen["body"])
        schema = seen["body"]["response_format"]["json_schema"]["schema"]
        self.assertEqual(schema["properties"]["action"]["enum"], legal_action_ids(match))
        messages = seen["body"]["messages"]
        self.assertEqual(messages[0], {"role": "system", "content": SYSTEM})
        self.assertIn(RULES, messages[0]["content"])
        self.assertNotIn("Your cards:", messages[0]["content"])
        self.assertEqual(messages[1], {"role": "user", "content": jev_parts(match)[1]})
        self.assertIn("Herz Ass", messages[1]["content"])
        self.assertEqual("\n".join(item["content"] for item in messages).count(RULES), 1)
        self.assertEqual(seen["body"]["prompt_cache_key"], f"{id(match.deal)}:computer")

    def test_a_json_action_must_be_one_of_the_legal_ids(self):
        legal = ["play:Herz-Ass"]
        self.assertEqual(read_choice('{"action":"play:Herz-Ass"}', legal), "play:Herz-Ass")
        self.assertIsNone(read_choice('{"action":"play:Pik-Ass"}', legal))

    def test_action_id_token_and_label_are_accepted_when_unique(self):
        legal = ["play:Herz-Ass"]
        self.assertEqual(interpret_reply("play:Herz-Ass", legal), "play:Herz-Ass")
        self.assertEqual(interpret_reply('"play:Herz-Ass."', legal), "play:Herz-Ass")
        self.assertEqual(interpret_reply("Herz-Ass", legal), "play:Herz-Ass")
        self.assertEqual(interpret_reply("Herz Ass", legal), "play:Herz-Ass")

    def test_ambiguous_card_and_a_sentence_are_not_proposals(self):
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Herz", "König"), card("Herz", "Dame")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "König")],
        )
        legal = legal_action_ids(match)
        self.assertGreater(sum(item.endswith("Herz-König") or item.endswith(":Herz-König") for item in legal), 1)
        self.assertIsNone(interpret_reply("Herz König", legal))
        self.assertIsNone(interpret_reply("I play the ace of hearts.", legal))

    def test_a_failed_call_is_a_failure(self):
        match = self.match()

        def opener(match, request):
            raise urllib.error.URLError("down")

        with patch("schnapsen.llm_player.send", opener):
            action, failed = LlmPlayer(key="temp-chat-secret").propose(match)
        self.assertIsNone(action)
        self.assertTrue(failed)

    def test_a_random_turn_does_not_call_chatgpt(self):
        match = self.match()
        match.players = {"human": "human", "computer": "random"}
        called = []

        def opener(match, request):
            called.append(request)
            return Response("play:Herz-Ass")

        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(match, random_player=RandomPlayer(lambda hand: card("Herz", "Ass")))
        self.assertEqual(called, [])
        self.assertEqual(match.deal.current_trick[0][1], card("Herz", "Ass"))


class LlmTurnTests(unittest.TestCase):
    def follow_position(self):
        match = seated(
            "human",
            [card("Karo", "König")],
            [card("Karo", "Bube"), card("Herz", "Ass")],
            None,
            [],
        )
        match.deal.trump_card = None
        match.deal.trump_suit = "Herz"
        from schnapsen.engine import apply_action

        apply_action(match, "play:Karo-König")
        match.players["computer"] = "llm"
        return match

    def test_missing_chat_key_plays_nothing(self):
        match = self.follow_position()
        before = list(match.deal.current_trick)
        take_ai_turn(match, llm_player=LlmPlayer(key=""))
        self.assertEqual(match.notice, "missing-chat-key")
        self.assertEqual(match.deal.current_trick, before)
        self.assertEqual(match.deal.to_play, "computer")
        self.assertFalse(match.choice_replaced)

    def test_first_off_suit_reply_is_asked_again(self):
        match = self.follow_position()
        seen = []

        def reply(current):
            seen.append(list(current.deal.current_trick))
            if len(seen) == 1:
                return "Herz Ass"
            return "play:Karo-Bube"

        take_ai_turn(match, llm_player=LlmPlayer(key="present", reply=reply))
        self.assertEqual(len(seen), 2)
        self.assertEqual(seen[1], [("human", card("Karo", "König"))])
        self.assertEqual(match.deal.current_trick[-1][1], card("Karo", "Bube"))
        self.assertFalse(match.choice_replaced)
        self.assertIsNone(match.jev_exchange)

    def test_second_illegal_reply_uses_the_predetermined_action(self):
        match = self.follow_position()
        legal = sorted(legal_action_ids(match))
        take_ai_turn(match, llm_player=LlmPlayer(key="present", reply=lambda current: "Herz Ass"))
        self.assertTrue(match.choice_replaced)
        self.assertEqual(match.deal.current_trick[-1][1].token, legal[0].split(":")[-1])

    def test_a_failed_call_is_not_retried(self):
        match = self.follow_position()
        legal = sorted(legal_action_ids(match))
        calls = []

        def reply(current):
            calls.append(1)
            raise RuntimeError("down")

        take_ai_turn(match, llm_player=LlmPlayer(key="present", reply=reply))
        self.assertEqual(calls, [1])
        self.assertTrue(match.choice_replaced)
        self.assertEqual(match.deal.current_trick[-1][1].token, legal[0].split(":")[-1])

    def test_a_missing_chat_key_does_not_stop_jev(self):
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Karo", "König")],
            card("Herz", "Bube"),
            [card("Kreuz", "Ass"), card("Kreuz", "Zehner")],
        )

        class Client:
            def __init__(self):
                self.calls = []

            def system_one(self, state, questions):
                self.calls.append(state)
                return type("R", (), {"choices": {"play": type("C", (), {"choice": "play:Karo-König"})()}})()

        client = Client()
        with (
            patch("schnapsen.turn.read_api_key", return_value="present"),
            patch("schnapsen.turn.read_chat_api_key", return_value=""),
        ):
            take_ai_turn(match, client)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(match.deal.current_trick[0][1], card("Karo", "König"))

    def test_a_random_turn_plays_while_both_keys_are_missing(self):
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Karo", "König")],
            card("Herz", "Bube"),
            [card("Kreuz", "Ass")],
        )
        match.players = {"human": "random", "computer": "random"}
        with (
            patch("schnapsen.turn.read_api_key", return_value=""),
            patch("schnapsen.turn.read_chat_api_key", return_value=""),
        ):
            take_ai_turn(match, random_player=RandomPlayer(lambda hand: hand[0]))
        self.assertIsNone(match.notice)
        self.assertEqual(len(match.deal.current_trick), 1)


class ConversationTests(unittest.TestCase):
    def endgame(self):
        match = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König")],
            [card("Herz", "Ass"), card("Herz", "König")],
            None,
            [],
        )
        match.deal.trump_card = None
        match.deal.trump_suit = "Kreuz"
        match.players = {"human": "human", "computer": "llm"}
        return match

    def test_an_illegal_retry_sends_the_same_messages(self):
        match = LlmTurnTests().follow_position()
        bodies = []
        tricks = []

        def opener(match, request):
            bodies.append(json.loads(request.data.decode("utf-8")))
            tricks.append(list(match.deal.current_trick))
            if len(bodies) == 1:
                return Response("nope")
            return Response('{"action":"play:Karo-Bube"}')

        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(match, llm_player=LlmPlayer(key="temp-chat-secret"))
        self.assertEqual(len(bodies), 2)
        self.assertEqual(tricks[1], [("human", card("Karo", "König"))])
        self.assertEqual(bodies[1]["messages"], bodies[0]["messages"])
        self.assertEqual(match.deal.current_trick[-1][1], card("Karo", "Bube"))
        self.assertFalse(match.choice_replaced)

    def test_a_later_turn_keeps_the_prefix_and_the_accepted_reply(self):
        match = self.endgame()
        bodies = []
        reply = '{"action":"play:Herz-Ass"}'

        def opener(match, request):
            bodies.append(json.loads(request.data.decode("utf-8")))
            if len(bodies) == 1:
                return Response(reply)
            return Response('{"action":"play:Herz-König"}')

        player = LlmPlayer(key="temp-chat-secret")
        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(match, llm_player=player)
            self.assertTrue(apply_action(match, "play:Pik-Ass"))
            take_ai_turn(match, llm_player=player)
        self.assertEqual(bodies[1]["messages"][:2], bodies[0]["messages"])
        self.assertEqual(bodies[1]["messages"][2], {"role": "assistant", "content": reply})
        self.assertEqual(bodies[1]["messages"][3]["role"], "user")
        self.assertNotIn(RULES, bodies[1]["messages"][3]["content"])
        self.assertEqual(bodies[1]["prompt_cache_key"], bodies[0]["prompt_cache_key"])

    def test_a_replaced_turn_records_the_predetermined_action(self):
        match = self.endgame()
        fallback = sorted(legal_action_ids(match))[0]
        bodies = []

        def opener(match, request):
            bodies.append(json.loads(request.data.decode("utf-8")))
            if len(bodies) < 3:
                return Response("nope")
            return Response('{"action":"play:Herz-König"}')

        player = LlmPlayer(key="temp-chat-secret")
        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(match, llm_player=player)
            self.assertTrue(match.choice_replaced)
            self.assertTrue(apply_action(match, "play:Pik-Ass"))
            take_ai_turn(match, llm_player=player)
        self.assertEqual(bodies[0]["messages"], bodies[1]["messages"])
        self.assertNotIn("nope", json.dumps(bodies[0]["messages"]))
        assistant = bodies[2]["messages"][2]
        self.assertEqual(assistant, {"role": "assistant", "content": fallback})
        self.assertNotIn("nope", assistant["content"])

    def test_a_failed_call_records_the_predetermined_action(self):
        match = self.endgame()
        fallback = sorted(legal_action_ids(match))[0]
        bodies = []

        def opener(match, request):
            bodies.append(json.loads(request.data.decode("utf-8")))
            if len(bodies) == 1:
                raise urllib.error.URLError("down")
            return Response('{"action":"play:Herz-König"}')

        player = LlmPlayer(key="temp-chat-secret")
        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(match, llm_player=player)
            self.assertTrue(match.choice_replaced)
            self.assertEqual(len(bodies), 1)
            self.assertTrue(apply_action(match, "play:Pik-Ass"))
            take_ai_turn(match, llm_player=player)
        self.assertEqual(
            bodies[1]["messages"][2],
            {"role": "assistant", "content": fallback},
        )

    def test_two_llm_seats_do_not_share_a_hidden_card(self):
        match = seated(
            "computer",
            [card("Pik", "Ass"), card("Pik", "König")],
            [card("Herz", "Ass"), card("Karo", "Dame")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner"), card("Kreuz", "König")],
        )
        match.players = {"human": "llm", "computer": "llm"}
        bodies = []

        def opener(match, request):
            bodies.append(json.loads(request.data.decode("utf-8")))
            legal = bodies[-1]["response_format"]["json_schema"]["schema"]["properties"]["action"]["enum"]
            chosen = "play:Herz-Ass" if "play:Herz-Ass" in legal else legal[0]
            return Response(json.dumps({"action": chosen}))

        player = LlmPlayer(key="temp-chat-secret")
        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(match, llm_player=player)
            take_ai_turn(match, llm_player=player)
        self.assertNotEqual(bodies[0]["prompt_cache_key"], bodies[1]["prompt_cache_key"])
        self.assertNotIn("Karo Dame", json.dumps(bodies[1]))
        self.assertNotIn("Karo-Dame", json.dumps(bodies[1]))

    def test_the_next_deal_starts_a_new_conversation(self):
        match = self.endgame()
        bodies = []

        def opener(match, request):
            bodies.append(json.loads(request.data.decode("utf-8")))
            legal = bodies[-1]["response_format"]["json_schema"]["schema"]["properties"]["action"]["enum"]
            return Response(json.dumps({"action": legal[0]}))

        player = LlmPlayer(key="temp-chat-secret")
        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(match, llm_player=player)
            previous = bodies[0]["messages"][1]["content"]
            previous_key = bodies[0]["prompt_cache_key"]
            self.assertTrue(start_deal(match))
            match.players = {"human": "llm", "computer": "llm"}
            take_ai_turn(match, llm_player=player)
        fresh = bodies[1]
        self.assertEqual([item["role"] for item in fresh["messages"]], ["system", "user"])
        self.assertNotIn(previous, json.dumps(fresh["messages"]))
        self.assertNotEqual(fresh["prompt_cache_key"], previous_key)
        self.assertEqual("\n".join(item["content"] for item in fresh["messages"]).count(RULES), 1)

    def test_a_random_or_jev_turn_adds_no_llm_message(self):
        player = LlmPlayer(key="temp-chat-secret")
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Herz", "Ass")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner")],
        )
        match.players = {"human": "human", "computer": "random"}
        take_ai_turn(
            match,
            random_player=RandomPlayer(lambda hand: card("Herz", "Ass")),
            llm_player=player,
        )
        match.players = {"human": "jev", "computer": "random"}
        match.deal.to_play = "human"
        match.deal.phase = "play"

        class Client:
            def system_one(self, state, questions):
                return type("R", (), {"choices": {"play": type("C", (), {"choice": "play:Pik-Ass"})()}})()

        with patch("schnapsen.turn.read_api_key", return_value="present"):
            take_ai_turn(match, Client(), llm_player=player)
        self.assertEqual(len(player._threads), 0)

        seen = {}

        def opener(match, request):
            seen["body"] = json.loads(request.data.decode("utf-8"))
            return Response('{"action":"play:Herz-Ass"}')

        with patch("schnapsen.llm_player.send", opener):
            take_ai_turn(self.endgame(), llm_player=player)
        self.assertEqual([item["role"] for item in seen["body"]["messages"]], ["system", "user"])


class ConnectionTests(unittest.TestCase):
    def match(self):
        match = seated(
            "computer",
            [card("Pik", "Ass")],
            [card("Herz", "Ass")],
            card("Kreuz", "Ass"),
            [card("Kreuz", "Zehner")],
        )
        match.players = {"human": "llm", "computer": "llm"}
        return match

    def test_one_connection_lasts_for_the_match(self):
        made = []
        script = []

        class FakeConn:
            def __init__(self, host, port=None, **kwargs):
                self.closed = False
                self.calls = 0
                made.append(self)

            def request(self, method, path, body=None, headers=None):
                self.calls += 1
                payload = json.loads(body)
                self.payload = payload

            def getresponse(self):
                if script:
                    text = script.pop(0)
                else:
                    action = self.payload["response_format"]["json_schema"]["schema"]["properties"]["action"]["enum"][0]
                    text = json.dumps({"action": action})
                return Response(text)

            def close(self):
                self.closed = True

        player = LlmPlayer(key="temp-chat-secret")
        with patch("schnapsen.llm_player.http.client.HTTPSConnection", FakeConn):
            match = self.match()
            take_ai_turn(match, llm_player=player)
            take_ai_turn(match, llm_player=player)
            self.assertEqual(len(made), 1)
            self.assertEqual(made[0].calls, 2)
            self.assertFalse(made[0].closed)
            self.assertEqual(made[0].payload["model"], "gpt-6-sol")
            self.assertIn("prompt_cache_key", made[0].payload)

            retry = self.match()
            legal = sorted(legal_action_ids(retry))
            script[:] = ["nope", json.dumps({"action": legal[0]})]
            take_ai_turn(retry, llm_player=player)
            self.assertEqual(len(made), 2)
            self.assertEqual(made[1].calls, 2)

            later = self.match()
            take_ai_turn(later, llm_player=player)
            start_deal(later)
            later.players = {"human": "llm", "computer": "llm"}
            take_ai_turn(later, llm_player=player)
            self.assertEqual(len(made), 3)
            self.assertGreaterEqual(made[2].calls, 2)
            close_chat_connection(later)
            self.assertTrue(made[2].closed)
            follow = self.match()
            take_ai_turn(follow, llm_player=player)
            self.assertEqual(len(made), 4)
            self.assertIsNot(made[2], made[3])

            scripted = self.match()
            before = len(made)

            def reply(current):
                return sorted(legal_action_ids(current))[0]

            take_ai_turn(scripted, llm_player=LlmPlayer(reply=reply))
            self.assertEqual(len(made), before)

            jev_only = self.match()
            jev_only.players = {"human": "random", "computer": "jev"}

            class Live:
                made = []

                def __init__(self, **kwargs):
                    Live.made.append(self)

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

                def system_one(self, state, questions):
                    action = sorted(questions["play"].criteria)[0]
                    return SimpleNamespace(choices={"play": SimpleNamespace(choice=action)})

            with patch("typesafe_sdk.TypeSafeClient", Live):
                take_ai_turn(jev_only)
            self.assertEqual(len(made), before)
            self.assertEqual(len(Live.made), 1)

            both = self.match()
            both.players = {"human": "llm", "computer": "jev"}
            chat_before = len(made)
            with patch("typesafe_sdk.TypeSafeClient", Live):
                take_ai_turn(both, llm_player=player)
                take_ai_turn(both, llm_player=player)
            self.assertEqual(len(Live.made), 2)
            self.assertEqual(len(made), chat_before + 1)
            close_jev_client(both)
            close_chat_connection(both)
