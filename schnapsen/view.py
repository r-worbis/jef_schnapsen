"""Human and Jev projections of one match. Hidden cards stay out of each payload."""

import json

from schnapsen.engine import (
    Deal,
    Match,
    Seat,
    action_label,
    counting_eyes,
    legal_action_ids,
    other,
)
from schnapsen.rules_text import RULES


def human_view(match: Match) -> dict[str, object]:
    deal = match.deal
    if deal is None:
        return {"started": False}
    your_turn = deal.phase != "ended" and deal.to_play == "human"
    actions = legal_action_ids(match) if your_turn else []
    return {
        "started": True,
        "dealer": match.dealer,
        "yourHand": [card.label for card in deal.hands["human"]],
        "opponentCount": len(deal.hands["computer"]),
        "trump": None if deal.trump_card is None else deal.trump_card.label,
        "trumpSuit": deal.trump_suit,
        "talonCount": len(deal.talon),
        "closed": deal.closed,
        "trick": [{"seat": seat, "card": card.label} for seat, card in deal.current_trick],
        "toPlay": None if deal.phase == "ended" else deal.to_play,
        "yourTurn": your_turn,
        "yourTricks": _named(deal.tricks["human"]),
        "opponentFirstTrick": _named(deal.tricks["computer"][:1]),
        "eyes": {seat: counting_eyes(deal, seat) for seat in ("human", "computer")},
        "pointsNeeded": dict(match.points_needed),
        "bummerl": dict(match.bummerl),
        "actions": [{"id": action_id, "label": action_label(action_id)} for action_id in actions],
        "computerAction": _action_payload(deal),
        "dealOver": deal.phase == "ended",
        "dealWinner": deal.winner,
        "gamePoints": deal.game_points,
        "matchOver": match.match_winner is not None,
        "matchWinner": match.match_winner,
        "canNextDeal": deal.phase == "ended" and match.match_winner is None,
        "missingKey": match.notice == "missing-key",
        "choiceReplaced": match.choice_replaced,
        "jev": _jev_payload(match),
    }


def jev_parts(match: Match) -> tuple[str, str]:
    deal = match.deal
    if deal is None:
        return RULES, ""
    seat: Seat = "computer"
    opponent = other(seat)
    remainder = [
        "Your cards: " + ", ".join(card.label for card in deal.hands[seat]),
        f"Trump suit: {deal.trump_suit}",
        "Trump card: " + ("hidden" if deal.trump_card is None else deal.trump_card.label),
        f"Talon count: {len(deal.talon)}",
        f"Talon closed: {'yes' if deal.closed else 'no'}",
        "Current trick: " + _trick_text(deal),
        "Your tricks: " + _tricks_text(deal.tricks[seat]),
        "Opponent first trick: " + _tricks_text(deal.tricks[opponent][:1]),
        f"Your eyes: {counting_eyes(deal, seat)}",
        f"Opponent eyes: {counting_eyes(deal, opponent)}",
        (
            "Points still needed: "
            f"you {match.points_needed[seat]}, opponent {match.points_needed[opponent]}"
        ),
        f"Bummerl: you {match.bummerl[seat]}, opponent {match.bummerl[opponent]}",
        f"To play: {deal.to_play}",
        "Legal actions:",
    ]
    for action_id in legal_action_ids(match):
        remainder.append(f"- {action_id}: {action_label(action_id)}")
    return RULES, "\n".join(remainder)


def jev_state(match: Match) -> str:
    rules, remainder = jev_parts(match)
    if not remainder:
        return rules
    return f"{rules}\n\n{remainder}"


def _jev_payload(match: Match) -> dict[str, object]:
    exchange = match.jev_exchange
    if exchange is None:
        return {"rules": "", "cards": "", "answers": [], "failed": False}
    return {
        "rules": exchange.rules,
        "cards": exchange.cards,
        "answers": list(exchange.answers),
        "failed": exchange.failed,
    }


def _named(tricks: list[list]) -> list[list[str]]:
    return [[card.label for card in trick] for trick in tricks]


def _tricks_text(tricks: list[list]) -> str:
    if not tricks:
        return "none"
    return "; ".join(", ".join(card.label for card in trick) for trick in tricks)


def _trick_text(deal: Deal) -> str:
    if not deal.current_trick:
        return "none"
    return ", ".join(f"{seat} played {card.label}" for seat, card in deal.current_trick)


def _action_payload(deal: Deal) -> dict[str, object] | None:
    action = deal.computer_action
    if action is None:
        return None
    return {
        "exchange": action.exchange,
        "took": action.took,
        "closed": action.closed,
        "marriage": action.marriage,
        "card": action.card,
        "declared": action.declared,
        "continued": action.continued,
    }


def dumps(payload: dict[str, object]) -> str:
    return json.dumps(payload)
