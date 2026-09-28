# Spec Delta

## Purpose

Run one Jev decision call against a sample document and print the typed answers so a new TypeSafe key can be checked end to end.

## ADDED Requirements

### Requirement: Decide a sample document in one call

The script SHALL send one fixed sample document to Jev and request three decisions together: whether the message is urgent, which team should handle it, and how frustrated the customer appears. Urgency SHALL be a probability from 0 to 1. The team SHALL be one of billing, technical, or sales. Frustration SHALL be a score on an ordered scale from calm to very angry.

#### Scenario: Successful decision

- **WHEN** the operator runs the script with a valid API key available in the environment
- **THEN** the script prints the urgency probability, the chosen team, and the frustration score

#### Scenario: Probabilities are visible

- **WHEN** the script prints a successful decision
- **THEN** the team answer includes a probability for each team and the frustration answer includes a probability for each level

### Requirement: Stop when the API key is missing

The script SHALL exit with a non-zero status when the API key is unset or empty, and SHALL NOT print decision answers.

#### Scenario: Missing key

- **WHEN** the operator runs the script without an API key in the environment
- **THEN** the process exits non-zero and prints no urgency, team, or frustration answer

### Requirement: Leave the API key out of the repository

The script SHALL read the API key from the environment and SHALL NOT write that key into any file in the repository.

#### Scenario: Successful run does not store the key

- **WHEN** the script completes a successful decision
- **THEN** no file in the repository contains the API key
