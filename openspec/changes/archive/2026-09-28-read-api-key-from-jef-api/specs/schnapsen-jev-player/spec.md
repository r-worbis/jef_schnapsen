# Spec Delta

## MODIFIED Requirements

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

### Requirement: Leave the API key out of the repository

The system SHALL NOT write the API key into any file in the repository. `jef.api` SHALL be listed in `.gitignore` so the key file is not tracked. Tests SHALL NOT print the key.

#### Scenario: A decision does not store the key

- **WHEN** a computer decision completes
- **THEN** no tracked file in the repository contains the API key

#### Scenario: Key file is ignored

- **WHEN** `jef.api` exists at the repository root
- **THEN** `.gitignore` lists `jef.api`
