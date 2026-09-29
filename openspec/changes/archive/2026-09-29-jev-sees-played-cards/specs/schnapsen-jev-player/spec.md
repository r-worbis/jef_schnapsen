# Spec Delta

## MODIFIED Requirements

### Requirement: Ask Jev with the computer's cards and the rules

On the computer seat's turn, the system SHALL send Jev the cards that seat currently holds, a statement of the weiches Schnapsen rules used by the game, and the public table state. The public table state SHALL include the trump card if it is still visible, the trump suit, the talon count, whether the talon is closed, the current trick, every awarded trick of the deal with both cards and which seat won it, both seats' eyes, both seats' game points still needed, both seats' Bummerl counts, and whose turn it is. The question SHALL ask which of the legal actions the computer seat should take. The legal actions SHALL be the only answers Jev is asked to choose among.

#### Scenario: Decision includes the hand and the rules

- **WHEN** it is the computer seat's turn to act
- **THEN** the request to Jev contains each card in the computer seat's hand, the rules statement, and the list of legal actions

#### Scenario: One choice is applied

- **WHEN** Jev selects one of the legal actions
- **THEN** the game applies that action and no other action for that turn

#### Scenario: Awarded tricks are listed in full

- **WHEN** both seats have won at least one trick and it is the computer seat's turn
- **THEN** the request names both cards of every awarded trick and which seat won each trick, including tricks the human seat won after its first trick

### Requirement: Keep hidden cards out of the request

The request to Jev SHALL NOT include the human seat's current card faces or the order of the face-down talon. The request SHALL include the faces of cards that have already been played in awarded tricks.

#### Scenario: Human hand is omitted

- **WHEN** the system builds the computer seat's decision request
- **THEN** the request does not contain the identity of any card still held by the human seat

#### Scenario: Talon order is omitted

- **WHEN** face-down talon cards remain and the system builds the decision request
- **THEN** the request contains the talon count and does not contain the identity of those face-down cards
