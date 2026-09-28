# schnapsen-jev-player Specification

## Purpose

Choose the computer seat's action by asking Jev, giving it that seat's own cards, the Schnapsen rules, and the public table, and applying only a legal choice.

## Requirements

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

The system SHALL read the API key from the file `jef.api` at the repository root and SHALL NOT read it from the environment. Tests that need a key SHALL read that same file. When that file is missing, unreadable, or contains only whitespace, the system SHALL NOT send a decision request and SHALL NOT apply a computer action. The table SHALL show that the key is missing and SHALL name `jef.api` as the file that supplies it.

#### Scenario: Missing key

- **WHEN** it becomes the computer seat's turn and `jef.api` is missing, unreadable, or contains only whitespace
- **THEN** no decision request is sent, no computer card is played, and the table shows that the key is missing and names `jef.api`

#### Scenario: Environment variable does not supply the key

- **WHEN** it becomes the computer seat's turn, `TYPESAFE_API_KEY` is set, and `jef.api` is missing or contains only whitespace
- **THEN** no decision request is sent, no computer card is played, and the table shows that the key is missing

#### Scenario: Key file authorizes the computer turn

- **WHEN** it becomes the computer seat's turn and `jef.api` contains a key, even if `TYPESAFE_API_KEY` is unset
- **THEN** a decision request is sent and the environment variable is not required

#### Scenario: Tests use the key file

- **WHEN** a test needs an API key for a computer turn
- **THEN** it uses the contents of `jef.api` and does not use `TYPESAFE_API_KEY` as a substitute

### Requirement: Do not ask Jev to end a deal at sixty-six

The statement of rules sent to Jev SHALL say that a deal ends as soon as a seat has at least 66 counting eyes, with no declaration to choose. After a computer trick or marriage that reaches 66, the system SHALL NOT send a decision request whose legal actions include ending or continuing the deal.

#### Scenario: Rules describe automatic ending

- **WHEN** it is the computer seat's turn to act
- **THEN** the rules statement in the request says the deal ends at 66 without a declaration

#### Scenario: No declare-or-continue turn

- **WHEN** the computer seat has just been awarded a trick or a counting marriage that brings it to at least 66 eyes
- **THEN** the deal is ended and no decision request is sent for that ending

### Requirement: Keep the last request and answers for the table

When a computer turn sends a decision request, the system SHALL keep the rules statement from that request, the remainder of that request, and each answer Jev returned, in order. The remainder SHALL be the cards, public table, and legal actions that were sent with the rules. A second request on the same turn SHALL add its answer after the first and SHALL NOT replace the rules statement or the remainder, because both requests use the same text. A failed request SHALL be kept as a failure with no answer text. A later computer turn that sends a new request SHALL replace the kept exchange. A turn that sends no request SHALL leave the kept exchange unchanged. The kept exchange SHALL NOT include the API key. Keeping the exchange SHALL NOT change which action is applied.

#### Scenario: A legal answer is kept with the request

- **WHEN** Jev returns one legal action
- **THEN** the kept exchange contains the rules statement, the remainder of that request, and that answer, and the game applies that action

#### Scenario: Both answers from one turn are kept

- **WHEN** the first answer is not legal and the second answer is legal
- **THEN** the kept exchange lists the first answer and then the second, with one rules statement and one remainder, and the game applies the second answer

#### Scenario: A failed request is kept without an answer

- **WHEN** the decision request fails
- **THEN** the kept exchange records the failure with no answer text, and the game applies the predetermined legal action

#### Scenario: A turn with no request leaves the exchange

- **WHEN** a previous request is kept and the next computer turn sends no request
- **THEN** the kept rules, remainder, and answers stay as they were

#### Scenario: The key is not kept

- **WHEN** a decision request is kept
- **THEN** the kept rules, remainder, and answers do not contain the API key

### Requirement: Leave the API key out of the repository

The system SHALL NOT write the API key into any file in the repository. `jef.api` SHALL be listed in `.gitignore` so the key file is not tracked. Tests SHALL NOT print the key.

#### Scenario: A decision does not store the key

- **WHEN** a computer decision completes
- **THEN** no tracked file in the repository contains the API key

#### Scenario: Key file is ignored

- **WHEN** `jef.api` exists at the repository root
- **THEN** `.gitignore` lists `jef.api`
