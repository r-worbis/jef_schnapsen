# Spec Delta

## ADDED Requirements

### Requirement: Do not ask Jev to end a deal at sixty-six

The statement of rules sent to Jev SHALL say that a deal ends as soon as a seat has at least 66 counting eyes, with no declaration to choose. After a computer trick or marriage that reaches 66, the system SHALL NOT send a decision request whose legal actions include ending or continuing the deal.

#### Scenario: Rules describe automatic ending

- **WHEN** it is the computer seat's turn to act
- **THEN** the rules statement in the request says the deal ends at 66 without a declaration

#### Scenario: No declare-or-continue turn

- **WHEN** the computer seat has just been awarded a trick or a counting marriage that brings it to at least 66 eyes
- **THEN** the deal is ended and no decision request is sent for that ending
