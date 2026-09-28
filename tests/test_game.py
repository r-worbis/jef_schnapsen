"""Rules engine: pack, deal, tricks, marriages, and the match."""

import random
import unittest

from schnapsen.cards import EYES, RANKS, SUITS, Card, full_pack
from schnapsen.engine import (
    action_label,
    apply_action,
    build_deal,
    counting_eyes,
    legal_action_ids,
    match_with_deal,
    new_match,
    parse_action,
    record_game_points,
    start_deal,
)


def card(suit: str, rank: str) -> Card:
    return Card(suit, rank)


def snapshot(match):
    deal = match.deal
    return (
        tuple(item.label for item in deal.hands["human"]),
        tuple(item.label for item in deal.hands["computer"]),
        tuple(item.label for item in deal.talon),
        None if deal.trump_card is None else deal.trump_card.label,
        deal.closed,
        deal.phase,
        dict(match.points_needed),
        dict(match.bummerl),
    )


def scripted_deal(human, computer, trump, talon, leader="human", closed=False):
    trump_suit = trump.suit if trump is not None else "Herz"
    pack = [card("Herz", "Ass")] * 20
    match = match_with_deal("computer", full_pack())
    deal = match.deal
    deal.hands = {"human": list(human), "computer": list(computer)}
    deal.talon = list(talon)
    deal.trump_card = None if closed else trump
    deal.trump_suit = trump_suit
    deal.leader = leader
    deal.to_play = leader
    deal.closed = closed
    deal.current_trick = []
    deal.tricks = {"human": [], "computer": []}
    deal.marriage_eyes = {"human": 0, "computer": 0}
    deal.won_trick = {"human": False, "computer": False}
    deal.phase = "play"
    deal.closed_by = None
    return match


class PackTests(unittest.TestCase):
    def test_pack_has_each_card_once_and_the_eye_values(self):
        pack = full_pack()
        self.assertEqual(len(pack), 20)
        self.assertEqual(len(set(pack)), 20)
        for suit in SUITS:
            for rank in RANKS:
                self.assertIn(Card(suit, rank), pack)
        self.assertEqual([EYES[rank] for rank in ("Ass", "Zehner", "König", "Dame", "Bube")], [11, 10, 4, 3, 2])
        self.assertGreater(Card("Herz", "Ass").rank_value, Card("Herz", "Zehner").rank_value)
        self.assertGreater(Card("Herz", "Zehner").rank_value, Card("Herz", "König").rank_value)
        self.assertGreater(Card("Herz", "König").rank_value, Card("Herz", "Dame").rank_value)
        self.assertGreater(Card("Herz", "Dame").rank_value, Card("Herz", "Bube").rank_value)


class DealerTests(unittest.TestCase):
    def test_higher_card_deals(self):
        draw = [card("Pik", "Ass"), card("Pik", "Bube"), *full_pack()[2:]]
        deal = full_pack()
        match = new_match(scripted=[draw, deal])
        self.assertEqual(match.dealer, "human")

    def test_equal_ranks_are_redrawn(self):
        tied = [card("Herz", "Ass"), card("Karo", "Ass"), *full_pack()[2:]]
        decided = [card("Pik", "Bube"), card("Pik", "König"), *full_pack()[2:]]
        match = new_match(scripted=[tied, decided, full_pack()])
        self.assertEqual(match.dealer, "computer")

    def test_roles_swap_after_a_deal(self):
        draw = [card("Pik", "Ass"), card("Pik", "Bube"), *full_pack()[2:]]
        match = new_match(scripted=[draw, full_pack(), full_pack()])
        self.assertEqual(match.dealer, "human")
        record_game_points(match, "human", 1)
        self.assertEqual(match.dealer, "computer")
        start_deal(match)
        self.assertEqual(match.deal.to_play, "human")


class DealTests(unittest.TestCase):
    def test_opening_layout(self):
        pack = full_pack()
        deal = build_deal(pack, "computer")
        self.assertEqual(deal.hands["human"], [pack[0], pack[1], pack[2], pack[7], pack[8]])
        self.assertEqual(deal.hands["computer"], [pack[3], pack[4], pack[5], pack[9], pack[10]])
        self.assertEqual(deal.trump_card, pack[6])
        self.assertEqual(len(deal.talon), 9)
        self.assertEqual(deal.talon, pack[11:20])
        self.assertEqual(len(deal.hands["human"]), 5)
        self.assertEqual(len(deal.hands["computer"]), 5)


