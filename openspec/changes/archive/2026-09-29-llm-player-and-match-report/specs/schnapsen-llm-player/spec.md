# Spec Delta

## Purpose

Ask ChatGPT which card the LLM seat plays, using the same decision facts Jev already receives, and leave acceptance of that play to the engine.

## ADDED Requirements

### Requirement: Ask ChatGPT with the same facts as Jev

When it is the turn of a seat bound to the LLM, the system SHALL send ChatGPT the same rules statement, the same own cards, the same public table, and the same legal actions that a Jev request for that seat would contain. The public table SHALL include the trump card if it is still visible, the trump suit, the talon count, whether the talon is closed, the current trick, every awarded trick of the deal with both cards and which seat won it, both seats' eyes, both seats' game points still needed, both seats' Bummerl counts, and whose turn it is. The question SHALL ask which of those legal actions to play now. The model SHALL be `gpt-6-sol`. The request SHALL NOT include the opponent's current card faces or the order of the face-down talon. The request SHALL NOT include the API key.

#### Scenario: The question matches the Jev facts

- **WHEN** it is the LLM seat's turn
- **THEN** the ChatGPT question contains each card in that seat's hand, the rules statement, and each legal action that a Jev request for that same position would list

#### Scenario: The opponent's hand is omitted

- **WHEN** the system builds the ChatGPT question
- **THEN** the question does not contain the identity of any card still held by the other seat

#### Scenario: The model is gpt-6-sol

- **WHEN** the system sends the ChatGPT question
- **THEN** the request names the model `gpt-6-sol`

#### Scenario: The random player is not asked

- **WHEN** it is the random player's turn
- **THEN** no ChatGPT request is sent

### Requirement: The reply is the played card

The system SHALL treat a reply as the played card only when the reply is one legal action id, or when the reply is one card token or one card label and exactly one legal action plays that card. The system SHALL propose that action and SHALL NOT apply it itself. Any other reply SHALL NOT be applied.

#### Scenario: An action id is the proposal

- **WHEN** the reply is exactly one legal action id
- **THEN** that action is the proposal

#### Scenario: One card names one legal action

- **WHEN** the reply is one card in the seat's hand and exactly one legal action plays that card
- **THEN** that action is the proposal

#### Scenario: One card names several actions

- **WHEN** the reply names a card that more than one legal action would play
- **THEN** the reply is not applied and the deal is unchanged

### Requirement: Do not apply an illegal reply

If the reply is not a legal action, the system SHALL NOT apply it. The system SHALL ask ChatGPT once more with the same question. If the second reply is also not a legal action, the system SHALL apply one predetermined legal action and the table SHALL show that the choice was replaced. If the call fails, the system SHALL NOT ask again, SHALL apply that same predetermined legal action, and SHALL show that the choice was replaced. A refused reply SHALL leave the cards, eyes, and scores unchanged until a legal action is applied. Once the talon is exhausted or closed, a reply that breaks Farbzwang or Stichzwang SHALL be one of these refused replies.

#### Scenario: The first reply is illegal

- **WHEN** the first reply is not a legal action and the call itself succeeded
- **THEN** the deal is unchanged and ChatGPT is asked again with the same question

#### Scenario: The second reply is illegal

- **WHEN** the second reply is not a legal action
- **THEN** a predetermined legal action is applied and the table shows that the choice was replaced

#### Scenario: The call fails

- **WHEN** the call to ChatGPT fails
- **THEN** a predetermined legal action is applied, ChatGPT is not asked again on that turn, and the table shows that the choice was replaced

#### Scenario: Farbzwang is still refused

- **WHEN** the talon is exhausted, the LLM holds a card of the led suit, and the reply names a card of another suit
- **THEN** that reply is not applied, the trick is unchanged, and the same seat is still to play

### Requirement: Stop the LLM turn when chat.api is missing

The system SHALL read the ChatGPT API key from the file `chat.api` at the repository root and SHALL NOT read it from the environment. When that file is missing, unreadable, or contains only whitespace, the system SHALL NOT call ChatGPT and SHALL NOT apply an LLM action. The table SHALL show that the key is missing and SHALL name `chat.api`. A missing or empty `jef.api` SHALL NOT by itself stop the LLM. A missing or empty `chat.api` SHALL NOT by itself stop Jev or the random player.

#### Scenario: Missing chat key

- **WHEN** it becomes the LLM seat's turn and `chat.api` is missing, unreadable, or blank
- **THEN** no ChatGPT request is sent, no LLM card is played, and the table names `chat.api`

#### Scenario: The environment does not supply the chat key

- **WHEN** it becomes the LLM seat's turn, an environment variable holds a key, and `chat.api` is missing or blank
- **THEN** no ChatGPT request is sent and no LLM card is played

#### Scenario: Jev's key does not authorize the LLM

- **WHEN** it becomes the LLM seat's turn, `jef.api` contains a key, and `chat.api` is missing or blank
- **THEN** no ChatGPT request is sent and no LLM card is played

#### Scenario: The chat key does not stop Jev

- **WHEN** it becomes a Jev seat's turn, `jef.api` contains a key, and `chat.api` is missing
- **THEN** the missing `chat.api` file does not stop the Jev request

### Requirement: Leave the chat API key out of the repository

The system SHALL NOT write the ChatGPT API key into any file in the repository. `chat.api` SHALL be listed in `.gitignore` so the key file is not tracked. Tests SHALL NOT print the key. The HTML report SHALL NOT contain the key.

#### Scenario: A decision does not store the key

- **WHEN** an LLM decision completes
- **THEN** no tracked file in the repository contains the ChatGPT API key

#### Scenario: The chat key file is ignored

- **WHEN** `chat.api` exists at the repository root
- **THEN** `.gitignore` lists `chat.api`
