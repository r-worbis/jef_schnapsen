# Proposal

## Why

When the human leads and the computer answers, the reply is played and the trick is collected in the same step. The answering card never stays on the table, so the human cannot see what was played before the cards are taken and the eyes are counted.

## What Changes

- After the computer plays a card in answer to the human's lead, both cards stay on the table.
- The trick is not collected, and eyes, draws, the next leader, and any deal result that depends on that trick do not change, until the human confirms they have seen the reply.
- The table offers one confirmation control for that pause. Assumption: confirmation is an explicit button, labeled in German like the rest of the table, not a timer and not a click on the card.
- A trick the human completes by following the computer's lead is still collected immediately. The computer's own lead is unchanged.

## Capabilities

### New Capabilities

### Modified Capabilities

- `schnapsen-game`: A computer card played in answer to the human's lead does not award the trick until the human confirms they have seen it.
- `schnapsen-table`: While that reply is waiting, the page keeps both cards face up and accepts only the confirmation that collects and counts the trick.

## Impact

- `schnapsen/engine.py`: trick resolution when the computer is the follower, plus a human-only confirmation action.
- `schnapsen/server.py` and `schnapsen/page.html`: the pause must not start another computer turn, and the page must show the reply and the confirmation control.
- `schnapsen/view.py`: the waiting trick stays in the human view until confirmation.
- Tests in `tests/test_game.py` and `tests/test_table.py` that script a computer follow and expect the trick to be gone at once.
