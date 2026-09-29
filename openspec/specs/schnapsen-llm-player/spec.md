# schnapsen-llm-player Specification

## Purpose

Ask ChatGPT which card the LLM seat plays, using the same decision facts Jev already receives, and leave acceptance of that play to the engine.

## Requirements

### Requirement: Ask ChatGPT with the same facts as Jev

When it is the turn of a seat bound to the LLM, the system SHALL send ChatGPT the same own cards, the same public table, and the same legal actions that a Jev request for that seat would contain. The rules statement SHALL be the same statement a Jev request would contain, and it SHALL appear in exactly one message of that seat's conversation: the first message. Every later request of that conversation SHALL include that first message unchanged and SHALL NOT repeat the rules statement in any later message. The new user message on each turn SHALL contain the current hand, the public table, and the legal actions. The public table SHALL include the trump card if it is still visible, the trump suit, the talon count, whether the talon is closed, the current trick, every awarded trick of the deal with both cards and which seat won it, both seats' eyes, both seats' game points still needed, both seats' Bummerl counts, and whose turn it is. The question SHALL ask which of those legal actions to play now. The model SHALL be `gpt-6-sol`. The request SHALL NOT include the opponent's current card faces or the order of the face-down talon. The request SHALL NOT include the API key.

#### Scenario: The question matches the Jev facts

- **WHEN** it is the LLM seat's turn
- **THEN** the request contains each card in that seat's hand, the rules statement exactly once, and each legal action that a Jev request for that same position would list

#### Scenario: A later turn does not repeat the rules

- **WHEN** the same LLM seat is asked again later in the same deal
- **THEN** the new user message contains that seat's current hand and legal actions, and the rules statement appears only in the unchanged first message

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

If the reply is not a legal action, the system SHALL NOT apply it. The system SHALL ask ChatGPT once more with the same message list. The rejected reply SHALL NOT be added to the conversation. If the second reply is also not a legal action, the system SHALL apply one predetermined legal action and the table SHALL show that the choice was replaced. If the call fails, the system SHALL NOT ask again, SHALL apply that same predetermined legal action, and SHALL show that the choice was replaced. A refused reply SHALL leave the cards, eyes, and scores unchanged until a legal action is applied. Once the talon is exhausted or closed, a reply that breaks Farbzwang or Stichzwang SHALL be one of these refused replies.

#### Scenario: The first reply is illegal

- **WHEN** the first reply is not a legal action and the call itself succeeded
- **THEN** the deal is unchanged, ChatGPT is asked again with the same message list, and that list does not include the rejected reply

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

### Requirement: One deal is one conversation per LLM seat

For each seat bound to the LLM, the system SHALL keep one conversation for the current deal. A later deal of the same match SHALL start a new conversation for each LLM seat and SHALL NOT include messages from the previous deal. One seat's conversation SHALL NOT contain a card the other seat still holds. A turn by Jev or by the random player SHALL NOT add a message to an LLM conversation.

#### Scenario: A later deal starts a new conversation

- **WHEN** an LLM seat has been asked during a deal and is asked again in a later deal of the same match
- **THEN** the later request does not contain the previous deal's messages, and the rules statement appears once in its first message

#### Scenario: Two LLM seats stay separate

- **WHEN** both seats are bound to the LLM and one seat has been asked
- **THEN** the other seat's request does not contain any card the first seat still holds

### Requirement: Keep a cacheable prefix

The system SHALL send each LLM seat's conversation as an append-only message list for the current deal. Messages already sent for that seat in that deal SHALL be repeated unchanged, in the same order, at the start of every later request of that deal. The first message SHALL contain the rules statement and SHALL NOT contain the current hand, the legal actions, or a timestamp. After an LLM turn applies an action, the conversation SHALL append the user message for that position and one assistant message for the action that was applied. When the applied action came from an accepted reply, the assistant message SHALL be that reply. When the applied action is the predetermined replacement, the assistant message SHALL name that action and SHALL NOT include the rejected reply or the failed call. Each request SHALL include a cache key that is the same for every turn of that seat in that deal, different for the other seat, and different after a new deal starts.

#### Scenario: The next request keeps the previous prefix

- **WHEN** an LLM seat's reply is applied and that seat is asked again in the same deal
- **THEN** the new request begins with the previous request's messages, unchanged, followed by that reply and the new user message

#### Scenario: A replaced action is what the next turn sees

- **WHEN** both replies on an LLM turn are not legal actions and the predetermined action is applied
- **THEN** the next request's assistant message for that turn names the predetermined action and does not include the rejected replies

#### Scenario: The first message stays free of the hand

- **WHEN** the system sends the first request of a deal for an LLM seat
- **THEN** the first message contains the rules statement and does not contain the cards in that seat's hand

#### Scenario: The cache key stays with the seat

- **WHEN** the same LLM seat is asked twice in one deal and the other seat is also bound to the LLM
- **THEN** both requests for the first seat use one cache key, and the other seat's request uses a different cache key

#### Scenario: A new deal uses a new cache key

- **WHEN** an LLM seat is asked in one deal and asked again in the next deal of the same match
- **THEN** the two requests use different cache keys

### Requirement: Reuse one ChatGPT connection for a match

A match that sends a live ChatGPT request SHALL open one connection for that match and SHALL use that same connection for every live ChatGPT request of that match. That includes the second request after an illegal reply, later deals of the same match, and an LLM seat on either side. The connection SHALL stay open between those requests. When the next match starts, the system SHALL close the connection of the match that is ending and SHALL open a different connection for the new match on its first live ChatGPT request. A match that sends no live ChatGPT request SHALL open no ChatGPT connection. A scripted reply SHALL NOT open one. The ChatGPT connection SHALL be separate from the client that sends Jev decision requests: a Jev request SHALL NOT open or use the ChatGPT connection, and a ChatGPT request SHALL NOT open or use the Jev client. A match in which one seat is Jev and the other is the LLM SHALL hold one of each.

#### Scenario: Two turns share the connection

- **WHEN** a match sends a live ChatGPT request and a later turn of that same match sends another
- **THEN** both requests use the connection opened for that match, and that connection is still open after the first request

#### Scenario: The retry uses the same connection

- **WHEN** the first reply of a turn is not a legal action and ChatGPT is asked again
- **THEN** the second request uses the same connection as the first request of that turn

#### Scenario: The next deal keeps the connection

- **WHEN** a match sends a live ChatGPT request, that deal ends, another deal of the same match starts, and that deal sends a live ChatGPT request
- **THEN** the later request uses the connection opened for that match

#### Scenario: Both seats share the connection

- **WHEN** both seats of a match are the LLM and each seat sends a live ChatGPT request
- **THEN** both requests use the one connection opened for that match

#### Scenario: The next match opens a new connection

- **WHEN** a match has sent a live ChatGPT request and the next match sends a live ChatGPT request
- **THEN** the first match's connection is closed and the next match's request uses a different connection

#### Scenario: A scripted reply opens no connection

- **WHEN** the LLM seat answers from a scripted reply
- **THEN** no ChatGPT connection is opened

#### Scenario: Jev and the LLM each keep their own client

- **WHEN** one seat of a match is Jev, the other is the LLM, and each sends a request
- **THEN** the match has one Jev client and one ChatGPT connection, and neither request uses the other's client
