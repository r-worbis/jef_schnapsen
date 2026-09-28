# Proposal

## Why

The table only draws the French-suited pack, so a player who wants doppeldeutsche Karten cannot choose them. A legal card play is also listed again as a text button, even though clicking that card already plays it.

## What Changes

- Add a second twenty-card doppeldeutsche face set beside the current French set, with its source and license recorded. The French set stays the default.
- On the table, and on the deck preview, offer a German choice between Französisch and Doppeldeutsch. The choice applies at once to every face-up card and to player-visible card names. It does not reshuffle, and it does not change engine card tokens, action ids, or JSON field names. Assumption: the browser remembers the choice, and a first visit uses Französisch.
- Visible doppeldeutsche names follow the usual Schnapsen correspondence: Herz stays Herz, Karo is Schelle, Pik is Grün, Kreuz is Eichel, Dame is Ober, Bube is Unter, and Ass, Zehner, and König stay. Assumption: both decks share the existing card back.
- Stop offering a text button for a plain card play (`play:` with no exchange, talon close, or marriage). Clicking that card in the hand remains how the player plays it. Text buttons stay for moves a single card click cannot express: exchanging the trump jack, closing the talon, declaring a marriage, declaring 66, continuing without declaring, confirming a seen computer reply, and starting the next deal.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `schnapsen-card-faces`: The project keeps the French pack and adds a doppeldeutsche pack, the preview can show either pack, and the table draws the pack the player selected.
- `schnapsen-table`: The page offers the deck choice, names cards in that deck's language, and offers a plain card play only by clicking the card.

## Impact

- New drawings and attribution under `schnapsen/static/cards/`, plus the deck preview and `schnapsen/page.html`.
- `tests/test_card_faces.py` and `tests/test_table.py` for the second pack, the selector, and which actions are buttons.
- No change to dealing, scoring, legal action ids, or the text Jev receives. The API may still list a plain `play:` action; the page just does not render that one as a button.
