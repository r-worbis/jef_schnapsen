"""Deal, play, and score a weiches Schnapsen match."""

import random
from dataclasses import dataclass, field

from schnapsen.cards import Card, full_pack, parse_card

Seat = str
SEATS = ("human", "computer")

_PLAY_HEADS = {
    "play": (False, False, False),
    "exchange": (True, False, False),
    "close": (False, True, False),
    "exchange-close": (True, True, False),
    "marry": (False, False, True),
    "exchange-marry": (True, False, True),
    "close-marry": (False, True, True),
    "exchange-close-marry": (True, True, True),
}
def other(seat: Seat) -> Seat:
    return "computer" if seat == "human" else "human"


class DeckSource:
    """Shuffles with an injected random source, or yields scripted packs in order."""

    def __init__(self, rng: random.Random, scripted: list[list[Card]] | None = None) -> None:
        self.rng = rng
        self.scripted = list(scripted) if scripted is not None else None

    def draw_pack(self) -> list[Card]:
        if self.scripted is not None:
            return list(self.scripted.pop(0))
        cards = full_pack()
        self.rng.shuffle(cards)
        return cards


@dataclass
class LastAction:
    seat: Seat
    exchange: bool = False
    took: str | None = None
    closed: bool = False
    marriage: str | None = None
    card: str | None = None
    declared: bool = False
    continued: bool = False


@dataclass
class Deal:
    hands: dict[Seat, list[Card]]
    talon: list[Card]
    trump_card: Card | None
    trump_suit: str
    leader: Seat
    to_play: Seat
    closed: bool = False
    closed_by: Seat | None = None
    opponent_eyes_at_close: int | None = None
    opponent_trickless_at_close: bool | None = None
    current_trick: list[tuple[Seat, Card]] = field(default_factory=list)
    tricks: dict[Seat, list[list[Card]]] = field(
        default_factory=lambda: {"human": [], "computer": []}
    )
    marriage_eyes: dict[Seat, int] = field(default_factory=lambda: {"human": 0, "computer": 0})
    won_trick: dict[Seat, bool] = field(default_factory=lambda: {"human": False, "computer": False})
    phase: str = "play"
    winner: Seat | None = None
    game_points: int | None = None
    last_action: LastAction | None = None
    computer_action: LastAction | None = None


@dataclass
class JevExchange:
    rules: str
    cards: str
    answers: list[str] = field(default_factory=list)
    failed: bool = False


@dataclass
class Match:
    source: DeckSource
    dealer: Seat = "human"
    points_needed: dict[Seat, int] = field(
        default_factory=lambda: {"human": 7, "computer": 7}
    )
    bummerl: dict[Seat, int] = field(default_factory=lambda: {"human": 0, "computer": 0})
    deal: Deal | None = None
    match_winner: Seat | None = None
    notice: str | None = None
    choice_replaced: bool = False
    jev_exchange: JevExchange | None = None


@dataclass
class Plan:
    kind: str
    exchange: bool = False
    close: bool = False
    marriage: str | None = None
    card: Card | None = None


def new_match(
    rng: random.Random | None = None,
    scripted: list[list[Card]] | None = None,
) -> Match:
    source = DeckSource(rng or random.Random(), scripted)
    match = Match(source=source)
    _select_dealer(match)
    start_deal(match)
    return match


def match_with_deal(dealer: Seat, pack: list[Card]) -> Match:
    match = Match(source=DeckSource(random.Random()))
    match.dealer = dealer
    match.deal = build_deal(pack, dealer)
    return match


def _select_dealer(match: Match) -> None:
    while True:
        pack = match.source.draw_pack()
        human_card, computer_card = pack[0], pack[1]
        if human_card.rank_value != computer_card.rank_value:
            match.dealer = (
                "human" if human_card.rank_value > computer_card.rank_value else "computer"
            )
            return


def start_deal(match: Match) -> bool:
    if match.match_winner is not None:
        return False
    match.deal = build_deal(match.source.draw_pack(), match.dealer)
    match.notice = None
    match.choice_replaced = False
    return True


def build_deal(pack: list[Card], dealer: Seat) -> Deal:
    if len(pack) != 20:
        raise ValueError("a deal uses 20 cards")
    forehand = other(dealer)
    return Deal(
        hands={
            forehand: [pack[0], pack[1], pack[2], pack[7], pack[8]],
            dealer: [pack[3], pack[4], pack[5], pack[9], pack[10]],
        },
        talon=list(pack[11:20]),
        trump_card=pack[6],
        trump_suit=pack[6].suit,
        leader=forehand,
        to_play=forehand,
    )


