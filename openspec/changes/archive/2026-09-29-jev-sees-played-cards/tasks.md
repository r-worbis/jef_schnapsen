# Tasks

## 1. Jev remainder lists every awarded trick

- [x] 1.1 In `jev_parts`, list both seats' full awarded-trick piles (both cards, which seat won), keep the current trick, and leave the human-hand and talon-order omissions in place. Verify in `tests/test_table.py` that after the human has won two tricks the Jev state contains both of those tricks, still contains the computer hand and rules, and still omits a card remaining in the human hand. Verify `python -m unittest tests.test_table` passes.
- [x] 1.2 Confirm `human_view` still exposes only `opponentFirstTrick` for the computer pile. Verify the existing opening-view and opponent-first-trick assertions still pass under `python -m unittest tests.test_table`.
