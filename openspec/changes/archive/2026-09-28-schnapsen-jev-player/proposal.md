# Proposal

## Why

The repository can already ask Jev a typed question, but it has no game for that decision to play. A local Schnapsen table gives Jev a real choice — which legal action to take — while a person plays the other seat and can see their own cards and the score.

## What Changes

- Add weiches Schnapsen for two players: a 20-card pack, dealer and forehand, the talon and face-up trump, tricks, marriages, trump-jack exchange, closing the talon, 66-eye declaration, and last-trick wins.
- Score each deal in eyes and game points, counted down from seven. The first player to seven game points wins the Bummerl. A 7:0 Bummerl is Schneider and counts double. A match ends when one player has two Bummerl.
- Add a local page for the human seat: own cards, the computer's card count (faces hidden), trump, talon, the current trick, eyes, points still needed, and Bummerl.
- On the computer's turn, send Jev that player's own cards, the written rules, and the public table state, and ask which legal action to play. The engine applies only a legal action. The human's hidden cards are not sent.
- Leave `decide.py` and the `jev-decisions` sample as they are. The API key stays in the environment and is not written into the repository.

Assumptions recorded here: the rules are the main weiches Schnapsen section of the German Wikipedia article (French suit names: Herz, Karo, Pik, Kreuz; ranks Ass, Zehner, König, Dame, Bube). Scharfes Schnapsen, tournament scoring, and three- or four-player variants are out of scope. A match is first to two Bummerl.

## Capabilities

### New Capabilities

- `schnapsen-game`: Deal, play, and score a weiches Schnapsen match between two seats.
- `schnapsen-table`: Show the human seat its cards and the match state, and accept its legal actions.
- `schnapsen-jev-player`: Ask Jev how the computer seat should play from its own cards, the rules, and the public table.

### Modified Capabilities

- None. `jev-decisions` still runs the fixed sample script only.

## Impact

- New Python game package and a local browser page, beside the existing `decide.py` script.
- Reuses `typesafe-sdk` and `TypeSafeClient.system_one` (`jev-latest`). No new model host.
- Each computer turn calls `https://api.typesafe.ai/v1/systemone` and needs `TYPESAFE_API_KEY`.
- The engine is testable without a live call. A live match spends account credit once per computer decision.
