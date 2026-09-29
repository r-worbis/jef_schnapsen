# Proposal

## Why

The match can only seat a person against Jev. The computer turn, the "seen" pause, and the Jev request are all hard-wired to that one pairing, so a second AI cannot take a seat and two AIs cannot play each other. A later model player has to be safe even when it proposes a card that breaks the rules, which means the engine, not the player, has to accept or refuse the play.

## What Changes

- Bind each of the two existing seats to a player kind. The kinds in this change are the person at the page, Jev, and a stub that stands in for an LLM. The default binding stays the person on the right and Jev on the left.
- The right seat may be the person, Jev, or the stub. The left seat may be Jev or the stub. That allows Jev against the stub, the stub against itself, and Jev against itself, as well as the person against either AI.
- The stub proposes one card drawn uniformly at random from its own hand, as a plain play. It does not marry, exchange the trump, close the talon, or apply Farbzwang or Stichzwang itself. An injected random source makes the draw repeatable in tests.
- A player only proposes an action. The engine is the only code that applies one, and it applies it only when the action is legal. Once the talon is exhausted or closed, that check is Farbzwang and then Stichzwang (the request's Stickzwang): a higher card of the led suit, otherwise a lower card of that suit, otherwise a trump, otherwise any card. A refused proposal leaves the cards, eyes, and scores unchanged, and the same seat is still to play.
- An illegal proposal is asked again once. A second illegal proposal applies one predetermined legal action and the table shows that the choice was replaced. A missing `jef.api` key still applies nothing when the seat to play is Jev.
- The pause that waits for "Gesehen" applies only when the person led and an AI has just answered. When the right seat is an AI, the trick is taken as soon as the answering card is played.
- Assumption: seat ids stay `human` (right) and `computer` (left). Those ids are places at the table, not the player kind.
- Assumption: the person can sit only on the right. This change does not add a second human seat.
- Assumption: the follow order itself stays the one already required by `schnapsen-game` and tightened by the open change `enforce-farbzwang-stichzwang`. This change does not replace that change. It requires every player, including two AIs, to pass through that same engine check.
- Assumption: the stub's random draw uses the process random source unless a test injects one. It never calls an LLM and never reads `jef.api`.

## Capabilities

### New Capabilities

- `schnapsen-players`: Bind a player kind to each seat, play a deal between two AIs, and let the stub propose a random card from its hand without applying it.

### Modified Capabilities

- `schnapsen-game`: Any seat's proposal is accepted only by the engine, including Farbzwang and Stichzwang after the talon is exhausted or closed. The "seen" pause applies only when the person at the page led.
- `schnapsen-jev-player`: Jev is one player kind and can sit on either seat. The request carries that seat's own cards. Retry, fallback, and the missing-key stop stay.
- `schnapsen-table`: The page chooses the two player kinds, hides a hand that is not the person's, and advances an AI turn. It does not ask for "Gesehen" when an AI led.

## Impact

- `schnapsen/engine.py`: `apply_action` remains the only way a card is played. The acknowledge pause depends on whether the leader is the person, not on the seat id `computer`.
- `schnapsen/player.py`: Jev becomes one implementation of a player that proposes an action. A new stub player proposes a random card. The server asks whichever player is bound to the seat to play.
- `schnapsen/server.py`, `schnapsen/view.py`, and `schnapsen/page.html`: the match records the two bindings; the page can start a match of two AIs and still start the current person-versus-Jev match.
- Tests in `tests/test_game.py` and `tests/test_table.py` cover a refused follow from a non-human proposal, a stub card, and a deal in which two AIs face each other.
- Action ids stay as they are. One new request sets the two player kinds and starts a new match. `jef.api` stays the only key source, and only Jev reads it.
