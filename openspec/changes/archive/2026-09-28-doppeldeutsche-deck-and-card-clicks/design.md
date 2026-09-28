# Design

## Context

See proposal.md for why. The French faces already live as `{token}.svg` plus `back.svg` in `schnapsen/static/cards/`, and `tests/test_card_faces.py` asserts that directory's top-level `*.svg` set is exactly those twenty-one files. `page.html` builds a face URL from the engine label (`Herz Ass` → `Herz-Ass.svg`) and makes a hand card a button only for `play:{token}`. The same turn also renders every legal action, including those `play:` ids, as a text button. `server.py` already serves files under `/static/` in subdirectories. Engine tokens, `action_label`, and the JSON view stay French.

## Goals / Non-Goals

**Goals:**

- Vendor a second twenty-card face set addressed by the same engine tokens, and let the preview and the table switch drawings and visible names together.
- Drop only the text buttons whose id is a plain `play:` action.

**Non-Goals:**

- Renaming engine suits or ranks, or changing action ids, Jev text, or legal moves.
- A second card back, the Skat 7/8/9, or a new click for marriage, exchange, or closing.
- Waiting for a separate art-acceptance step before the selector works. The player can stay on Französisch.

## Decisions

### Vendor the Wikimedia German-suited SVGs under the engine tokens

Use the twenty Schnapsen ranks from the Wikimedia Commons set "German Skat cards (SVG set by Mfrasca)" (CC BY-SA 3.0, traced from the xskat German cardset). That set is German-suited and double-ended (Eichel, Blatt, Herz, Schellen; Daus, 10, König, Ober, Unter). It is the license-clear doppeldeutsche suit system, not a commercial Piatnik scan.

Store unmodified copies at `schnapsen/static/cards/doppeldeutsch/{engine-token}.svg`:

| Engine token | Wikimedia file |
| --- | --- |
| Herz-Ass, Herz-Zehner, Herz-König, Herz-Dame, Herz-Bube | `hart-01 daus`, `hart-10`, `hart-13 konig`, `hart-12 ober`, `hart-11 unter` |
| Karo-Ass, Karo-Zehner, Karo-König, Karo-Dame, Karo-Bube | `schellen-01`, `schellen-10`, `schellen-13 king`, `schellen-12 queen`, `schellen-11 jack` |
| Pik-Ass, Pik-Zehner, Pik-König, Pik-Dame, Pik-Bube | `blatt-01 daus`, `blatt-10`, `blatt-13 king`, `blatt-12 queen`, `blatt-11 jack` |
| Kreuz-Ass, Kreuz-Zehner, Kreuz-König, Kreuz-Dame, Kreuz-Bube | `eichel-01 daus`, `eichel-10`, `eichel-13 konig`, `eichel-12 ober`, `eichel-11 unter` |

A subdirectory keeps the existing top-level French glob intact. Both packs use the existing `back.svg`. Record the source, author, and CC BY-SA 3.0 in `ATTRIBUTION.md` without replacing the French `LICENSE` file.

Alternative: draw a new pack. Rejected because a complete free German-suited set already exists. Alternative: put the files beside the French ones. Rejected because the current test requires the top-level set to be exactly the French pack plus the back.

### One remembered choice, applied only in the browser

A control labeled Französisch / Doppeldeutsch on `page.html` and on `preview.html` reads and writes the same `localStorage` key `schnapsen-deck`. Missing or unknown values mean Französisch. Changing it re-renders from the last table state, or swaps the preview pack, with no request to the server. Face URLs are `/static/cards/doppeldeutsch/{token}.svg` or `/static/cards/{token}.svg`. Visible names are a client substitution on engine words: Karo→Schelle, Pik→Grün, Kreuz→Eichel, Dame→Ober, Buben→Unter, Bube→Unter. Replace `Buben` before `Bube`, so "Den Trumpf-Buben tauschen" becomes "Den Trumpf-Unter tauschen". Apply that substitution to card alt text, trump notes, the computer-action notice (including the taken trump and the marriage suit), and remaining button labels. Do not change the `data-id` or the posted action id.

Alternative: teach `action_label` and the JSON view a deck parameter. Rejected because Jev and the API should keep the French tokens, and the deck is a local display preference.

### Hide plain `play:` buttons and leave every other action

When building the actions row, skip an id that matches `play:` plus a single card token. Keep `exchange:`, `close:`, `exchange-close:`, `marry:`, the declare variants, `declare`, `continue`, `seen`, and `next-deal`. Hand clicks stay as they are: a card is clickable only when `play:{token}` is legal, and that click posts that id.

Alternative: make a click on König or Dame declare the marriage. Rejected because the plain play of that card is also legal, so one click cannot mean both.

## Risks / Trade-offs

- [The xskat picture is the German Skat pattern, not a Piatnik doppeldeutsch printing] → The suits and ranks match Schnapsen doppeldeutsch, the license is clear, and Französisch remains one click away. The attribution says where the pictures come from.
- [CC BY-SA share-alike on the new SVGs] → Vendor those files unmodified in their own directory and name the license next to them. Leave the French LGPL `LICENSE` file as it is.
- [Word substitution could miss a new label] → Cover the trump-exchange label, a Karo-Dame notice, and a marriage button in the table tests. Engine labels that name a card already use these suit and rank words.

## Migration Plan

No data migration. A browser with no stored choice keeps today's French faces and today's French wording. Removing the stored key restores that default.

## Open Questions

None. The art source, the name mapping, the shared back, and which buttons remain are fixed above.