class TrickTests(unittest.TestCase):
    def test_discard_loses_and_trump_captures_while_the_talon_is_open(self):
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König")]
        trump = card("Herz", "Bube")
        human = [card("Karo", "Ass"), card("Pik", "Dame"), card("Pik", "König"), card("Pik", "Zehner"), card("Pik", "Bube")]
        computer = [card("Pik", "Ass"), card("Herz", "Zehner"), card("Karo", "König"), card("Karo", "Dame"), card("Karo", "Bube")]
        match = scripted_deal(human, computer, trump, talon)
        self.assertIn("play:Karo-Ass", legal_action_ids(match))
        self.assertTrue(apply_action(match, "play:Karo-Ass"))
        self.assertIn("play:Pik-Ass", legal_action_ids(match))
        self.assertIn("play:Herz-Zehner", legal_action_ids(match))
        self.assertIn("play:Karo-König", legal_action_ids(match))
        self.assertTrue(apply_action(match, "play:Pik-Ass"))
        self.assertTrue(apply_action(match, "seen"))
        self.assertEqual(match.deal.tricks["human"][-1][0], card("Karo", "Ass"))
        self.assertEqual(match.deal.to_play, "human")

        match = scripted_deal(human, computer, trump, talon)
        apply_action(match, "play:Karo-Ass")
        self.assertTrue(apply_action(match, "play:Herz-Zehner"))
        self.assertTrue(apply_action(match, "seen"))
        self.assertEqual(match.deal.tricks["computer"][-1][1], card("Herz", "Zehner"))

    def test_winner_draws_first_and_a_closed_or_empty_talon_deals_nothing(self):
        trump = card("Kreuz", "Ass")
        talon = [card("Karo", "Dame"), card("Karo", "König"), card("Kreuz", "König")]
        human = [card("Herz", "Ass"), card("Herz", "König")]
        computer = [card("Pik", "Ass"), card("Pik", "König")]
        match = scripted_deal(human, computer, trump, talon)
        apply_action(match, "play:Herz-Ass")
        apply_action(match, "play:Pik-Ass")
        apply_action(match, "seen")
        self.assertEqual(match.deal.hands["human"][-1], card("Karo", "Dame"))
        self.assertEqual(match.deal.hands["computer"][-1], card("Karo", "König"))
        self.assertEqual(match.deal.trump_card, trump)

        match = scripted_deal(human, computer, trump, [card("Karo", "Dame")])
        apply_action(match, "play:Herz-Ass")
        apply_action(match, "play:Pik-Ass")
        apply_action(match, "seen")
        self.assertIn(card("Karo", "Dame"), match.deal.hands["human"])
        self.assertIn(trump, match.deal.hands["computer"])
        self.assertIsNone(match.deal.trump_card)

        closed = scripted_deal(human, computer, None, [], closed=True)
        closed.deal.trump_suit = "Herz"
        before = (len(closed.deal.hands["human"]), len(closed.deal.hands["computer"]))
        apply_action(closed, "play:Herz-Ass")
        apply_action(closed, "play:Pik-Ass")
        apply_action(closed, "seen")
        self.assertEqual(
            (len(closed.deal.hands["human"]), len(closed.deal.hands["computer"])),
            (before[0] - 1, before[1] - 1),
        )

    def test_must_beat_the_led_suit_and_suit_before_trump(self):
        human = [card("Karo", "König")]
        computer = [card("Karo", "Ass"), card("Karo", "Bube"), card("Herz", "Ass")]
        match = scripted_deal(human, computer, None, [], leader="human", closed=True)
        match.deal.trump_suit = "Herz"
        apply_action(match, "play:Karo-König")
        legal = legal_action_ids(match)
        self.assertEqual(legal, ["play:Karo-Ass"])
        before = snapshot(match)
        self.assertFalse(apply_action(match, "play:Herz-Ass"))
        self.assertFalse(apply_action(match, "play:Karo-Bube"))
        self.assertEqual(snapshot(match), before)

        computer = [card("Karo", "Bube"), card("Herz", "Ass")]
        match = scripted_deal([card("Karo", "König")], computer, None, [], closed=True)
        match.deal.trump_suit = "Herz"
        apply_action(match, "play:Karo-König")
        self.assertEqual(legal_action_ids(match), ["play:Karo-Bube"])
        self.assertFalse(apply_action(match, "play:Herz-Ass"))


