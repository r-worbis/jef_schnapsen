# Design

## Context

See proposal.md. `jev_parts` currently lists `deal.tricks["computer"]` in full and `deal.tricks["human"][:1]`. Each stored trick is `[lead_card, follow_card]`. The human page still hides later computer tricks and is not part of this change.

## Goals / Non-Goals

**Goals:**

- Put every awarded trick into the Jev remainder with both faces and the winning seat.
- Leave the human JSON trick fields as they are.

**Non-Goals:**

- Reconstruct who led each awarded trick as a separate line (lead vs follow order is already in the pile).
- A running "cards still out" inventory distinct from the trick list.
- Showing the opponent hand or face-down talon order.

## Decisions

### Replace the truncated opponent line with both piles

In `jev_parts`, emit one line for the computer's awarded tricks and one for the human's awarded tricks, both using the existing `_tricks_text` helper over the full lists. Drop the `[:1]` slice for the opponent. Name the seats in the labels so Jev can tell who won which pile.

Keep "Current trick" as the incomplete play. Do not add a second flattened "all played cards" list; the two piles plus the current trick are the played cards.

Alternative: a chronological log of every card with seat. That would need extra engine history. The piles already have every played face.

### Tests assert Jev, not the table

Extend the Jev-state tests so a second human-won trick appears in the request. Leave `opponentFirstTrick` on `human_view` unchanged.

## Risks / Trade-offs

- [The Jev reveal box on the page will show later computer-won tricks inside the remainder string] → Accepted. Those cards are already public play; the rest of the table still hides the computer hand.
- [Longer state documents] → A 20-card deal is a few extra lines.

## Migration Plan

None. Next computer turn uses the new remainder. Rollback is reverting `jev_parts` and the tests.

## Open Questions

None.
