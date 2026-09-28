# Proposal

## Why

This table is a test of Jev. The computer's turn sends the rules, the current cards, and the legal options, then applies Jev's answer, but the page never shows that text or the answer. A tester cannot see what was asked or what came back.

## What Changes

- Add a button on the Schnapsen table that reveals the last text sent to Jev and the answer Jev gave. Assumption: the control is a toggle on the existing table page, with German labels, and it is not added to the sample script `decide.py`.
- The reveal is three boxes: the game rules, the current cards and options, and the result.
- The rules box is the rules statement from that request. The cards box is the rest of that request: the computer seat's cards, the public table, and the legal actions. The result box is the answer Jev returned.
- When Jev is asked a second time on the same turn, both answers appear in the result box, in order. The rules and cards boxes stay the single shared request. If a request fails, the result box says so and names no invented choice.
- Before any request has been sent, the button still opens the three boxes, and each box says that nothing has been sent yet.
- The cards box includes the computer seat's hand, because that hand was in the request. Those faces stay off the rest of the table. The API key is never shown.
- What Jev is asked, which answer is applied, and the fallback when an answer is illegal or a request fails stay as they are.

## Capabilities

### New Capabilities

### Modified Capabilities

- `schnapsen-table`: The page gains a button that opens three boxes for the last Jev request and answer. The rule that hides the computer seat's cards allows those cards inside that cards box only.
- `schnapsen-jev-player`: After a computer turn that sends a request, the rules text, the cards and options text, and each answer Jev gave are kept for the table. Asking and applying a choice are unchanged.

## Impact

- `schnapsen/player.py`: keep the last request split and each answer, including a failed request, without changing which action is applied.
- `schnapsen/view.py` and `schnapsen/server.py`: include that exchange in the human view. The computer's remaining hand stays out of every other field.
- `schnapsen/page.html`: German toggle and three boxes.
- `tests/test_table.py`: the view exposes the three parts after a scripted computer turn, and the page offers the button. The sample script in `decide.py` is unchanged.