class AcknowledgeTests(unittest.TestCase):
    def test_computer_answer_stays_until_seen_human_follow_does_not(self):
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König")]
        trump = card("Herz", "Bube")
        human = [card("Karo", "Ass"), card("Pik", "Dame")]
        computer = [card("Pik", "Ass"), card("Karo", "König")]
        match = scripted_deal(human, computer, trump, talon)
        apply_action(match, "play:Karo-Ass")
        apply_action(match, "play:Karo-König")
        self.assertEqual(
            match.deal.current_trick,
            [("human", card("Karo", "Ass")), ("computer", card("Karo", "König"))],
        )
        self.assertEqual(counting_eyes(match.deal, "human"), 0)
        self.assertEqual(counting_eyes(match.deal, "computer"), 0)
        self.assertEqual(tuple(item.label for item in match.deal.talon), tuple(item.label for item in talon))
        self.assertEqual(match.deal.to_play, "human")
        self.assertEqual(match.deal.phase, "acknowledge")
        self.assertEqual(match.deal.leader, "human")
        self.assertEqual(legal_action_ids(match), ["seen"])

        follow = scripted_deal(
            [card("Karo", "König")],
            [card("Karo", "Ass")],
            trump,
            talon,
            leader="computer",
        )
        apply_action(follow, "play:Karo-Ass")
        apply_action(follow, "play:Karo-König")
        self.assertEqual(follow.deal.current_trick, [])
        self.assertEqual(follow.deal.tricks["computer"][-1], [card("Karo", "Ass"), card("Karo", "König")])
        self.assertNotEqual(follow.deal.phase, "acknowledge")
        self.assertFalse(apply_action(follow, "seen"))

    def test_seen_awards_draws_and_waits_on_last_trick_and_sixty_six(self):
        idle = scripted_deal(
            [card("Karo", "Ass")],
            [card("Pik", "Ass")],
            card("Herz", "Bube"),
            [card("Kreuz", "Ass")],
        )
        before = snapshot(idle)
        self.assertFalse(apply_action(idle, "seen"))
        self.assertEqual(snapshot(idle), before)

        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König")]
        trump = card("Herz", "Bube")
        human = [card("Karo", "Ass"), card("Pik", "Dame")]
        computer = [card("Karo", "König"), card("Pik", "Ass")]
        match = scripted_deal(human, computer, trump, talon)
        apply_action(match, "play:Karo-Ass")
        apply_action(match, "play:Karo-König")
        self.assertTrue(apply_action(match, "seen"))
        self.assertEqual(match.deal.tricks["human"][-1], [card("Karo", "Ass"), card("Karo", "König")])
        self.assertEqual(counting_eyes(match.deal, "human"), 15)
        self.assertEqual(match.deal.hands["human"][-1], card("Kreuz", "Ass"))
        self.assertEqual(match.deal.hands["computer"][-1], card("Kreuz", "Zehner"))
        self.assertEqual(match.deal.to_play, "human")

        prior = [
            card("Herz", "Ass"),
            card("Herz", "Zehner"),
            card("Karo", "Zehner"),
            card("Pik", "Zehner"),
            card("Kreuz", "Zehner"),
            card("Herz", "König"),
        ]
        self.assertEqual(sum(item.eyes for item in prior), 55)
        waiting = scripted_deal(
            [card("Karo", "Bube"), card("Pik", "Dame")],
            [card("Karo", "Ass"), card("Pik", "König")],
            None,
            [],
            closed=True,
        )
        waiting.deal.trump_suit = "Herz"
        waiting.deal.tricks["computer"].append(prior)
        waiting.deal.won_trick["computer"] = True
        apply_action(waiting, "play:Karo-Bube")
        apply_action(waiting, "play:Karo-Ass")
        self.assertEqual(counting_eyes(waiting.deal, "computer"), 55)
        self.assertEqual(waiting.deal.phase, "acknowledge")
        apply_action(waiting, "seen")
        self.assertGreaterEqual(counting_eyes(waiting.deal, "computer"), 66)
        self.assertEqual(waiting.deal.winner, "computer")
        self.assertNotIn("declare", legal_action_ids(waiting))
        self.assertNotIn("continue", legal_action_ids(waiting))

        last = scripted_deal([card("Herz", "König")], [card("Pik", "König")], None, [])
        last.deal.trump_suit = "Herz"
        last.deal.trump_card = None
        last.deal.tricks["computer"].append(
            [card("Herz", "Ass"), card("Karo", "Ass"), card("Pik", "Ass")]
        )
        last.deal.won_trick["computer"] = True
        apply_action(last, "play:Herz-König")
        apply_action(last, "play:Pik-König")
        self.assertEqual(last.deal.phase, "acknowledge")
        self.assertIsNone(last.deal.winner)
        apply_action(last, "seen")
        self.assertEqual(last.deal.winner, "human")
        self.assertEqual(last.deal.game_points, 1)