def cards_to_draw(deal: Deal) -> int:
    return len(deal.talon) + (1 if deal.trump_card is not None else 0)


def stock_open(deal: Deal) -> bool:
    return not deal.closed and cards_to_draw(deal) > 0


def counting_eyes(deal: Deal, seat: Seat) -> int:
    eyes = sum(card.eyes for trick in deal.tricks[seat] for card in trick)
    if deal.won_trick[seat]:
        eyes += deal.marriage_eyes[seat]
    return eyes


def can_exchange(deal: Deal, seat: Seat) -> bool:
    if deal.closed or deal.trump_card is None:
        return False
    return Card(deal.trump_suit, "Bube") in deal.hands[seat]


def can_close(deal: Deal, seat: Seat) -> bool:
    if deal.closed or deal.trump_card is None or deal.current_trick:
        return False
    if deal.to_play != seat:
        return False
    return len(deal.talon) >= 2


def trick_points(trickless: bool, eyes: int) -> int:
    if trickless:
        return 3
    if eyes <= 32:
        return 2
    return 1


def parse_action(action_id: str) -> Plan | None:
    if action_id == "seen":
        return Plan(kind="seen")
    if action_id == "next-deal":
        return Plan(kind="next-deal")
    head, separator, rest = action_id.partition(":")
    if not separator:
        return None
    if head not in _PLAY_HEADS:
        return None
    exchange, close, marry = _PLAY_HEADS[head]
    if marry:
        suit, sep, token = rest.partition(":")
        card = parse_card(token) if sep else None
        if card is None:
            return None
        return Plan(kind="play", exchange=exchange, close=close, marriage=suit, card=card)
    card = parse_card(rest)
    if card is None or ":" in rest:
        return None
    return Plan(kind="play", exchange=exchange, close=close, card=card)


def action_label(action_id: str) -> str:
    plan = parse_action(action_id)
    if plan is None:
        return action_id
    if plan.kind == "seen":
        return "Gesehen"
    if plan.kind == "next-deal":
        return "Das nächste Blatt geben"
    parts: list[str] = []
    if plan.exchange:
        parts.append("Den Trumpf-Buben tauschen")
    if plan.close:
        parts.append("Den Talon zudrehen")
    if plan.marriage and plan.card is not None:
        parts.append(f"Die {plan.marriage}-Hochzeit ansagen und {plan.card.label} ausspielen")
    elif plan.card is not None:
        parts.append(f"{plan.card.label} spielen")
    return ", dann ".join(parts)


def legal_action_ids(match: Match) -> list[str]:
    deal = match.deal
    if deal is None:
        return []
    if deal.phase == "ended":
        return [] if match.match_winner else ["next-deal"]
    if deal.phase == "acknowledge":
        return ["seen"]
    return [action_id for action_id in _candidates(deal) if is_legal(match, action_id)]


def is_legal(match: Match, action_id: str) -> bool:
    plan = parse_action(action_id)
    deal = match.deal
    if plan is None or deal is None:
        return False
    if plan.kind == "next-deal":
        return deal.phase == "ended" and match.match_winner is None
    if deal.phase == "ended":
        return False
    seat = deal.to_play
    if plan.kind == "seen":
        return deal.phase == "acknowledge"
    if deal.phase != "play":
        return False
    leading = not deal.current_trick
    if plan.close and (not leading or not can_close(deal, seat)):
        return False
    if plan.exchange and not can_exchange(deal, seat):
        return False
    if not leading and (plan.close or plan.marriage):
        return False
    hand = _projected_hand(deal, seat, plan.exchange)
    if plan.card is None or plan.card not in hand:
        return False
    if plan.marriage:
        if not leading or not _holds_marriage(hand, plan.marriage):
            return False
        pair = {Card(plan.marriage, "König"), Card(plan.marriage, "Dame")}
        if plan.card not in pair:
            return False
    if not leading:
        lead_card = deal.current_trick[0][1]
        allowed = _legal_follow(hand, lead_card, deal.trump_suit, not stock_open(deal))
        if plan.card not in allowed:
            return False
    return True


def apply_action(match: Match, action_id: str) -> bool:
    if not is_legal(match, action_id):
        return False
    plan = parse_action(action_id)
    assert plan is not None
    _execute(match, plan)
    return True


