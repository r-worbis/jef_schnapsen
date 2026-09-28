# Design

## Context

See proposal.md for motivation. Today `_resolve_trick` sets `phase` to `declare` when the winner has at least 66 eyes, and legal actions are `continue` plus `declare`. Marriage can also use `marry-declare:*` without leading. False `declare` from that phase awards the opponent. A computer follow still waits in `acknowledge` until `seen`; only then does `_resolve_trick` run.

## Goals / Non-Goals

**Goals:**

- Apply the existing `_declare` scoring path automatically when counting eyes first reach 66, after the trick is actually awarded.
- Drop the `declare` phase and the action ids `declare`, `continue`, and `marry-declare` (including exchange/close prefixes).
- Keep `acknowledge` / `seen` so a computer answer that would cross 66 is still visible before the deal ends.

**Non-Goals:**

- Changing game-point thresholds, Bummerl, last-trick scoring when nobody has 66, or closed-talon failure scoring.
- Letting a seat skip ending once they have 66.

## Decisions

### Call the existing award from `_resolve_trick` and after a counting marriage

When `_resolve_trick` would have entered `declare`, call `_declare(match, winner)` instead. After executing a marriage, if that seat already has a trick and counting eyes are at least 66, call `_declare` and do not play a marriage card. Last-trick and closed-talon empty-hand paths stay in `_finish_terminal`.

Alternative considered: keep a silent `declare` action applied by the server. Rejected because legal-action lists and Jev would still see a fake choice.

### Remove parse/legal/label branches for declare and continue

`parse_action`, `legal_action_ids`, `is_legal`, `_execute`, `_candidates`, and `action_label` drop those kinds. Tests that set `phase = "declare"` and `apply_action(..., "declare")` instead award a trick (or apply a marriage) and assert the deal ended. The false-declaration case is deleted.

### Rules text and table copy

`schnapsen/rules_text.py` states automatic ending at 66. Table tests that drive a computer `declare` become a computer play that crosses 66 after `seen`. Banner copy can keep “hat 66 angesagt” or switch to an ended-deal banner; either is fine as long as the result shows winner, points, and eyes.

## Risks / Trade-offs

- [A human who wanted to play on past 66 cannot] → Accepted; that is the requested rule.
- [Tests and table helpers still list `declare`] → Rewrite those cases as part of implementation, including `test_declaration_thresholds_false_declaration_closer_failure_and_last_trick` and the table computer-declare payload.

## Migration Plan

Local engine and tests only. No stored matches.