class MarriageTests(unittest.TestCase):
    def test_trump_marriage_plain_marriage_and_no_eyes_without_a_trick(self):
        trump = card("Herz", "Bube")
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König"), card("Kreuz", "Dame")]
        human = [card("Herz", "König"), card("Herz", "Dame"), card("Karo", "König"), card("Karo", "Dame"), card("Pik", "König")]
        computer = [card("Herz", "Ass"), card("Pik", "Bube"), card("Karo", "Ass"), card("Karo", "Bube"), card("Kreuz", "Bube")]
        match = scripted_deal(human, computer, trump, talon)
        self.assertIn("marry:Herz:Herz-König", legal_action_ids(match))
        self.assertTrue(apply_action(match, "marry:Herz:Herz-König"))
        self.assertEqual(match.deal.marriage_eyes["human"], 40)
        self.assertEqual(match.deal.current_trick[0][1], card("Herz", "König"))
        self.assertEqual(counting_eyes(match.deal, "human"), 0)
        apply_action(match, "play:Pik-Bube")
        apply_action(match, "seen")
        self.assertTrue(match.deal.won_trick["human"])
        self.assertEqual(counting_eyes(match.deal, "human"), 40 + 4 + 2)

        match = scripted_deal(human, computer, trump, talon)
        apply_action(match, "marry:Karo:Karo-Dame")
        self.assertEqual(match.deal.marriage_eyes["human"], 20)
        apply_action(match, "play:Karo-Ass")
        self.assertEqual(counting_eyes(match.deal, "human"), 0)

        fresh = scripted_deal(human, computer, trump, talon)
        self.assertIn("marry:Herz:Herz-König", legal_action_ids(fresh))


