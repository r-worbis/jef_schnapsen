# Design

## Context

See proposal.md for why. `schnapsen/page.html` is one document: a vertical stack of Computer, Trumpf und Talon, Stich, and Deine Karten, beside an aside of Augen, Noch benötigte Punkte, Bummerl, and the Jev reveal. `.layout` is `grid-template-columns: 1fr 240px`, and under 800px it collapses to one column. The script fills stable ids (`computer-hand`, `trump`, `talon`, `trick`, `your-hand`, `actions`, `eyes`, `points`, `bummerl`, `jev-toggle`, `jev-boxes`). Cards are 74×104px. A full talon draws one back per remaining card and wraps. German headings and `lang="de"` stay as specified.

## Goals / Non-Goals

**Goals:**

- One horizontal row: computer, center (trump, current talon, current trick), human.
- Score groups and the Jev reveal on a band under that row.
- Keep the existing element ids and the script that fills them.
- The `main` surface uses the full viewport width. Card size is derived from that width, with no fixed `max-width` on the page.

**Non-Goals:**

- Changing what the state API returns, which cards are hidden, or how a trick is confirmed.
- Renaming the computer heading from Computer to Jef.
- Drawing won-trick piles. The page does not render them today, and this change does not add them.
- Restyling card art or the deck preview.

## Decisions

1. **Reorder the existing sections; do not rewrite the renderer.** Move the Computer section, a center section that already holds `#trump`, `#talon`, and `#trick`, and the Deine Karten section (including `#actions`) into a three-column grid. Place the three score sections and the Jev section in a full-width band after that grid. Title, deck choice, turn line, `#notice`, and `#result` stay above the grid. The fill functions keep writing the same ids.

   Alternative: split talon and trick into two center rows built by new nodes. Rejected because the current nodes already separate those regions, and new ids would force script changes for no new information.

2. **Keep three columns even when the viewport is narrow, and fill the screen when it is wide.** Drop the rule that stacks `.layout` into one column under 800px. Drop the `max-width` on `main` so the board is always as wide as the viewport, minus padding. Size cards from viewport width (`clamp` on `vw`, height from the card aspect ratio) so they grow on a wide screen and shrink on a narrow one. If they still overflow, the page may scroll horizontally. The old stack put the computer above the player again, which this change is replacing.

   Alternative: keep a 980px or 1200px centered column. Rejected because the board would stay narrower than the available screen.

3. **Keep the center to about one card height.** Put trump, a compact overlapping talon stack (at most three backs plus the count), and the current trick in one horizontal group. Do not draw a back for every remaining talon card: that stacked nine cards high and pushed the scores off the screen. Cards are about 1.5 times the first compact trial (`clamp(72px, 9.9vw, 153px)`). A five-card hand may wrap onto a second row.

4. **Put the three score groups in one row under the cards.** Augen, Noch benötigte Punkte, and Bummerl sit side by side under the board, with the Jev button and boxes spanning the width beneath them. That replaces the old 240px aside without making the footer a second vertical page.

5. **Put title, pack choice, and turn line on one chrome row.** That removes two extra lines above the board. Banners still sit under that row when they appear.

## Risks / Trade-offs

- [Nine talon backs plus two hands are taller than a laptop] → Draw at most three overlapping backs for the talon and keep trump and trick beside that stack.
- [A shorter card makes click targets smaller] → Keep cards large enough to click on a desktop width, and only scale down as the viewport shrinks.
- [Moving the Jev boxes below the fold hides a long reveal until the player scrolls] → The toggle stays in the lower band, directly under the scores, which is where the aside content moved.

## Migration Plan

Edit `schnapsen/page.html` only. Reload the table to confirm the three columns and the lower score band. No data migration and no API change. Revert is restoring the previous grid and section order in that file.

## Open Questions

None.
