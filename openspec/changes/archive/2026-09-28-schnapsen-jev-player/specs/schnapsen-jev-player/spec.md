# Spec Delta

## Purpose

Choose the computer seat's action by asking Jev, giving it that seat's own cards, the Schnapsen rules, and the public table, and applying only a legal choice.

## ADDED Requirements

### Requirement: Ask Jev with the computer's cards and the rules

On the computer seat's turn, the system SHALL send Jev the cards that seat currently holds, a statement of the weiches Schnapsen rules used by the game, and the public table state. The public table state SHALL include the trump card if it is still visible, the trump suit, the talon count, whether the talon is closed, the current trick, the computer seat's own won tricks, the human seat's first won trick, both seats' eyes, both seats' game points still needed, both seats' Bummerl counts, and whose turn it is. The question SHALL ask which of the legal actions the computer seat should take. The legal actions SHALL be the only answers Jev is asked to choose among.

#### Scenario: Decision includes the hand and the rules

- **WHEN** it is the computer seat's turn to act
- **THEN** the request to Jev contains each card in the computer seat's hand, the rules statement, and the list of legal actions

#### Scenario: One choice is applied

- **WHEN** Jev selects one of the legal actions
- **THEN** the game applies that action and no other action for that turn

### Requirement: Keep hidden cards out of the request

The request to Jev SHALL NOT include the human seat's current card faces or the order of the face-down talon. It SHALL NOT include the human seat's won tricks after that seat's first trick.

#### Scenario: Human hand is omitted

- **WHEN** the system builds the computer seat's decision request
- **THEN** the request does not contain the identity of any card still held by the human seat

#### Scenario: Talon order is omitted

- **WHEN** face-down talon cards remain and the system builds the decision request
- **THEN** the request contains the talon count and does not contain the identity of those face-down cards

### Requirement: Do not apply an illegal choice

If Jev's answer is not one of the legal actions, the system SHALL NOT apply it. The system SHALL ask Jev once more with the same hand, rules, public state, and legal actions. If the second answer is also not a legal action, or either request fails, the system SHALL apply one predetermined legal action and the table SHALL show that the computer's choice was replaced.

#### Scenario: First answer is illegal

- **WHEN** Jev's first answer is not in the legal action list
- **THEN** the deal is unchanged and Jev is asked again

#### Scenario: Second answer is illegal

- **WHEN** Jev's second answer is not in the legal action list
- **THEN** a predetermined legal action is applied and the table shows that the choice was replaced

#### Scenario: Request fails

- **WHEN** the request to Jev fails
- **THEN** a predetermined legal action is applied and the table shows that the choice was replaced

### Requirement: Stop the computer turn when the API key is missing

The system SHALL read the API key from the environment. When the key is unset or empty, the system SHALL NOT send a decision request and SHALL NOT apply a computer action. The table SHALL show that the key is missing.

#### Scenario: Missing key

- **WHEN** it becomes the computer seat's turn and the API key is unset or empty
- **THEN** no decision request is sent, no computer card is played, and the table shows that the key is missing

### Requirement: Leave the API key out of the repository

The system SHALL NOT write the API key into any file in the repository.

#### Scenario: A decision does not store the key

- **WHEN** a computer decision completes
- **THEN** no file in the repository contains the API key
