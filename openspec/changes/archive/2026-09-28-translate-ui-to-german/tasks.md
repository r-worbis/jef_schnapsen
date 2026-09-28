# Tasks

## 1. Table page copy

- [x] 1.1 Set `schnapsen/page.html` `lang` to `de` and replace static headings and the initial turn line with German; verify the file contains `lang="de"` and German headings for Computer, Trumpf und Talon, Stich, Deine Karten, Augen, Noch benötigte Punkte, and Bummerl
- [x] 1.2 Translate every string assembled in `render()` (dealer/turn, banners, talon/trump notes, trick captions, score-row names, face-down aria labels) to German; verify no player-facing English remains in `schnapsen/page.html` besides card tokens and code identifiers

## 2. Action labels

- [x] 2.1 Translate `action_label` in `schnapsen/engine.py` to German while leaving action ids unchanged; verify a unit check that `declare` / `next-deal` / play ids still parse the same and their labels are German
- [x] 2.2 Update tests that match English action labels or table chrome so they expect German copy; verify `python -m unittest tests.test_table tests.test_game tests.test_card_faces` (or the project’s usual test command) passes

## 3. Deck preview copy

- [x] 3.1 Set `schnapsen/static/cards/preview.html` `lang` to `de` and translate the title, heading, and instructional paragraph; verify captions still use the existing German card tokens and the heading is German
