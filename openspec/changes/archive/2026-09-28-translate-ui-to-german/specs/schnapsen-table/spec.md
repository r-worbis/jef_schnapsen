# Spec Delta

## ADDED Requirements

### Requirement: Table copy is German

The human table SHALL present its headings, turn and dealer lines, score-row names, talon and trump notes, banners, action button labels, and face-down card names in German. Action ids, JSON field names, and card tokens SHALL stay unchanged. The document language SHALL be German.

#### Scenario: Opening chrome is German

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the section headings and the dealer and turn line are in German, and the document language is German

#### Scenario: Action buttons are German

- **WHEN** it is the human seat's turn and legal actions include playing a card, exchanging the trump Bube, closing the talon, declaring a marriage, or declaring 66
- **THEN** each offered action's visible label is German and the action id is the same as before

#### Scenario: Result banners are German

- **WHEN** a deal or the match ends, or the table reports a missing API key or a replaced computer choice
- **THEN** the banner text shown to the human seat is German