class ExchangeAndCloseTests(unittest.TestCase):
    def test_exchange_with_one_face_down_card_and_refusals(self):
        trump = card("Herz", "Ass")
        human = [card("Herz", "Bube"), card("Karo", "Ass"), card("Karo", "König"), card("Pik", "Dame"), card("Pik", "König")]
        computer = [card("Karo", "Dame"), card("Karo", "Bube"), card("Pik", "Ass"), card("Pik", "Bube"), card("Kreuz", "Ass")]
        match = scripted_deal(human, computer, trump, [card("Kreuz", "Zehner")])
        self.assertIn("exchange:Karo-Ass", legal_action_ids(match))
        self.assertTrue(apply_action(match, "exchange:Karo-Ass"))
        self.assertEqual(match.deal.trump_card, card("Herz", "Bube"))
        self.assertIn(card("Herz", "Ass"), match.deal.hands["human"])
        self.assertNotIn(card("Herz", "Bube"), match.deal.hands["human"])
        self.assertEqual(match.deal.current_trick[0][1], card("Karo", "Ass"))

        drawn = scripted_deal(human, computer, None, [])
        drawn.deal.trump_suit = "Herz"
        before = snapshot(drawn)
        self.assertFalse(apply_action(drawn, "exchange:Karo-Ass"))
        self.assertEqual(snapshot(drawn), before)

        closed = scripted_deal(human, computer, trump, [card("Kreuz", "Zehner"), card("Kreuz", "König")], closed=True)
        closed.deal.trump_suit = "Herz"
        before = snapshot(closed)
        self.assertFalse(apply_action(closed, "exchange:Karo-Ass"))
        self.assertEqual(snapshot(closed), before)

    def test_close_freezes_opponent_eyes_and_refuses_the_last_face_down_card(self):
        trump = card("Pik", "Ass")
        human = [card("Herz", "Ass"), card("Herz", "König"), card("Karo", "König"), card("Karo", "Dame"), card("Kreuz", "König")]
        computer = [card("Karo", "Ass"), card("Karo", "Bube"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube")]
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "Dame")]
        match = scripted_deal(human, computer, trump, talon)
        match.deal.tricks["computer"].append(
            [card("Herz", "Zehner"), card("Herz", "Dame"), card("Karo", "Zehner"), card("Pik", "Zehner")]
        )
        match.deal.won_trick["computer"] = True
        self.assertEqual(counting_eyes(match.deal, "computer"), 33)
        self.assertTrue(apply_action(match, "close:Herz-Ass"))
        self.assertTrue(match.deal.closed)
        self.assertIsNone(match.deal.trump_card)
        self.assertEqual(match.deal.talon, [])
        self.assertEqual(match.deal.opponent_eyes_at_close, 33)
        match.deal.tricks["computer"].append([card("Kreuz", "Bube"), card("Pik", "Zehner")])
        self.assertGreater(counting_eyes(match.deal, "computer"), 33)
        closer_win = scripted_deal([card("Kreuz", "König")], [card("Pik", "Bube")], None, [], closed=True)
        closer_win.deal.trump_suit = "Pik"
        closer_win.deal.closed_by = "human"
        closer_win.deal.opponent_trickless_at_close = False
        closer_win.deal.opponent_eyes_at_close = 33
        closer_win.deal.won_trick["computer"] = True
        closer_win.deal.marriage_eyes["human"] = 40
        closer_win.deal.tricks["human"].append(
            [card("Herz", "Ass"), card("Herz", "Zehner"), card("Herz", "König"), card("Karo", "Ass")]
        )
        closer_win.deal.won_trick["human"] = True
        apply_action(closer_win, "play:Kreuz-König")
        apply_action(closer_win, "play:Pik-Bube")
        apply_action(closer_win, "seen")
        self.assertEqual(closer_win.deal.game_points, 1)
        self.assertEqual(closer_win.deal.winner, "human")

        blocked = scripted_deal(human, computer, trump, [card("Kreuz", "Ass")])
        before = snapshot(blocked)
        self.assertNotIn("close:Herz-Ass", legal_action_ids(blocked))
        self.assertFalse(apply_action(blocked, "close:Herz-Ass"))
        self.assertEqual(snapshot(blocked), before)


