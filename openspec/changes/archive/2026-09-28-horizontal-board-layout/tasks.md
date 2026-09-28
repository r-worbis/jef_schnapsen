# Tasks

## 1. Horizontal board in the page

- [x] 1.1 In `schnapsen/page.html`, put Computer, a center section holding `#trump`, `#talon`, and `#trick`, and Deine Karten (with `#actions` still inside it) in that order inside `.layout`. Move Augen, Noch benötigte Punkte, Bummerl, and the Jev section into a full-width band after `.layout`. Leave the title, deck choice, `#turn-line`, `#notice`, and `#result` above the board. Verify the same element ids remain and the German headings are unchanged.
- [x] 1.2 Replace the `1fr 240px` grid and the max-width 800px single-column rule with a three-column board that does not stack, a center column that stacks trump, wrapping talon, then trick, and a score row of three groups with the Jev control beneath it. Scale card size down with the viewport so the row stays left-center-right. Verify the stylesheet no longer sets `.layout` to one column, and that `.layout` uses three columns.
- [x] 1.3 Remove any max-width on `main` so the board always spans the available screen width, and size cards from viewport width. Verify `main` has no `max-width` and that card width uses `vw`.
- [x] 1.4 Put the title, pack choice, and turn line on one row. Draw the talon as a compact stack beside the trump and the trick so the center is about one card high. Verify a fresh deal shows Augen, points still needed, and Bummerl in the same viewport as the hands.

## 2. Confirm the table

- [x] 2.1 Load the table on a fresh deal and verify the computer backs are left of the trump and talon, the human cards and action buttons are right of them, and Augen, points still needed, Bummerl, and the Jev button are below that row. Play one card and verify the trick appears in the center, between the hands.
- [x] 2.2 Run `python -m unittest tests.test_card_faces tests.test_table tests.test_game` and verify it passes.
