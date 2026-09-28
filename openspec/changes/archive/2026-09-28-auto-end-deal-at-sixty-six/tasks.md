# Tasks

## 1. Engine: end at 66 without a choice

- [x] 1.1 In `_resolve_trick`, when the winner has at least 66 counting eyes, call `_declare` instead of setting `phase` to `declare`. After a marriage that counts and reaches 66, call `_declare` and do not lead a marriage card. Remove `marry-declare` candidates. Verify a unit case: a trick (or marriage with a prior trick) that reaches 66 ends the deal with the 3/2/1 awards, no `declare`/`continue` in `legal_action_ids`, and no marriage card on the table.
- [x] 1.2 Remove `declare` and `continue` from parse, legal, labels, `_execute`, and the declare-phase branch of `legal_action_ids`. Delete the false-declaration test. Keep last-trick and closer-failure scoring. Verify `python -m unittest tests.test_game` passes, including the closed-talon closer award of 1 and the computer-answer case that stays below 66 until `seen` then ends.

## 2. Rules text, table, and Jev

- [x] 2.1 Update `schnapsen/rules_text.py` so a deal ends at 66 with no declaration. Verify the rules string used in a computer decision request includes that wording and does not tell Jev to choose declare or continue (`python -m unittest tests.test_table` or the test that captures the Jev prompt).
- [x] 2.2 Stop offering `declare`/`continue` on the table. Replace the computer-declare payload test with a play that crosses 66 after `seen`. Verify the human view after such a trick shows the deal result (winner, game points, both eyes) and no declaration action, and that `python -m unittest` passes.
