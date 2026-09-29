# Spec Delta

## MODIFIED Requirements

### Requirement: Ask Jev with the computer's cards and the rules

On the turn of a seat whose player is Jev, the system SHALL send Jev the cards that seat currently holds, a statement of the weiches Schnapsen rules used by the game, and the public table state. The public table state SHALL include the trump card if it is still visible, the trump suit, the talon count, whether the talon is closed, the current trick, every awarded trick of the deal with both cards and which seat won it, both seats' eyes, both seats' game points still needed, both seats' Bummerl counts, and whose turn it is. The question SHALL ask which of the legal actions that seat should take. The legal actions SHALL be the only answers Jev is asked to choose among. The seat MAY be the left seat or the right seat.

#### Scenario: Decision includes the hand and the rules

- **WHEN** it is the left seat's turn to act and that seat's player is Jev
- **THEN** the request to Jev contains each card in the left seat's hand, the rules statement, and the list of legal actions

#### Scenario: Jev on the right receives that seat's cards

- **WHEN** it is the right seat's turn to act and that seat's player is Jev
- **THEN** the request contains each card in the right seat's hand and does not contain a card still held by the left seat

#### Scenario: One choice is applied

- **WHEN** Jev selects one of the legal actions
- **THEN** the game applies that action and no other action for that turn

#### Scenario: Awarded tricks are listed in full

- **WHEN** both seats have won at least one trick and it is a Jev seat's turn
- **THEN** the request names both cards of every awarded trick and which seat won each trick, including tricks the other seat won after its first trick

### Requirement: Keep hidden cards out of the request

The request to Jev SHALL NOT include the opposing seat's current card faces or the order of the face-down talon. The request SHALL include the faces of cards that have already been played in awarded tricks.

#### Scenario: Human hand is omitted

- **WHEN** Jev is playing the left seat and the system builds that seat's decision request
- **THEN** the request does not contain the identity of any card still held by the right seat

#### Scenario: The left hand is omitted when Jev sits on the right

- **WHEN** Jev is playing the right seat and the system builds that seat's decision request
- **THEN** the request does not contain the identity of any card still held by the left seat

#### Scenario: Talon order is omitted

- **WHEN** face-down talon cards remain and the system builds the decision request
- **THEN** the request contains the talon count and does not contain the identity of those face-down cards

### Requirement: Stop the computer turn when the API key is missing

The system SHALL read the API key from the file `jef.api` at the repository root and SHALL NOT read it from the environment. Tests that need a key SHALL read that same file. When it is a Jev seat's turn and that file is missing, unreadable, or contains only whitespace, the system SHALL NOT send a decision request and SHALL NOT apply an action for that seat. The table SHALL show that the key is missing and SHALL name `jef.api` as the file that supplies it. This stop SHALL NOT apply on a turn whose player is the stub.

#### Scenario: Missing key

- **WHEN** it becomes a Jev seat's turn and `jef.api` is missing, unreadable, or contains only whitespace
- **THEN** no decision request is sent, no card is played for that seat, and the table shows that the key is missing and names `jef.api`

#### Scenario: Environment variable does not supply the key

- **WHEN** it becomes a Jev seat's turn, `TYPESAFE_API_KEY` is set, and `jef.api` is missing or contains only whitespace
- **THEN** no decision request is sent, no card is played for that seat, and the table shows that the key is missing

#### Scenario: Key file authorizes the computer turn

- **WHEN** it becomes a Jev seat's turn and `jef.api` contains a key, even if `TYPESAFE_API_KEY` is unset
- **THEN** a decision request is sent and the environment variable is not required

#### Scenario: Tests use the key file

- **WHEN** a test needs an API key for a Jev turn
- **THEN** it uses the contents of `jef.api` and does not use `TYPESAFE_API_KEY` as a substitute

#### Scenario: A stub turn ignores the missing key

- **WHEN** it is the stub's turn and `jef.api` is missing
- **THEN** the stub's turn is still taken and the table does not show that the key is missing

### Requirement: Do not ask Jev to end a deal at sixty-six

The statement of rules sent to Jev SHALL say that a deal ends as soon as a seat has at least 66 counting eyes, with no declaration to choose. After a trick or marriage of a seat played by Jev that reaches 66, the system SHALL NOT send a decision request whose legal actions include ending or continuing the deal. This SHALL hold whether Jev is playing the left seat or the right seat.

#### Scenario: Rules describe automatic ending

- **WHEN** it is a Jev seat's turn to act
- **THEN** the rules statement in the request says the deal ends at 66 without a declaration

#### Scenario: No declare-or-continue turn

- **WHEN** a seat played by Jev has just been awarded a trick or a counting marriage that brings it to at least 66 eyes
- **THEN** the deal is ended and no decision request is sent for that ending

### Requirement: Keep the last request and answers for the table

When a Jev turn sends a decision request, the system SHALL keep the rules statement from that request, the remainder of that request, and each answer Jev returned, in order. The remainder SHALL be the cards, public table, and legal actions that were sent with the rules. A second request on the same turn SHALL add its answer after the first and SHALL NOT replace the rules statement or the remainder, because both requests use the same text. A failed request SHALL be kept as a failure with no answer text. A later Jev turn that sends a new request SHALL replace the kept exchange, whichever seat Jev is playing. A turn that sends no request, including a turn played by the stub, SHALL leave the kept exchange unchanged. The kept exchange SHALL NOT include the API key. Keeping the exchange SHALL NOT change which action is applied.

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

- **WHEN** a previous request is kept and the next Jev turn sends no request
- **THEN** the kept rules, remainder, and answers stay as they were

#### Scenario: A stub turn leaves the exchange

- **WHEN** a previous Jev request is kept and the next turn is played by the stub
- **THEN** the kept rules, remainder, and answers stay as they were, and no new request is added

#### Scenario: The key is not kept

- **WHEN** a decision request is kept
- **THEN** the kept rules, remainder, and answers do not contain the API key
