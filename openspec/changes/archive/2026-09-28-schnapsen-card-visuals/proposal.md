# Proposal

## Why

The in-flight change `schnapsen-jev-player` has no card pictures. Its table draws each card as rank text plus a suit character in CSS. The pack and the page therefore have nothing a person can inspect as a real deck. Adding license-clear drawings now, then wiring them into the table only after that deck is checked by hand, keeps artwork review separate from play.

## What Changes

- Confirm that `schnapsen-jev-player` and the current `schnapsen/` page do not already ship card images (they do not: design of that change forbids image files; `page.html` uses `♥ ♦ ♠ ♣` and rank names).
- Add a twenty-card French-suited Schnapsen pack (Herz, Karo, Pik, Kreuz × Ass, Zehner, König, Dame, Bube) plus one card back as SVG (or drawings in SVG) under the project, with a source and license record.
- Add a small local preview that shows every face and the back so a person can approve the deck before play uses it.
- After that review, show those faces on the human table wherever a card is face up, and the back wherever a card is face down. Engine labels, legal actions, and Jev prompts stay text.

## Capabilities

### New Capabilities

- `schnapsen-card-faces`: Vendor the Schnapsen pack artwork, map it to engine card tokens, expose a review of the full deck, and (after that review) render those faces on the table.

### Modified Capabilities

- (none — `schnapsen-table` is not in the main spec set yet; table rendering of faces is specified here so this change does not rewrite the in-flight table delta.)

## Impact

- New static files under the repo (SVG faces, back, license/attribution).
- New or extended HTML for a deck preview; later, `schnapsen/page.html` (and its CSS) so face-up and face-down cards use those files.
- No change to dealing, scoring, action ids, or Jev payloads.
- Apply is two parts: Part I stops at committed artwork plus preview. Part II starts only after a person has looked at that preview and accepted the deck.