def record_game_points(match: Match, winner: Seat, points: int) -> None:
    loser = other(winner)
    match.points_needed[winner] = max(0, match.points_needed[winner] - points)
    deal = match.deal
    if deal is not None:
        deal.phase = "ended"
        deal.winner = winner
        deal.game_points = points
    if match.points_needed[winner] == 0:
        charge = 2 if match.points_needed[loser] == 7 else 1
        match.bummerl[loser] += charge
        if match.bummerl[loser] >= 2:
            match.match_winner = winner
        else:
            match.points_needed = {"human": 7, "computer": 7}
    match.dealer = other(match.dealer)


def _candidates(deal: Deal) -> list[str]:
    seat = deal.to_play
    leading = not deal.current_trick
    exchanges = (False, True) if can_exchange(deal, seat) else (False,)
    closes = (False, True) if leading and can_close(deal, seat) else (False,)
    ids: list[str] = []
    for exchange in exchanges:
        for close in closes:
            hand = _projected_hand(deal, seat, exchange)
            prefix = _prefix(exchange, close)
            if leading:
                for suit in _marriage_suits(hand):
                    for rank in ("König", "Dame"):
                        ids.append(f"{prefix}marry:{suit}:{Card(suit, rank).token}")
                for card in hand:
                    ids.append(_play_id(exchange, close, card))
            else:
                lead_card = deal.current_trick[0][1]
                allowed = _legal_follow(hand, lead_card, deal.trump_suit, not stock_open(deal))
                for card in allowed:
                    ids.append(_play_id(exchange, close, card))
    return ids


def _play_id(exchange: bool, close: bool, card: Card) -> str:
    if exchange and close:
        return f"exchange-close:{card.token}"
    if exchange:
        return f"exchange:{card.token}"
    if close:
        return f"close:{card.token}"
    return f"play:{card.token}"


def _prefix(exchange: bool, close: bool) -> str:
    if exchange and close:
        return "exchange-close-"
    if exchange:
        return "exchange-"
    if close:
        return "close-"
    return ""


def _projected_hand(deal: Deal, seat: Seat, exchange: bool) -> list[Card]:
    hand = list(deal.hands[seat])
    if not exchange or deal.trump_card is None:
        return hand
    bube = Card(deal.trump_suit, "Bube")
    return [card for card in hand if card != bube] + [deal.trump_card]


def _marriage_suits(hand: list[Card]) -> list[str]:
    return [suit for suit in ("Herz", "Karo", "Pik", "Kreuz") if _holds_marriage(hand, suit)]


def _holds_marriage(hand: list[Card], suit: str | None) -> bool:
    if suit not in ("Herz", "Karo", "Pik", "Kreuz"):
        return False
    return Card(suit, "König") in hand and Card(suit, "Dame") in hand


def _legal_follow(hand: list[Card], lead: Card, trump: str, restricted: bool) -> list[Card]:
    if not restricted:
        return list(hand)
    same = [card for card in hand if card.suit == lead.suit]
    if same:
        higher = [card for card in same if card.rank_value > lead.rank_value]
        return higher or same
    trumps = [card for card in hand if card.suit == trump]
    return trumps or list(hand)


def _execute(match: Match, plan: Plan) -> None:
    if plan.kind == "next-deal":
        start_deal(match)
        return
    if plan.kind == "seen":
        _resolve_trick(match)
        return
    deal = match.deal
    assert deal is not None
    seat = deal.to_play
    took: str | None = None
    if plan.exchange:
        took = _exchange(deal, seat)
    if plan.close:
        _close(deal, seat)
    if plan.marriage:
        _add_marriage(deal, seat, plan.marriage)
        if counting_eyes(deal, seat) >= 66:
            _note(
                deal,
                LastAction(
                    seat=seat,
                    exchange=plan.exchange,
                    took=took,
                    closed=plan.close,
                    marriage=plan.marriage,
                    declared=True,
                ),
            )
            _declare(match, seat)
            return
    assert plan.card is not None
    _play_card(match, seat, plan.card, plan, took)


def _exchange(deal: Deal, seat: Seat) -> str:
    bube = Card(deal.trump_suit, "Bube")
    taken = deal.trump_card
    assert taken is not None
    deal.hands[seat].remove(bube)
    deal.hands[seat].append(taken)
    deal.trump_card = bube
    return taken.label


