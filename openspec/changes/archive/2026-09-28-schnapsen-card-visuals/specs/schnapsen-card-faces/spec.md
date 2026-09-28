# Spec Delta

## Purpose

Provide a license-clear twenty-card Schnapsen drawing set, a way to inspect that set, and use of those drawings on the human table after the set is accepted.

## ADDED Requirements

### Requirement: Twenty faces and one back in the project

The project SHALL contain one drawing for each of the twenty pack cards (Herz, Karo, Pik, Kreuz each with Ass, Zehner, König, Dame, and Bube) and one drawing for a face-down back. Each face SHALL be identifiable from the file set as that suit and rank. The project SHALL record the source of the drawings and the license under which they are used.

#### Scenario: Full Schnapsen pack is present

- **WHEN** a person lists the vendored card drawings
- **THEN** there is exactly one face for each of the twenty pack cards and one back

#### Scenario: Source and license are recorded

- **WHEN** a person opens the license record for the drawings
- **THEN** they can read the original source and the license name

### Requirement: Deck preview of every drawing

The system SHALL serve a local preview that shows all twenty faces and the back at once, using the vendored drawings, so a person can accept or reject the deck before those drawings are used in play.

#### Scenario: Preview shows the whole pack

- **WHEN** a person opens the deck preview
- **THEN** they see each of the twenty faces and the back

### Requirement: Table uses accepted drawings

After the deck has been accepted, the human table SHALL show the matching face drawing for every face-up card (own hand, trump while visible, cards in the current trick, and other face-up cards the table already shows) and SHALL show the back drawing for every face-down card (computer count and remaining talon). Hidden card identities SHALL still not appear as faces.

#### Scenario: Face-up cards use pack art

- **WHEN** the human seat views a dealt table after the deck is accepted
- **THEN** each of that seat's five cards and the face-up trump use the drawings for those cards

#### Scenario: Face-down cards use the back

- **WHEN** the human seat views a dealt table after the deck is accepted and the computer still holds five cards
- **THEN** the five computer cards and the face-down talon cards use the back drawing and no computer face drawing
