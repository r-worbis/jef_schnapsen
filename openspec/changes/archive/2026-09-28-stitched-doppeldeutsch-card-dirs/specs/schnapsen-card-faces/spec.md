# Spec Delta

## MODIFIED Requirements

### Requirement: Twenty faces and one back in the project

The project SHALL contain one French-suited drawing for each of the twenty pack cards (Herz, Karo, Pik, Kreuz each with Ass, Zehner, König, Dame, and Bube) and one drawing for a face-down back. The French faces SHALL live in a `french` directory and SHALL NOT sit beside the back. The back SHALL stay in the parent card directory, shared by both packs, and SHALL NOT be copied into `french` or `doppeldeutsch`. Each French face SHALL be identifiable from that set as that suit and rank. The project SHALL record the source of the French drawings and the license under which they are used. The French set SHALL remain in the project when a doppeldeutsche set is also present.

#### Scenario: Full Schnapsen pack is present

- **WHEN** a person lists the vendored French card drawings
- **THEN** there is exactly one face for each of the twenty pack cards in the `french` directory and the back is not in that directory

#### Scenario: Shared back stays beside both packs

- **WHEN** a person lists the parent card directory
- **THEN** the back drawing is there, and the twenty French faces are not stored beside it

#### Scenario: Source and license are recorded

- **WHEN** a person opens the license record for the French drawings
- **THEN** they can read the original source and the license name

### Requirement: Deck preview of every drawing

The system SHALL serve a local preview that shows all twenty faces and the shared back of one pack at once, using the vendored drawings. The preview SHALL offer a choice of Französisch or Doppeldeutsch and SHALL show the chosen pack. Until the player has chosen, the preview SHALL show Französisch. French faces SHALL load from the `french` directory. Doppeldeutsche faces SHALL load from the `doppeldeutsch` directory. The back SHALL load from the parent card directory. The choice SHALL be the same choice the table uses.

#### Scenario: Preview shows the whole pack

- **WHEN** a person opens the deck preview and has not chosen a pack
- **THEN** they see each of the twenty French faces from the `french` directory and the shared back, and they do not see the doppeldeutsche faces

#### Scenario: Preview shows the doppeldeutsche pack

- **WHEN** a person opens the deck preview and chooses Doppeldeutsch
- **THEN** they see each of the twenty doppeldeutsche faces from the `doppeldeutsch` directory and the shared back, and they do not see the French faces

### Requirement: Table uses accepted drawings

The human table SHALL show the matching face drawing from the pack the player has selected for every face-up card (own hand, trump while visible, cards in the current trick, and other face-up cards the table already shows) and SHALL show the shared back drawing for every face-down card (computer count and remaining talon). Until the player has chosen, the table SHALL use the French pack. French face URLs SHALL be under the `french` directory. Doppeldeutsche face URLs SHALL be under the `doppeldeutsch` directory. The back URL SHALL stay in the parent card directory. Hidden card identities SHALL still not appear as faces. Changing the selected pack SHALL NOT change which cards are in play.

#### Scenario: Face-up cards use pack art

- **WHEN** the human seat views a dealt table and has not chosen a pack
- **THEN** each of that seat's five cards and the face-up trump use the French drawings from the `french` directory

#### Scenario: Face-up cards use the doppeldeutsche pack

- **WHEN** the human seat views a dealt table and has selected Doppeldeutsch
- **THEN** each of that seat's five cards and the face-up trump use the doppeldeutsche drawings from the `doppeldeutsch` directory and do not use the French drawings

#### Scenario: Face-down cards use the back

- **WHEN** the human seat views a dealt table after either pack is selected and the computer still holds five cards
- **THEN** the five computer cards and the face-down talon cards use the shared back drawing and no computer face drawing

## ADDED Requirements

### Requirement: Doppeldeutsche faces are full Tell cards

The project SHALL contain one doppeldeutsche drawing for each of the twenty pack cards, stored in the `doppeldeutsch` directory and addressed by the same engine tokens as the French faces. Each drawing SHALL be the Wilhelm-Tell face published for that card at `https://schnopsn.com/images/ddeutsch/`, under the mapping Pik is Grün, Kreuz is Eichel, Herz stays Herz, Karo is Schellen, Ass is 11, Zehner is 10, König is 04, Dame is Ober (03), and Bube is Unter (02). The project SHALL NOT use the smaller article crops whose file names end in `_2`. Each vendored face SHALL be one full card that still shows its picture after a half turn: a published picture that is only the upright half SHALL be joined to a 180° copy of that same picture, and a published picture that is already a full double-ended card SHALL be kept as that card and SHALL NOT be joined to a second copy of itself. The project SHALL record `https://schnopsn.com/doppeldeutsche-karten` as the source of those drawings. The doppeldeutsche set SHALL NOT replace the French set or the shared back.

#### Scenario: Doppeldeutsche pack is present

- **WHEN** a person lists the vendored doppeldeutsche drawings
- **THEN** there is exactly one face for each of the twenty pack cards and none of those files is the previous Wikimedia SVG set

#### Scenario: Upright half becomes a full card

- **WHEN** a person opens the vendored face for Pik Bube
- **THEN** that face is a full upright card whose lower half is the upper half turned 180°

#### Scenario: Already-full card is not stacked twice

- **WHEN** a person opens the vendored face for Pik König
- **THEN** that face is the published full card and is not two copies of that card stacked together

#### Scenario: Doppeldeutsche source is recorded

- **WHEN** a person opens the license record for the doppeldeutsche drawings
- **THEN** they can read `https://schnopsn.com/doppeldeutsche-karten` as the source, and the record does not name the Wikimedia Skat set as that source
