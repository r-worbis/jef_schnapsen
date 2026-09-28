# Spec Delta

## ADDED Requirements

### Requirement: Lay the board out horizontally

The page SHALL place the computer seat, the center of the table, and the human seat in one horizontal row. The computer seat's cards SHALL be to the left of the center. The human seat's cards SHALL be to the right of the center. The center SHALL contain the current trump, or the note that replaces it once the trump card is gone, the current talon, and the cards of the current trick. The title, the pack choice, and the turn line SHALL share one row above the board. Deal or match banners SHALL stay above the board. Action buttons, including the confirmation that a computer answer has been seen, SHALL stay with the human seat. Augen, the game points still needed, and the Bummerl counts SHALL be shown below that row. The control that reveals the last text sent to Jev SHALL be in that same lower area. The playing surface SHALL use the full available screen width, and the card drawings SHALL scale with that width. The page SHALL NOT keep the board in a narrower fixed-width column than the viewport. The center SHALL be one row of about one card height: trump, a compact face-down talon stack with its count, and the current trick beside each other. The page SHALL NOT stack a full face-down card for every remaining talon card. When no deal or match banner is shown, Augen, points still needed, and Bummerl SHALL be visible in the same viewport as the two hands.

#### Scenario: Opening seats face each other

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the computer seat's five face-down cards are left of the trump and talon, the human seat's five cards are right of the trump and talon, and Augen, points still needed, and Bummerl are below both hands

#### Scenario: The trick stays between the hands

- **WHEN** the current trick contains one or two cards
- **THEN** those cards are shown in the center, between the computer seat and the human seat, and are not shown inside either hand

#### Scenario: The talon stays in the center when it is closed

- **WHEN** the talon is closed
- **THEN** the closed-talon note is in the center, between the two hands

#### Scenario: Scores and the Jev control sit below the cards

- **WHEN** the page is shown during a deal
- **THEN** Augen, points still needed, Bummerl, and the Jev reveal control are below the computer hand, the center, and the human hand

#### Scenario: Play controls stay with the human seat

- **WHEN** it is the human seat's turn, or a computer answer is waiting to be confirmed
- **THEN** the offered action buttons are in the human seat's region, to the right of the center

#### Scenario: The board fills the screen width

- **WHEN** the page is shown in a viewport
- **THEN** the playing surface spans that viewport's width, and the cards scale with that width instead of remaining a fixed size inside a narrower column

#### Scenario: Title, pack, and turn share one row

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the title, the pack choice, and the turn line sit on one row above the board

#### Scenario: The talon is a short stack

- **WHEN** nine face-down talon cards remain
- **THEN** the center shows the talon count and a compact face-down stack whose height is about one card, not nine separate card heights

#### Scenario: Scores stay on the opening screen

- **WHEN** a deal has just been dealt and no deal or match banner is shown
- **THEN** Augen, points still needed, and Bummerl are visible in the same viewport as the two hands
