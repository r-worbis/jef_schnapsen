# Spec Delta

## MODIFIED Requirements

### Requirement: Decide a sample document in one call

The script SHALL send one fixed sample document to Jev and request three decisions together: whether the message is urgent, which team should handle it, and how frustrated the customer appears. Urgency SHALL be a probability from 0 to 1. The team SHALL be one of billing, technical, or sales. Frustration SHALL be a score on an ordered scale from calm to very angry.

#### Scenario: Successful decision

- **WHEN** the operator runs the script and `jef.api` at the repository root contains a valid API key
- **THEN** the script prints the urgency probability, the chosen team, and the frustration score

#### Scenario: Probabilities are visible

- **WHEN** the script prints a successful decision
- **THEN** the team answer includes a probability for each team and the frustration answer includes a probability for each level

### Requirement: Stop when the API key is missing

The script SHALL read the API key from the file `jef.api` at the repository root and SHALL NOT read it from the environment. Tests that need a key SHALL read that same file. The script SHALL exit with a non-zero status when that file is missing, unreadable, or contains only whitespace, and SHALL NOT print decision answers.

#### Scenario: Missing key

- **WHEN** the operator runs the script and `jef.api` is missing, unreadable, or contains only whitespace
- **THEN** the process exits non-zero and prints no urgency, team, or frustration answer

#### Scenario: Environment variable does not supply the key

- **WHEN** the operator runs the script with `TYPESAFE_API_KEY` set and `jef.api` missing or whitespace-only
- **THEN** the process exits non-zero and prints no urgency, team, or frustration answer

#### Scenario: Tests use the key file

- **WHEN** a test needs an API key for the sample script
- **THEN** it uses the contents of `jef.api` and does not use `TYPESAFE_API_KEY` as a substitute

### Requirement: Leave the API key out of the repository

The script SHALL read the API key from `jef.api` and SHALL NOT write that key into any file in the repository. `jef.api` SHALL be listed in `.gitignore` so the key file is not tracked. Tests SHALL NOT print the key.

#### Scenario: Successful run does not store the key

- **WHEN** the script completes a successful decision
- **THEN** the script has not written the API key into any file

#### Scenario: Key file is ignored

- **WHEN** `jef.api` exists at the repository root
- **THEN** `.gitignore` lists `jef.api`