class ScoringTests(unittest.TestCase):
    def _finish_at_sixty_six(self, human_prior, computer_prior):
        match = scripted_deal(
            [card("Pik", "König"), card("Kreuz", "Bube")],
            [card("Pik", "Dame"), card("Kreuz", "Dame")],
            card("Herz", "Zehner"),
            [card("Kreuz", "Ass"), card("Kreuz", "König")],
        )
        if human_prior:
            match.deal.tricks["human"].append(human_prior)
            match.deal.won_trick["human"] = True
        if computer_prior:
            match.deal.tricks["computer"].append(computer_prior)
            match.deal.won_trick["computer"] = True
        apply_action(match, "play:Pik-König")
        apply_action(match, "play:Pik-Dame")
        apply_action(match, "seen")
        self.assertNotIn("declare", legal_action_ids(match))
        self.assertNotIn("continue", legal_action_ids(match))
        return match

    def test_declaration_thresholds_false_declaration_closer_failure_and_last_trick(self):
        sixty_six = [
            card("Herz", "Zehner"), card("Karo", "Zehner"), card("Pik", "Zehner"), card("Kreuz", "Zehner"),
            card("Herz", "König"), card("Karo", "König"), card("Pik", "König"), card("Kreuz", "König"),
            card("Herz", "Dame"), card("Karo", "Dame"),
            card("Herz", "Bube"), card("Karo", "Bube"),
        ]
        self.assertEqual(sum(item.eyes for item in sixty_six), 66)
        no_trick = self._finish_at_sixty_six(sixty_six, [])
        self.assertEqual(no_trick.deal.game_points, 3)
        self.assertEqual(no_trick.deal.winner, "human")

        thirty_three = [card("Herz", "Ass"), card("Karo", "Ass"), card("Pik", "Ass")]
        self.assertEqual(sum(item.eyes for item in thirty_three), 33)
        high = self._finish_at_sixty_six(sixty_six, thirty_three)
        self.assertEqual(high.deal.game_points, 1)

        low = [card("Karo", "Dame"), card("Karo", "Bube")]
        with_trick = self._finish_at_sixty_six(sixty_six, low)
        self.assertEqual(with_trick.deal.game_points, 2)

        prior = [
            card("Herz", "Ass"), card("Herz", "Zehner"), card("Karo", "Zehner"),
            card("Pik", "Zehner"), card("Kreuz", "Zehner"), card("Herz", "König"),
        ]
        self.assertEqual(sum(item.eyes for item in prior), 55)
        trump = card("Herz", "Bube")
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "König"), card("Kreuz", "Dame")]
        human = [card("Herz", "König"), card("Herz", "Dame"), card("Karo", "Ass"), card("Pik", "König"), card("Pik", "Dame")]
        computer = [card("Herz", "Ass"), card("Pik", "Bube"), card("Karo", "Bube"), card("Kreuz", "Bube"), card("Pik", "Ass")]
        married = scripted_deal(human, computer, trump, talon)
        married.deal.tricks["human"].append(prior)
        married.deal.won_trick["human"] = True
        self.assertNotIn("marry-declare:Herz", legal_action_ids(married))
        self.assertTrue(apply_action(married, "marry:Herz:Herz-König"))
        self.assertEqual(married.deal.winner, "human")
        self.assertEqual(married.deal.game_points, 3)
        self.assertEqual(married.deal.current_trick, [])
        self.assertIn(card("Herz", "König"), married.deal.hands["human"])

        closer = scripted_deal([card("Herz", "Ass")], [card("Pik", "Ass")], None, [], closed=True)
        closer.deal.trump_suit = "Herz"
        closer.deal.closed_by = "human"
        closer.deal.opponent_trickless_at_close = True
        closer.deal.opponent_eyes_at_close = 0
        apply_action(closer, "play:Herz-Ass")
        apply_action(closer, "play:Pik-Ass")
        apply_action(closer, "seen")
        self.assertEqual(closer.deal.winner, "computer")
        self.assertEqual(closer.deal.game_points, 3)

        closer = scripted_deal([card("Herz", "Ass")], [card("Pik", "Ass")], None, [], closed=True)
        closer.deal.trump_suit = "Herz"
        closer.deal.closed_by = "human"
        closer.deal.opponent_trickless_at_close = False
        closer.deal.opponent_eyes_at_close = 20
        closer.deal.won_trick["computer"] = True
        apply_action(closer, "play:Herz-Ass")
        apply_action(closer, "play:Pik-Ass")
        apply_action(closer, "seen")
        self.assertEqual(closer.deal.winner, "computer")
        self.assertEqual(closer.deal.game_points, 2)

        last = scripted_deal([card("Herz", "König")], [card("Pik", "König")], None, [])
        last.deal.trump_suit = "Herz"
        last.deal.trump_card = None
        last.deal.tricks["computer"].append(thirty_three)
        last.deal.won_trick["computer"] = True
        apply_action(last, "play:Herz-König")
        apply_action(last, "play:Pik-König")
        apply_action(last, "seen")
        self.assertEqual(last.deal.winner, "human")
        self.assertEqual(last.deal.game_points, 1)

    def test_bummerl_countdown_schneider_match_and_no_carry(self):
        match = match_with_deal("human", full_pack())
        match.points_needed["human"] = 4
        record_game_points(match, "human", 2)
        self.assertEqual(match.points_needed["human"], 2)
        self.assertEqual(match.bummerl["computer"], 0)

        match = match_with_deal("human", full_pack())
        record_game_points(match, "human", 3)
        record_game_points(match, "human", 3)
        record_game_points(match, "human", 3)
        self.assertEqual(match.points_needed["human"], 0)
        self.assertEqual(match.points_needed["computer"], 7)
        self.assertEqual(match.bummerl["computer"], 2)
        self.assertEqual(match.match_winner, "human")

        match = match_with_deal("human", full_pack())
        match.bummerl["computer"] = 1
        match.points_needed["human"] = 1
        match.points_needed["computer"] = 4
        record_game_points(match, "human", 1)
        self.assertEqual(match.bummerl["computer"], 2)
        self.assertEqual(match.match_winner, "human")

        match = match_with_deal("computer", full_pack())
        match.points_needed["human"] = 2
        match.points_needed["computer"] = 5
        record_game_points(match, "human", 3)
        self.assertEqual(match.points_needed["human"], 7)
        self.assertEqual(match.points_needed["computer"], 7)
        self.assertEqual(match.bummerl["computer"], 1)
        self.assertIsNone(match.match_winner)


