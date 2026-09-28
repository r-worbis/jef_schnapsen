# Proposal

## Why

The table stacks the computer hand, the talon, the current trick, and the human hand in one vertical column, with scores in a side column. A horizontal board puts the two seats across from each other and keeps the stock and the cards just played between them, which is how the table is meant to be read.

## What Changes

- Arrange the playing surface in three columns: the computer seat (Jef) on the left, the current trump and talon together with the current trick in the middle, and the human seat on the right.
- Move the score block under that row: Augen, points still needed, and Bummerl. The Jev reveal stays with that lower band, because it currently sits in the side column that this layout removes.
- Keep the deck choice and the turn line above the board, on one row with the title. Keep action buttons, including the confirmation button, with the human hand. Keep deal or match banners above the board.
- Scale the table to the available screen width at all times: the board uses the full viewport width, and card size follows that width, instead of sitting in a fixed-width column.
- Keep the center short: trump, a compact talon stack with its count, and the current trick sit beside each other at about one card height, so Augen, points still needed, and Bummerl remain on the same screen as the hands.
- Leave game rules, the state API, card art, and which information is shown or hidden unchanged.

## Capabilities

### New Capabilities

### Modified Capabilities

- `schnapsen-table`: The page must place the computer hand on the left, the human hand on the right, the current talon and the current trick in the middle, and the score block below those three regions. The playing surface must always match the available screen width. Title, pack choice, and turn share one row. The center stays about one card high so the scores stay on screen.

## Impact

- `schnapsen/page.html` is the only playing surface. Its grid and section order change. Element ids used by the page script stay the same so rendering of hands, talon, trick, scores, actions, and the Jev boxes does not need a new data shape.
- No engine, view, or API change. `tests/test_card_faces.py` reads `page.html` for card paths and should keep passing if those paths stay put.
