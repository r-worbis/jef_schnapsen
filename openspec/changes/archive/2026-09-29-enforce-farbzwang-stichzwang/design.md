# Design

## Context

See proposal.md for why. `schnapsen/engine.py` already filters a follow in `_legal_follow`. `is_legal` calls it when a trick has a lead, and `apply_action` returns without calling `_execute` when `is_legal` is false. `_candidates` uses the same function, and `legal_action_ids` keeps only ids that `is_legal` accepts. The human view and the Jev request both take that list.

`stock_open` is true only when the talon is not closed and `cards_to_draw` is greater than zero. `cards_to_draw` counts the face-down talon plus the face-up trump, so the obligations start only after that trump has been drawn, or after a close. Rank order is the existing `rank_value`: Ass, Zehner, König, Dame, Bube.

`tests/test_game.py` already locks beating a plain suit and suit-before-trump. It does not lock a void, a trump lead, a computer-seat refusal, or a discard while the face-up trump is still to be drawn.

## Goals / Non-Goals

**Goals:**

- One follow check in the engine, used both to list legal plays and to refuse a play.
- That check implements the order in the modified `schnapsen-game` requirement: higher card of the led suit, else any card of that suit, else a trump, else any card. A trump lead is a led suit, not a separate trump step.
- Tests for the scenarios that are not locked yet.

**Non-Goals:**

- A second checker in `schnapsen/page.html` or `schnapsen/player.py`.
- Changing marriage, exchange, closing, drawing, 66, or last-trick scoring.
- Requiring the lowest card that wins the trick.

## Decisions

### Keep `_legal_follow` as the only follow rule

The restricted branch already returns a higher card of the led suit, else the led suit, else trumps, else the hand. A trump lead falls into the led-suit branch because those cards share the lead's suit, so a non-trump is legal only when that branch is empty. `is_legal` and `_candidates` both call this function with `not stock_open(deal)`.

Alternative: a new rules module that inspects the deal after `_execute`. Rejected. A forbidden card must not change the deal, so the check has to run before `_execute`. A second copy can disagree with the list Jev and the table see.

Alternative: filter only in the page. Rejected. The computer turn and `POST /api/action` would bypass it. Both already go through `apply_action`.

### Do not special-case the seats

The same function runs for whoever `to_play` is. A test that the computer is to follow, and a test that the human is to follow, both submit a forbidden card through `apply_action` and expect a false result and an unchanged snapshot.

### Leave the open-talon branch as "any card"

When `stock_open` is true, `_legal_follow` returns the whole hand. That includes the moment the face-down talon is empty and the face-up trump is still to be drawn. No new flag.

### Exchange stays on the projected hand

A follow may still be paired with a trump-Bube exchange while the stock is open. `is_legal` already checks the projected hand. Exhausted and closed deals cannot exchange, because `can_exchange` is false once the trump is drawn or the talon is closed. This change does not touch that.

## Risks / Trade-offs

- [A scripted test follows with an off-suit card after the stock is closed while still holding the led suit] → Run `python -m unittest tests.test_game` and fix the script so the follow is legal, or fix `_legal_follow` if the new scenarios fail. Do not weaken the new scenarios.
- [`_candidates` and `is_legal` drift] → `legal_action_ids` already intersects candidates with `is_legal`, and `apply_action` refuses on `is_legal` alone. Keep both call sites on `_legal_follow` so the offered list and the refusal use one order.

## Migration Plan

No stored deal format and no action-id format changes. Rollback is reverting the engine check and the new tests.
