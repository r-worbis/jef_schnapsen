# Proposal

## Why

Once the talon is exhausted, the follower is no longer free to play any card. Farbzwang (follow the led suit) and Stichzwang (take the trick when able; the request's Stickzwang) have to be enforced by the engine before a card is accepted. The current scenarios only lock "beat a plain suit" and "suit before trump", so a void follow or a trump lead can drift from those two rules without a failing test.

## What Changes

- The engine's legality check is the only gate for a follow. It applies to the human seat and the computer seat. The page and Jev do not decide the rule themselves.
- Once nothing remains to draw, or the talon has been closed, the follower must obey Farbzwang, then Stichzwang: a higher card of the led suit if they have one, otherwise a lower card of that suit, otherwise a trump, otherwise any card.
- A follow that breaks that order is refused. Cards, eyes, and scores stay as they were, and the same seat is still to play.
- The legal-action list is that same check, so the table and Jev are offered only cards the engine would accept.
- Assumption: "talon exhausted" means no face-down talon card remains and the face-up trump has already been drawn. While that trump is still to be drawn, the stock is still open and these obligations do not apply.
- Assumption: closing the talon keeps using this same check, as the existing close rule already requires.
- Assumption: any higher card of the led suit is a legal way to satisfy Stichzwang. The follower is not required to play the lowest winner.

## Capabilities

### New Capabilities

### Modified Capabilities

- `schnapsen-game`: The follow rule after the talon is exhausted or closed names Farbzwang and Stichzwang, covers a void in the led suit and a trump lead, and is refused by the engine for either seat.

## Impact

- `schnapsen/engine.py`: the follow filter used by the legality check and by the legal-action list.
- `tests/test_game.py`: cases for a void, a trump lead, and a refused follow from either seat.
- The table and the Jev request stay on the engine's legal-action list. Their specs do not change.