class CompoundActionTests(unittest.TestCase):
    def test_illegal_id_is_refused_and_a_legal_id_applies_only_its_parts(self):
        trump = card("Herz", "Zehner")
        human = [card("Herz", "Bube"), card("Herz", "Ass"), card("Karo", "König"), card("Karo", "Dame"), card("Kreuz", "König")]
        computer = [card("Karo", "Ass"), card("Karo", "Bube"), card("Pik", "König"), card("Pik", "Dame"), card("Pik", "Bube")]
        talon = [card("Kreuz", "Ass"), card("Kreuz", "Zehner"), card("Kreuz", "Dame"), card("Kreuz", "Bube")]
        match = scripted_deal(human, computer, trump, talon)
        before = snapshot(match)
        self.assertFalse(apply_action(match, "play:No-Such"))
        self.assertFalse(apply_action(match, "close:Kreuz-Ass"))
        self.assertEqual(snapshot(match), before)

        self.assertTrue(apply_action(match, "exchange:Herz-Ass"))
        self.assertEqual(match.deal.trump_card, card("Herz", "Bube"))
        self.assertFalse(match.deal.closed)
        self.assertIn(card("Herz", "Zehner"), match.deal.hands["human"])
        self.assertEqual(match.deal.current_trick, [("human", card("Herz", "Ass"))])

        match = scripted_deal(human, computer, trump, talon)
        self.assertTrue(apply_action(match, "close:Herz-Ass"))
        self.assertTrue(match.deal.closed)
        self.assertIsNone(match.deal.trump_card)
        self.assertIn(card("Herz", "Bube"), match.deal.hands["human"])
        self.assertNotIn(card("Herz", "Zehner"), match.deal.hands["human"])

        match = scripted_deal(human, computer, trump, talon)
        self.assertTrue(apply_action(match, "exchange-close:Herz-Ass"))
        self.assertTrue(match.deal.closed)
        self.assertIn(card("Herz", "Zehner"), match.deal.hands["human"])
        self.assertNotIn(card("Herz", "Bube"), match.deal.hands["human"])
        self.assertEqual(match.deal.current_trick, [("human", card("Herz", "Ass"))])


class ActionLabelTests(unittest.TestCase):
    def test_ids_parse_the_same_and_labels_are_german(self):
        self.assertEqual(parse_action("next-deal").kind, "next-deal")
        self.assertEqual(action_label("next-deal"), "Das nächste Blatt geben")
        self.assertEqual(parse_action("seen").kind, "seen")
        self.assertEqual(action_label("seen"), "Gesehen")
        play = parse_action("play:Herz-Ass")
        self.assertEqual(play.kind, "play")
        self.assertEqual(play.card, card("Herz", "Ass"))
        self.assertEqual(action_label("play:Herz-Ass"), "Herz Ass spielen")


if __name__ == "__main__":
    unittest.main()
