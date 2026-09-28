# Design

## Context

See proposal.md for why the computer's answer must stay visible. Today `_play_card` in `schnapsen/engine.py` calls `_resolve_trick` as soon as `current_trick` has two cards. `submit_action` in `schnapsen/server.py` then plays the computer's answer in the same request as the human's lead, so the view returned to the page already has an empty trick and updated eyes. The page in `schnapsen/page.html` renders whatever `trick` and `actions` the view contains, and it calls `/api/computer` whenever `toPlay` is `computer`.

## Goals / Non-Goals

**Goals:**

- Keep the human lead and the computer's answering card in `current_trick` until the human confirms.
- Award, draw, and end the deal only inside the existing `_resolve_trick` path, triggered by that confirmation.
- Leave a human follow of a computer lead on the current immediate-award path.

**Non-Goals:**

- A pause when the computer leads, or when the human is the one who completes the trick.
- Changing the rules text sent to Jev. The pause is not a choice Jev is asked to make.
- A timer, a click on the card, or a separate HTTP route for confirmation.

## Decisions

### A new `acknowledge` phase, with the human to play

When the computer seat is the follower, `_play_card` sets `deal.phase` to `acknowledge` and `deal.to_play` to `human`, and returns without calling `_resolve_trick`. A human follower still falls through to `_resolve_trick`.

`acknowledge` is a phase, not a flag left on `play`. `_candidates` treats any non-empty trick as a follow and would offer more card plays against the lead. A separate phase makes those plays illegal in one branch, next to the existing `declare` and `ended` branches.

`to_play` is `human` so `computer_should_move` is false and the page does not post `/api/computer`. Jev is never offered this pause. `legal_action_ids` during `acknowledge` returns only the confirmation.

Alternative considered: resolve the trick in the engine and have the page delay the redraw. That would already have counted the eyes and drawn cards before the human had seen the reply, which the specs forbid.

### Confirmation is the action id `seen`

`parse_action("seen")` returns a plan of kind `seen`. It is legal only while `phase` is `acknowledge`. `_execute` calls `_resolve_trick` and does nothing else. `action_label` returns `Gesehen`, so the existing actions row in `page.html` is the button. No new control and no new route: the page posts `{ "id": "seen" }` to `/api/action`, the same way it posts every other human action.

After `seen`, `submit_action` keeps its current behavior of playing a computer turn when `computer_should_move` is true. If the computer won the trick and the deal continues, the response can already contain the computer's next lead. The awarded cards are then in the won-trick lists and the eyes, not left on the table. That matches every other human action that hands the turn to the computer.

### The human view needs no new fields

`human_view` already lists `current_trick`, counts eyes from awarded tricks only, and lists legal actions when `to_play` is `human`. During `acknowledge` that is both cards, the old eyes, `yourTurn: true`, and a single `seen` action. Reloading `/api/state` reads the same in-memory deal, so the two cards and the button come back.

`page.html` should keep calling `/api/computer` only when `toPlay` is `computer`. With `to_play` set to `human`, the current `load` and `sendAction` loops already wait. Change the page only if a check shows one of those loops would skip the button.

## Risks / Trade-offs

- [Engine tests apply a computer follow and then assert the awarded trick] → Those assertions run only after `seen`. Affected cases are the two tricks in `test_discard_loses_and_trump_captures_while_the_talon_is_open`, the three tricks in `test_winner_draws_first_and_a_closed_or_empty_talon_deals_nothing`, the computer follow in `test_trump_marriage_plain_marriage_and_no_eyes_without_a_trick` that expects `won_trick`, and the three terminal tricks in `test_declaration_thresholds_false_declaration_closer_failure_and_last_trick`. Follow-legality checks that stop before the computer plays a card stay as they are.
- [A later computer lead arrives in the same response as `seen`] → Accepted. The pause is for the answering card, not for the next lead. Eyes and won tricks in that response show the award.
- [`acknowledge` left in place would let a second computer play join the trick] → `to_play` is `human` and `computer_should_move` requires the computer. `legal_action_ids` returns only `seen`, so a stray computer call has no card to play.

## Migration Plan

The match lives in the server process. Restarting `python -m schnapsen` drops a deal that was mid-trick. There is no saved match to migrate.
