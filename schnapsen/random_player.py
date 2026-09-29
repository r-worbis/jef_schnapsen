"""A random player. It proposes one card from its hand and does not apply it."""

import random

from schnapsen.cards import Card
from schnapsen.engine import Match


class RandomPlayer:
    def __init__(self, choose=None) -> None:
        self.choose = choose or random.Random().choice

    def propose(self, match: Match) -> str:
        deal = match.deal
        assert deal is not None
        hand = list(deal.hands[deal.to_play])
        card: Card = self.choose(hand)
        return f"play:{card.token}"
