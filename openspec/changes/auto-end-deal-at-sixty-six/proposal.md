# Proposal

## Why

Reaching 66 counting eyes already decides the deal, but the engine still asks the winning seat to declare or continue. That extra choice is unused in this game: as soon as either seat has enough eyes, the deal should end.

## What Changes

- **BREAKING**: After a trick is awarded (including after `seen` for a computer answer) or after a marriage that counts, if that seat has at least 66 counting eyes, the engine ends the deal immediately and awards game points by the existing correct-declaration thresholds.
- **BREAKING**: Remove the `declare` phase and the player actions `declare`, `continue`, and `marry-declare` (and their exchange/close prefixes). False declarations are no longer possible.
- Keep last-trick and closed-talon failure scoring when nobody has reached 66.
- The table no longer offers a 66 declaration. The computer seat is no longer asked to choose declare vs continue.
- Update the rules text sent to Jev so it matches automatic ending at 66.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `schnapsen-game`: End the deal automatically at 66; drop optional and false declarations.
- `schnapsen-table`: Stop offering a declaration; show the deal result when 66 is reached without a player choice.
- `schnapsen-jev-player`: Legal computer actions no longer include declare or continue; rules text describes automatic ending.

## Impact

`schnapsen/engine.py` (`_resolve_trick`, marriage execution, action ids, labels, phases), `schnapsen/rules_text.py`, table copy in `schnapsen/page.html` if it mentions declaring 66, and tests in `tests/test_game.py` and `tests/test_table.py` that apply `declare` or expect a declare phase. Jev still chooses among remaining legal plays only.
