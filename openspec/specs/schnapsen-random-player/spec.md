# schnapsen-random-player Specification

## Purpose

Keep a random card player in the game under its own name, separate from Jev and from the LLM.

## Requirements

### Requirement: The random player replaces the stub

The player kind that proposes a random card SHALL be identified as `random`. The kind id `stub` SHALL NOT be a player kind. A request that names `stub` SHALL be refused and SHALL leave the current match unchanged. The random player SHALL remain available on the right seat and on the left seat, including opposite Jev, opposite the LLM, and opposite itself.

#### Scenario: A random seat is accepted

- **WHEN** a match is started with the random player on one seat and Jev on the other
- **THEN** the match starts and that seat is bound to `random`

#### Scenario: The old stub id is refused

- **WHEN** a request binds a seat to `stub`
- **THEN** the request is refused and the current match, including its deal and scores, stays as it was

### Requirement: The random player proposes one card from its hand

When it is the turn of a seat bound to the random player, that player SHALL propose exactly one card chosen uniformly from the cards that seat currently holds, as a plain play of that card. A supplied selector SHALL determine which of those cards is proposed, so the choice can be repeated. The random player SHALL NOT propose a marriage, a trump exchange, or closing the talon. It SHALL NOT apply the play. It SHALL NOT call ChatGPT, SHALL NOT read `chat.api`, and SHALL NOT read `jef.api`.

#### Scenario: The selected card is the proposal

- **WHEN** the random player's seat holds more than one card, the supplied selector picks one of them, and that plain play is legal
- **THEN** that card is played, the other cards of that seat stay in the hand, and the play is not a marriage, a trump exchange, or a close

#### Scenario: A missing key does not stop the random player

- **WHEN** it is the random player's turn and `jef.api` or `chat.api` is missing
- **THEN** the random player still proposes a card, no ChatGPT request is sent, and the missing-key notice is not shown for that turn

### Requirement: Replace a second illegal random proposal

If the random player's proposed card is not a legal play, the system SHALL NOT apply it. The system SHALL ask the random player once more for a card from the same hand. If that second card is also not a legal play, the system SHALL apply one predetermined legal action and the table SHALL show that the choice was replaced. If the first proposed card is legal, the system SHALL apply that card and SHALL NOT mark the choice as replaced. Once the talon is exhausted or closed, a card that breaks Farbzwang or Stichzwang SHALL be one of these refused proposals.

#### Scenario: The first card is illegal

- **WHEN** the talon is exhausted, the random player holds a card of the led suit and another card, and the supplied selector proposes the other card first
- **THEN** the trick is unchanged, the same seat is still to play, and the random player is asked again

#### Scenario: The second card is illegal

- **WHEN** the random player's first and second proposals are both cards the engine refuses
- **THEN** one predetermined legal action is applied and the table shows that the choice was replaced

#### Scenario: The first card is legal

- **WHEN** the random player's first proposal is a legal plain play
- **THEN** that card is played and the choice is not marked as replaced
