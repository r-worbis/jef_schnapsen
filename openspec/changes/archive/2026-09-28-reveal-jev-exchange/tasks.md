# Tasks

## 1. Keep the last request and answers

- [x] 1.1 On `Match`, keep the rules statement, the remainder of the request, the returned choice ids in order, and whether a request failed. Write that record in `_decide` from the same lines `jev_state` already joins, and send `rules`, a blank line, then the remainder so the string Jev receives does not change. Append each returned choice. On a failed call, set the failure flag and store no invented choice. Leave the record in place when the key is missing and when `start_deal` starts another deal; replace it on the next request. Verify in `tests/test_table.py` that a legal choice is stored and applied, that an illegal choice followed by a legal one stores both and applies the second, that a failing client stores the failure with no choice id and applies the fallback, that a later missing-key turn leaves that record, that the API key is absent from it, and that the sent state still contains `RULES` and the computer hand. Verify `python -m unittest tests.test_table` passes.

- [x] 1.2 Add that record to `human_view`. Before any request, the rules, cards, and answers are empty. After a request, a card the computer still holds appears only in the cards text. Verify the existing opening-view payload test still finds no computer-hand face, and add a test that a still-held requested card is in the cards text and in no other field of the JSON. Verify `python -m unittest tests.test_table` passes.

## 2. Reveal button and three boxes

- [x] 2.1 In `schnapsen/page.html`, add one toggle in the aside. Its label is `Jev anzeigen` while the boxes are hidden and `Jev ausblenden` while they are shown. The headings are `Spielregeln`, `Karten und Optionen`, and `Ergebnis`. Empty text is `Noch keine Anfrage.` A failed request adds `Die Anfrage ist fehlgeschlagen.` and does not invent a choice id. Returned choice ids are shown in order. The boxes start hidden, and a reload starts hidden while `GET /api/state` still returns the same three texts. Verify a test that the page contains those labels and that a second `GET /api/state` after a scripted computer turn returns the same rules, cards, and answer. Verify `python -m unittest tests.test_table` passes.

- [x] 2.2 Verify in the browser: open the button before any computer request and see `Noch keine Anfrage.` in all three boxes; after a computer turn, open the button and see the rules, the cards and options that were sent, and the returned action id; use the button again and see the boxes hide. The computer's cards on the table stay face down.
