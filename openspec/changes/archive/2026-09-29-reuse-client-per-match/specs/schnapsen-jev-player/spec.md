# Spec Delta

## ADDED Requirements

### Requirement: Reuse one decision client for a match

A match that sends a decision request to Jev SHALL open one client for that match and SHALL use that same client for every decision request of that match. That includes the second request after an illegal answer, later deals of the same match, and a Jev seat on either side. The client SHALL stay open between those requests. When the next match starts, the system SHALL close the client of the match that is ending and SHALL open a different client for the new match on its first decision request. A match that sends no decision request SHALL open no client. A client supplied for the match SHALL be used for its decision requests and SHALL NOT be opened or closed by the system.

#### Scenario: Two turns share the client

- **WHEN** a match sends a decision request and a later turn of that same match sends another
- **THEN** both requests use the client opened for that match, and that client is still open after the first request

#### Scenario: The retry uses the same client

- **WHEN** the first answer of a turn is not a legal action and Jev is asked again
- **THEN** the second request uses the same client as the first request of that turn

#### Scenario: The next deal keeps the client

- **WHEN** a match sends a decision request, that deal ends, another deal of the same match starts, and that deal sends a decision request
- **THEN** the later request uses the client opened for that match

#### Scenario: Both seats share the client

- **WHEN** both seats of a match are Jev and each seat sends a decision request
- **THEN** both requests use the one client opened for that match

#### Scenario: The next match opens a new client

- **WHEN** a match has sent a decision request and the next match sends a decision request
- **THEN** the first match's client is closed and the next match's request uses a different client

#### Scenario: A match with no Jev seat opens no client

- **WHEN** a match is played and neither seat is Jev
- **THEN** no decision client is opened

#### Scenario: A supplied client stays with its owner

- **WHEN** a client is supplied for a match and that match sends a decision request
- **THEN** the request uses the supplied client, and the system does not open or close a client for that match