def _close(deal: Deal, seat: Seat) -> None:
    deal.opponent_eyes_at_close = counting_eyes(deal, other(seat))
    deal.opponent_trickless_at_close = not deal.won_trick[other(seat)]
    deal.closed = True
    deal.closed_by = seat
    deal.trump_card = None
    deal.talon = []


def _add_marriage(deal: Deal, seat: Seat, suit: str) -> None:
    deal.marriage_eyes[seat] += 40 if suit == deal.trump_suit else 20


def _play_card(match: Match, seat: Seat, card: Card, plan: Plan, took: str | None) -> None:
    deal = match.deal
    assert deal is not None
    deal.hands[seat].remove(card)
    deal.current_trick.append((seat, card))
    _note(
        deal,
        LastAction(
            seat=seat,
            exchange=plan.exchange,
            took=took,
            closed=plan.close,
            marriage=plan.marriage,
            card=card.label,
        ),
    )
    if len(deal.current_trick) == 1:
        deal.to_play = other(seat)
        return
    if seat == "computer":
        deal.phase = "acknowledge"
        deal.to_play = "human"
        return
    _resolve_trick(match)


def _note(deal: Deal, action: LastAction) -> None:
    deal.last_action = action
    if action.seat == "computer":
        deal.computer_action = action


def _resolve_trick(match: Match) -> None:
    deal = match.deal
    assert deal is not None
    (lead_seat, lead_card), (follow_seat, follow_card) = deal.current_trick
    winner = follow_seat if _follower_wins(lead_card, follow_card, deal.trump_suit) else lead_seat
    deal.tricks[winner].append([lead_card, follow_card])
    deal.won_trick[winner] = True
    deal.current_trick = []
    deal.leader = winner
    hands_empty = all(len(deal.hands[seat]) == 0 for seat in SEATS)
    if hands_empty and (deal.closed or cards_to_draw(deal) == 0):
        _finish_terminal(match, winner)
        return
    if counting_eyes(deal, winner) >= 66:
        _declare(match, winner)
        return
    _draw_pair(deal, winner)
    deal.to_play = winner
    deal.phase = "play"


def _follower_wins(lead: Card, follow: Card, trump: str) -> bool:
    if follow.suit == lead.suit:
        return follow.rank_value > lead.rank_value
    return follow.suit == trump and lead.suit != trump


def _draw_pair(deal: Deal, winner: Seat) -> None:
    if deal.closed or cards_to_draw(deal) <= 0:
        return
    _draw_one(deal, winner)
    if cards_to_draw(deal) > 0:
        _draw_one(deal, other(winner))


def _draw_one(deal: Deal, seat: Seat) -> None:
    if deal.talon:
        deal.hands[seat].append(deal.talon.pop(0))
    elif deal.trump_card is not None:
        deal.hands[seat].append(deal.trump_card)
        deal.trump_card = None


def _declare(match: Match, seat: Seat) -> None:
    deal = match.deal
    assert deal is not None
    opponent = other(seat)
    if counting_eyes(deal, seat) < 66:
        award = trick_points(not deal.won_trick[opponent], counting_eyes(deal, opponent))
        record_game_points(match, opponent, award)
        return
    if deal.closed and seat != deal.closed_by:
        award = 3 if deal.opponent_trickless_at_close else 2
        record_game_points(match, seat, award)
        return
    if deal.closed and seat == deal.closed_by:
        award = trick_points(
            bool(deal.opponent_trickless_at_close),
            deal.opponent_eyes_at_close or 0,
        )
        record_game_points(match, seat, award)
        return
    award = trick_points(not deal.won_trick[opponent], counting_eyes(deal, opponent))
    record_game_points(match, seat, award)


def _finish_terminal(match: Match, last_winner: Seat) -> None:
    deal = match.deal
    assert deal is not None
    if deal.closed and deal.closed_by is not None:
        if counting_eyes(deal, deal.closed_by) >= 66:
            award = trick_points(
                bool(deal.opponent_trickless_at_close),
                deal.opponent_eyes_at_close or 0,
            )
            record_game_points(match, deal.closed_by, award)
            return
        opponent = other(deal.closed_by)
        award = 3 if deal.opponent_trickless_at_close else 2
        record_game_points(match, opponent, award)
        return
    opponent = other(last_winner)
    award = trick_points(not deal.won_trick[opponent], counting_eyes(deal, opponent))
    record_game_points(match, last_winner, award)
