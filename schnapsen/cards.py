"""The twenty-card Schnapsen pack."""

from dataclasses import dataclass

SUITS = ("Herz", "Karo", "Pik", "Kreuz")
RANKS = ("Ass", "Zehner", "König", "Dame", "Bube")
EYES = {"Ass": 11, "Zehner": 10, "König": 4, "Dame": 3, "Bube": 2}
RANK_VALUE = {"Ass": 5, "Zehner": 4, "König": 3, "Dame": 2, "Bube": 1}


@dataclass(frozen=True, order=True)
class Card:
    suit: str
    rank: str

    @property
    def eyes(self) -> int:
        return EYES[self.rank]

    @property
    def rank_value(self) -> int:
        return RANK_VALUE[self.rank]

    @property
    def label(self) -> str:
        return f"{self.suit} {self.rank}"

    @property
    def token(self) -> str:
        return f"{self.suit}-{self.rank}"


def full_pack() -> list[Card]:
    return [Card(suit, rank) for suit in SUITS for rank in RANKS]


def parse_card(token: str) -> Card | None:
    suit, separator, rank = token.partition("-")
    if not separator or suit not in SUITS or rank not in RANKS:
        return None
    return Card(suit, rank)
