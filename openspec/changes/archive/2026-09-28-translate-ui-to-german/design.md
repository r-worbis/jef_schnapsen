# Design

## Context

See proposal.md for motivation. Human-visible English lives in two HTML documents (`schnapsen/page.html`, `schnapsen/static/cards/preview.html`) and in `action_label` in `schnapsen/engine.py`, which the table JSON already sends as `actions[].label`. Card tokens are already German (`Herz Ass` style labels). Jev’s full state dump in `view.jev_state` is English prose and is out of spec scope.

## Goals / Non-Goals

**Goals:**

- Replace every player-facing English string on the table and preview with German of equivalent meaning.
- Keep action ids and card tokens stable so play, SVG paths, and Jev choice keys stay the same.
- Centralize action wording in `action_label` so the table buttons and any reuse of those strings stay in one place.

**Non-Goals:**

- A locale switcher or English fallback.
- Translating `RULES` or the rest of `jev_state` line prefixes.
- Changing JSON keys, seat ids (`human` / `computer`), or HTTP routes.

## Decisions

### Direct German copy in HTML and JS

Replace the static headings in `page.html` and the strings assembled in `render()`. Do not add an i18n library. The product is German-only.

Alternatives considered: a message catalog. Rejected for a single-page static table with no second locale.

### German `action_label` only

Translate the phrases in `action_label`. Leave `parse_action` and action ids (`play:Herz-Ass`, `next-deal`, `declare`, …) unchanged. The page already displays `item.label` and uses `item.id` for posts.

Alternatives considered: client-side mapping from id to German. Rejected because labels are already server-provided and Jev criteria reuse the same function.

### `lang="de"` on both documents

Mark the table and preview as German so browsers and assistive tools match the copy. Card `figcaption` tokens stay as file names.

### Tests assert German where they asserted English UI

Update tests that match page chrome or action labels. Tests that match card tokens or action ids stay as they are.

## Risks / Trade-offs

- [Jev still sees mixed language: German action labels inside English `jev_state`] → Accept for this change; translating the dump would be a separate spec for `schnapsen-jev-player`.
- [Wording may not match Austrian Schnapsen slang] → Prefer common German table terms (Computer, Talon, Augen, Bummerl, nächstes Blatt) and keep Bummerl untranslated as a game term.

## Migration Plan

Ship as a single code change. No data migration. Rollback is reverting the HTML and `action_label` strings.

## Open Questions

None.
