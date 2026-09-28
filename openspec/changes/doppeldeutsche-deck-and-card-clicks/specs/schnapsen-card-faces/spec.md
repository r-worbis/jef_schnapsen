# Spec Delta

## MODIFIED Requirements

### Requirement: Twenty faces and one back in the project

The project SHALL contain one French-suited drawing for each of the twenty pack cards (Herz, Karo, Pik, Kreuz each with Ass, Zehner, König, Dame, and Bube) and one drawing for a face-down back. Each French face SHALL be identifiable from that set as that suit and rank. The project SHALL record the source of the French drawings and the license under which they are used. The French set SHALL remain in the project when a doppeldeutsche set is also present.

#### Scenario: Full Schnapsen pack is present

- **WHEN** a person lists the vendored French card drawings
- **THEN** there is exactly one face for each of the twenty pack cards and one back

#### Scenario: Source and license are recorded

- **WHEN** a person opens the license record for the French drawings
- **THEN** they can read the original source and the license name

### Requirement: Deck preview of every drawing

The system SHALL serve a local preview that shows all twenty faces and the back of one pack at once, using the vendored drawings. The preview SHALL offer a choice of Französisch or Doppeldeutsch and SHALL show the chosen pack. Until the player has chosen, the preview SHALL show Französisch. The choice SHALL be the same choice the table uses.

#### Scenario: Preview shows the whole pack

- **WHEN** a person opens the deck preview and has not chosen a pack
- **THEN** they see each of the twenty French faces and the back

#### Scenario: Preview shows the doppeldeutsche pack

- **WHEN** a person opens the deck preview and chooses Doppeldeutsch
- **THEN** they see each of the twenty doppeldeutsche faces and the shared back, and they do not see the French faces

### Requirement: Table uses accepted drawings

The human table SHALL show the matching face drawing from the pack the player has selected for every face-up card (own hand, trump while visible, cards in the current trick, and other face-up cards the table already shows) and SHALL show the shared back drawing for every face-down card (computer count and remaining talon). Until the player has chosen, the table SHALL use the French pack. Hidden card identities SHALL still not appear as faces. Changing the selected pack SHALL NOT change which cards are in play.

#### Scenario: Face-up cards use pack art

- **WHEN** the human seat views a dealt table and has not chosen a pack
- **THEN** each of that seat's five cards and the face-up trump use the French drawings for those cards

#### Scenario: Face-up cards use the doppeldeutsche pack

- **WHEN** the human seat views a dealt table and has selected Doppeldeutsch
- **THEN** each of that seat's five cards and the face-up trump use the doppeldeutsche drawings for those cards and do not use the French drawings

#### Scenario: Face-down cards use the back

- **WHEN** the human seat views a dealt table after either pack is selected and the computer still holds five cards
- **THEN** the five computer cards and the face-down talon cards use the back drawing and no computer face drawing

### Requirement: Deck preview copy is German

The deck preview SHALL present its page title, heading, instructional paragraph, and pack-choice labels in German. French face captions SHALL remain the existing German card tokens. Doppeldeutsche face captions SHALL use the mapped names: Herz stays Herz, Karo is Schelle, Pik is Grün, Kreuz is Eichel, Dame is Ober, Bube is Unter, and Ass, Zehner, and König stay. The document language SHALL be German.

#### Scenario: Preview chrome is German

- **WHEN** a person opens the deck preview
- **THEN** the heading, the instructional paragraph, and the pack-choice labels are in German and the document language is German

#### Scenario: Doppeldeutsche caption uses the mapped name

- **WHEN** a person chooses Doppeldeutsch on the deck preview
- **THEN** the caption on the face that corresponds to Karo Dame is Schelle-Ober

## ADDED Requirements

### Requirement: Doppeldeutsche faces in the project

The project SHALL contain one doppeldeutsche drawing for each of the twenty pack cards. Each drawing SHALL be the German-suited face for that card under the mapping Herz stays Herz, Karo is Schelle, Pik is Grün, Kreuz is Eichel, Dame is Ober, Bube is Unter, and Ass, Zehner, and König stay. The project SHALL record the source of those drawings and the license under which they are used. The doppeldeutsche set SHALL NOT replace the French set or the shared back.

#### Scenario: Doppeldeutsche pack is present

- **WHEN** a person lists the vendored doppeldeutsche drawings
- **THEN** there is exactly one face for each of the twenty pack cards

#### Scenario: Doppeldeutsche source and license are recorded

- **WHEN** a person opens the license record for the doppeldeutsche drawings
- **THEN** they can read the original source and the license name
