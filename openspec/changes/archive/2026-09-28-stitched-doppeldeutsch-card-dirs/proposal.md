# Proposal

## Why

Doppeldeutsch on the table is the Wikimedia Skat set, not the Wilhelm-Tell faces described at [Doppeldeutsche Karten](https://schnopsn.com/doppeldeutsche-karten). Many of the pictures published with that article are only the upright half of a card, so they are not yet a full face that still reads after a 180° turn. The French faces also still sit in `schnapsen/static/cards/` beside `doppeldeutsch/`, so the two packs are not stored the same way.

## What Changes

- Take the twenty Schnapsen faces from `https://schnopsn.com/images/ddeutsch/` (Pik, Kreuz, Herz, Schellen; Ass, Zehner, König, Ober, Unter). The smaller `_2` crops on the article are not the face files.
- **BREAKING** for anyone requesting the old paths: a half-height source is stitched to a 180° copy of itself so the vendored face is one full double-ended card. A source that is already full height is kept as that full card. The resulting files replace the Wikimedia SVGs in `doppeldeutsch/`.
- **BREAKING** for the old French URLs: move the twenty French `{token}.svg` files into `schnapsen/static/cards/french/`. Leave the shared `back.svg`, `LICENSE`, `ATTRIBUTION.md`, and `preview.html` in `schnapsen/static/cards/`.
- Point the table and the deck preview at `french/{token}.svg` and `doppeldeutsch/{token}.png`. The Französisch / Doppeldeutsch choice, the visible name mapping, and the shared back stay as they are.
- Assumption: the article page does not publish a reuse license. Attribution records that page and the image URLs in place of the Wikimedia CC BY-SA note for this pack. The French LGPL record stays.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `schnapsen-card-faces`: French faces live in `french/`, doppeldeutsche faces are the stitched Tell pictures in `doppeldeutsch/`, and the preview and the table load the directory for the selected pack.

## Impact

- `schnapsen/static/cards/` (new `french/`, replaced `doppeldeutsch/` files, attribution).
- Face URLs in `schnapsen/page.html` and `schnapsen/static/cards/preview.html`.
- `tests/test_card_faces.py`, which currently expects the French SVGs at the top of `cards/` and doppeldeutsch SVGs from the Wikimedia set.
- No change to engine tokens, action ids, dealing, or the text sent to Jev.
