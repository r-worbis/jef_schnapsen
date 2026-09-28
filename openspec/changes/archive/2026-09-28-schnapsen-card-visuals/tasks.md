# Tasks

## 1. Part I — vendor the pack

- [x] 1.1 Add `schnapsen/static/cards/` with twenty per-card SVG files named `{token}.svg` (`Herz-Ass.svg` … `Kreuz-Bube.svg`) extracted from David Bellot SVG-cards plus `back.svg`, and verify a listing of that directory contains those twenty-one files and no other ranks
- [x] 1.2 Add `schnapsen/static/cards/LICENSE` (LGPL-2.1-or-later text) and `ATTRIBUTION.md` (author, source URL, token-to-group mapping), and verify both files name the license and the Bellot / SVG-cards source
- [x] 1.3 If the local server does not yet serve files under `schnapsen/static/`, add that serving so a GET of a card SVG returns the file, and verify fetching `Herz-Ass.svg` and `back.svg` succeeds

## 2. Part I — deck preview

- [x] 2.1 Add `schnapsen/static/cards/preview.html` that displays all twenty faces and the back using those SVG files, labeled with the German token, and verify opening the preview (file or served URL) shows twenty-one drawings
- [x] 2.2 Leave `schnapsen/page.html` using CSS rank/suit cards, and verify `cardFace` still writes rank text and `suitMark` rather than `<img>` or `<svg>`

## 3. Human gate

- [x] 3.1 Stop. Do not start section 4 until a person has opened the preview and accepted the deck (mark this task done only after that acceptance)

## 4. Part II — table uses the pack

- [x] 4.1 Change `cardFace` in `page.html` so a face-up card uses the SVG for that label and keeps an accessible name of the rank and suit, and verify a dealt table in the browser shows pack art on the human hand and the trump
- [x] 4.2 Change `cardBack` so face-down computer cards and talon cards use `back.svg`, and verify those regions show the back and no computer face SVG
- [x] 4.3 Confirm a legal play click still sends the same action id, and verify clicking a playable human card still posts that card's play id
