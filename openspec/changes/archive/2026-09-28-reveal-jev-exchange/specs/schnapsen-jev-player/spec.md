# Spec Delta

## ADDED Requirements

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
