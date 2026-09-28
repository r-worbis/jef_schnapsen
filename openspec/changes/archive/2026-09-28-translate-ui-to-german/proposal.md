# Proposal

## Why

The Schnapsen table and deck preview still present headings, status lines, banners, and action buttons in English, while card names already use German rank and suit words. Players who expect a German table cannot read the chrome and legal-action labels without switching languages.

## What Changes

- Present every human-visible string on the table page in German, including section headings, turn and dealer lines, banners (missing key, replaced choice, computer action, deal and match results), score-row names, talon and trump notes, and aria labels for face-down cards.
- Present every human-visible string on the deck preview page in German. Card token captions (Herz-Ass and so on) stay as they are.
- Serve German labels for legal actions on the table (the same labels the API already attaches to each action id). **BREAKING** for anyone who asserted the current English `action_label` wording in tests or scripts.
- Set the table and preview documents to German (`lang="de"`).
- Leave game rules, action ids, JSON field names, card file tokens, and CLI/Jev decision prose unchanged except where a shared action label string is reused.

Assumption: “UI text” means the human table and the deck preview, not the Jev state dump or `RULES` text. Shared `action_label` strings will still become German because the table shows them.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `schnapsen-table`: Require the human table’s visible copy, including action labels, to be German.
- `schnapsen-card-faces`: Require the deck preview’s instructional copy to be German.

## Impact

- `schnapsen/page.html` chrome and JavaScript status/banner strings.
- `schnapsen/engine.py` `action_label` (and therefore `/api/state` action labels and any Jev criteria that reuse those strings).
- `schnapsen/static/cards/preview.html` title, heading, and intro paragraph.
- Tests that match English UI or action-label wording (`tests/test_table.py` and related).
- No change to HTTP routes, action ids, or card SVG filenames.
