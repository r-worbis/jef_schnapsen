# Design

## Context

See proposal.md for why. French faces are the twenty `{token}.svg` files in `schnapsen/static/cards/`, next to `back.svg`, `LICENSE`, `ATTRIBUTION.md`, and `preview.html`. `tests/test_card_faces.py` asserts that top-level `*.svg` set is exactly those twenty faces plus `back.svg`. Doppeldeutsch is twenty Wikimedia SVGs in `schnapsen/static/cards/doppeldeutsch/`, and both `page.html` and `preview.html` build `/static/cards/doppeldeutsch/{token}.svg` or `/static/cards/{token}.svg`. The unarchived change `doppeldeutsche-deck-and-card-clicks` still describes that Wikimedia layout.

The Tell faces are the PNGs at `https://schnopsn.com/images/ddeutsch/`, not the smaller `_2` crops embedded in the article. Suit prefixes are `PI` Pik, `KR` Kreuz, `HE` Herz, `KA` Karo. Rank numbers are `11` Ass, `10` Zehner, `04` König, `03` Ober (Dame), `02` Unter (Bube). Twelve of those files are the upright half (about 209–211px tall). Eight are already a full double-ended card (434px tall): `PI04`, `PI10`, `KR04`, `KR10`, `HE04`, `HE10`, `KA03`, `KA10`.

## Goals / Non-Goals

**Goals:**

- Vendor one full doppeldeutsche face per engine token, built from those twenty PNGs.
- Store French faces in `french/` and doppeldeutsche faces in `doppeldeutsch/`, and point the preview and the table at those directories.

**Non-Goals:**

- A new card back, a change to the Französisch / Doppeldeutsch control, or a change to visible name mapping.
- Using the `_2` article crops, the Skat 7/8/9, or the Wikimedia SVGs.
- Changing engine tokens, action ids, or the text sent to Jev.

## Decisions

### Build each face from the full-size PNG, then stitch only the halves

Download `{PI|KR|HE|KA}{02|03|04|10|11}.png`. If the bitmap is taller than 300px, copy it unchanged. Otherwise paste the bitmap on top and a 180° rotation of that same bitmap directly under it, with no gap and no scaling. That lines the cut edge up with itself, so the lower half is the upper half inverted and the card still reads either way up.

| Engine token | Source |
| --- | --- |
| Pik-Bube, Pik-Dame, Pik-König, Pik-Zehner, Pik-Ass | `PI02`, `PI03`, `PI04`, `PI10`, `PI11` |
| Kreuz-Bube, Kreuz-Dame, Kreuz-König, Kreuz-Zehner, Kreuz-Ass | `KR02`, `KR03`, `KR04`, `KR10`, `KR11` |
| Herz-Bube, Herz-Dame, Herz-König, Herz-Zehner, Herz-Ass | `HE02`, `HE03`, `HE04`, `HE10`, `HE11` |
| Karo-Bube, Karo-Dame, Karo-König, Karo-Zehner, Karo-Ass | `KA02`, `KA03`, `KA04`, `KA10`, `KA11` |

Write `schnapsen/static/cards/doppeldeutsch/{token}.png` and delete the twenty `.svg` files there. Widths differ by a few pixels (281–290); keep each file's own width. The static handler already picks `image/png` from the file name.

Alternative: stitch every file, including the 434px cards. Rejected because those are already double-ended and a second join would stack two full cards. Alternative: use the `_2` crops. Rejected because they are smaller article illustrations, and König and Zehner have no `_2` file except `KA04_2`.

### Move only the French faces

Move the twenty `{token}.svg` files to `schnapsen/static/cards/french/`. Leave `back.svg`, `LICENSE`, `ATTRIBUTION.md`, and `preview.html` in `schnapsen/static/cards/`.

`page.html` face URLs become `/static/cards/french/{token}.svg` or `/static/cards/doppeldeutsch/{token}.png`. The back URL stays `/static/cards/back.svg`. `preview.html` uses the same relative paths (`french/…`, `doppeldeutsch/….png`, `back.svg`).

In `ATTRIBUTION.md`, replace the doppeldeutsch Wikimedia / CC BY-SA section with the source page `https://schnopsn.com/doppeldeutsche-karten`, the image base `https://schnopsn.com/images/ddeutsch/`, the token mapping, and a note that the page does not publish a reuse license. Leave the French Bellot / LGPL section and `LICENSE` as they are.

Alternative: name the directory `franzoesisch` to match the control value. Rejected because the request names the directory `french`. The stored choice value stays `franzoesisch`.

## Risks / Trade-offs

- [The article does not publish a reuse license] → Record the source URL and that fact. Do not attach the old CC BY-SA line to these PNGs. The French LGPL files stay under their own license.
- [Half-card bitmaps include a black margin and are not all the same width] → Join each bitmap to its own rotation, so the two halves match. Do not crop or force one canvas size.
- [`doppeldeutsche-deck-and-card-clicks` is complete but not archived, and its delta still requires Wikimedia SVGs and top-level French paths] → Archive that change before this one, or its card-face delta will fight this layout. This change is the later file layout and art.

## Migration Plan

Move the French files, replace the doppeldeutsch files, then update the two pages, the attribution, and `tests/test_card_faces.py`. Old URLs `/static/cards/{token}.svg` and `/static/cards/doppeldeutsch/{token}.svg` stop working. A stored `schnapsen-deck` value needs no migration. Putting the French SVGs back at the top level and restoring the Wikimedia SVGs reverses the file move.

## Open Questions

None. Which source file maps to which token, which twelve files are stitched, and where the back stays are fixed above.
