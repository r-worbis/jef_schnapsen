# Design

## Context

See proposal.md. `schnapsen-jev-player` design states suits are text and CSS, not image files. `schnapsen/page.html` builds a `.card` with rank text and `suitMark` (`♥ ♦ ♠ ♣`). Engine cards use `Card.label` (`Herz Ass`) and `Card.token` (`Herz-Ass`). There are no SVG or raster files in the repo today.

Schnapsen uses the French suits (hearts, diamonds, spades, clubs) and the ranks ace, ten, king, queen, jack — not a German-suited pack.

## Goals / Non-Goals

**Goals:**

- Vendor a complete, named set of twenty faces plus a back that maps 1:1 onto `Card.token`.
- Keep license files next to the art so redistribution stays honest.
- Give a static preview page that does not depend on a live match.
- Gate table integration on a person looking at that preview.

**Non-Goals:**

- Changing rules, action ids, or Jev text (those stay German rank/suit names).
- Animations, 3D, or a second deck theme.
- Raster conversion unless a chosen SVG cannot render in the browser as-is.

## Decisions

### Source of the drawings

Use David Bellot’s French-suited SVG pack (SVG-cards, LGPL-2.1-or-later), as published at [svg-cards.sourceforge.net](http://svg-cards.sourceforge.net/) and on Wikimedia Commons (`Svg-cards-2.0.svg`) / [htdebeer/SVG-cards](https://github.com/htdebeer/SVG-cards/). Face cards follow the Paris pattern. Group ids map as:

| Engine token | SVG group id |
| --- | --- |
| Herz-Ass | `heart_1` |
| Herz-Zehner | `heart_10` |
| Herz-König | `heart_king` |
| Herz-Dame | `heart_queen` |
| Herz-Bube | `heart_jack` |
| Karo-* | `diamond_*` (same rank suffix) |
| Pik-* | `spade_*` |
| Kreuz-* | `club_*` |
| back | `back` |

Copy the license text into the repo. Do not vendor jokers or ranks 2–9.

**Alternative considered:** CC0/public-domain scans of individual cards. Rejected as the default because twenty separate files plus a back would still need a consistent size and a named mapping; Bellot’s sheet already has both. Switch only if review rejects the Paris-pattern faces.

**Alternative considered:** Keep CSS pips. Rejected because the request is for drawings or SVG of the cards.

### How files live in the project

Store under `schnapsen/static/cards/`:

- `svg-cards.svg` (or extracted per-card SVG files if the sprite is awkward to serve)
- `LICENSE` (LGPL text)
- `ATTRIBUTION.md` (author, URL, mapping table)

If using the sprite, the preview and the table reference fragments (`svg-cards.svg#heart_1`) via `<use href="...">` or `<img>` of extracted cards. Prefer extracted per-card SVG files named `{token}.svg` plus `back.svg` so the mapping is visible on disk without opening the sprite.

### Two-part apply

**Part I** (this change’s first apply pass): add files, mapping, license, and `schnapsen/static/cards/preview.html` (or a route that only serves that folder) listing all twenty faces and the back. Do not change `page.html` yet.

**Part II** (only after a person says the preview is acceptable): change `cardFace` / `cardBack` in `page.html` to render the SVG (keep click handlers and action ids). Keep accessible names (rank and suit) on the element so tests that look for labels still work.

The stop between parts is a human gate, not a feature flag in the engine.

### Preview vs table

The preview is a static HTML file next to the SVGs so it can be opened as a file or served by the existing local server without a match. The table continues to get card identities as text labels from the JSON payload; only the browser maps label → drawing.

## Risks / Trade-offs

- [LGPL obligations if the SVG is modified or if linking rules are misread] → Keep the upstream SVG and license file unmodified; attribution in `ATTRIBUTION.md`; do not minify away the license.
- [Sprite `#fragment` `<img>` does not show a single card in all browsers] → Extract twenty-one standalone SVG files during Part I if fragment references fail in the preview.
- [Part II done before review] → Tasks list Part I complete and an explicit “stop for review” before any `page.html` edit.
- [Hidden cards leaking as faces] → Table still receives only labels the view already allows; computer hand and talon stay `back.svg`.

## Migration Plan

Part I is additive. Rollback is delete `schnapsen/static/cards/`. Part II rollback is restore CSS cards in `page.html`. No match data to migrate.

## Open Questions

None. Deck source is Bellot SVG-cards unless review rejects it, in which case Part I is redone with a different license-clear set and Part II still waits.
