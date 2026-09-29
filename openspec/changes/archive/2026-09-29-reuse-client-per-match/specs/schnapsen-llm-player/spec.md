# Spec Delta

## ADDED Requirements

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
