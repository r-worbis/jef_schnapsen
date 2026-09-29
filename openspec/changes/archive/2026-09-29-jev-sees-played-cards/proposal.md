# Proposal

## Why

Jev already receives the computer seat's current hand, but each decision request omits most awarded tricks: only the computer's own won tricks and the human's first trick are listed. A human player remembers every card that has been played. Without that list, Jev cannot count remaining cards the way a competent opponent would.

## What Changes

- Include every awarded trick of the deal in the computer decision request, with both cards of each trick and which seat won it, not only the computer's tricks and the human's first trick.
- Keep listing the current incomplete trick, the computer's hand, rules, trump, talon count, closed flag, eyes, points, and Bummerl as today.
- Continue omitting the human seat's remaining hand and the order of face-down talon cards.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `schnapsen-jev-player`: The public table sent to Jev includes all played cards from awarded tricks, not only the computer's tricks and the opponent's first trick.

## Impact

- `schnapsen/view.py` (`jev_parts`) is the request text; tests in `tests/test_table.py` that assert opponent tricks stay truncated need to expect the full list for Jev while the human page can keep hiding later computer tricks.
- No engine, API, or SDK change. The human table payload is unchanged except that the Jev reveal "cards" box will show the richer remainder after the next computer turn.
