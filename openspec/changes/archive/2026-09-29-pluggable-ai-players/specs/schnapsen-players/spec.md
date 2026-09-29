# Spec Delta

## Purpose

Bind each seat of a Schnapsen match to a player, let two AI players play a deal against each other, and let a stub stand in for an LLM by proposing a random card that the engine may still refuse.

## ADDED Requirements

### Requirement: Bind a player to each seat

The match SHALL bind the right seat and the left seat to one player kind each. The kinds SHALL be the person at the page, Jev, and the stub. The right seat SHALL be the seat whose id is `human`. The left seat SHALL be the seat whose id is `computer`. Those ids name the places at the table. The default binding SHALL be the person on the right and Jev on the left. The right seat MAY be the person, Jev, or the stub. The left seat MAY be Jev or the stub and SHALL NOT be the person. A request that binds the person to the left seat SHALL be refused and SHALL leave the current match unchanged. Choosing an allowed pair SHALL start a new match from a new deal and SHALL discard the deal that was in progress.

#### Scenario: Default seats

- **WHEN** a match is started and no player pair was chosen
- **THEN** the person plays the right seat and Jev plays the left seat

#### Scenario: Two stubs replace the deal

- **WHEN** a deal is in progress and the chosen pair is the stub on the right and the stub on the left
- **THEN** a new match starts, the previous deal is gone, and each seat is bound to the stub

#### Scenario: The person cannot sit on the left

- **WHEN** a request binds the person to the left seat
- **THEN** the request is refused and the current match, including its deal and scores, stays as it was

### Requirement: The stub proposes a random card

When it is the turn of a seat bound to the stub, the stub SHALL propose exactly one card chosen uniformly from the cards that seat currently holds, as a plain play of that card. A supplied selector SHALL determine which of those cards is proposed, so the choice can be repeated. The stub SHALL NOT propose a marriage, a trump exchange, or closing the talon. The stub SHALL NOT apply the play. The stub SHALL NOT read `jef.api` and SHALL NOT send a decision request.

#### Scenario: The selected card is the proposal

- **WHEN** the stub's seat holds more than one card, the supplied selector picks one of them, and that plain play is legal
- **THEN** that card is played, the other cards of that seat stay in the hand, and the play is not a marriage, a trump exchange, or a close

#### Scenario: The stub does not ask Jev

- **WHEN** it is the stub's turn, including when `jef.api` is missing
- **THEN** no decision request is sent and the missing-key notice is not shown for that turn

### Requirement: Two AI players alternate

When both seats are bound to Jev or the stub, the match SHALL ask the player bound to the seat that is to play, apply the result under the engine's rules, and then ask the player bound to the seat that is to play next. The person SHALL NOT have to submit an action for those turns. A legal answering card SHALL be awarded under the existing taking, drawing, and declaration rules without waiting for a confirmation.

#### Scenario: A stub lead and a stub answer finish the trick

- **WHEN** both seats are bound to the stub, the left seat leads a legal card, and the right seat answers with a legal card
- **THEN** the trick is awarded, confirmation is not legal, and neither card is still waiting in the current trick

#### Scenario: The person sends nothing

- **WHEN** both seats are bound to an AI and it is an AI seat's turn to play a card
- **THEN** that turn is taken without an action submitted by the person

### Requirement: Replace a second illegal proposal

If the stub's proposed card is not a legal play, the system SHALL NOT apply it. The system SHALL ask the stub once more for a card from the same hand. If that second card is also not a legal play, the system SHALL apply one predetermined legal action and the table SHALL show that the choice was replaced. If the first proposed card is legal, the system SHALL apply that card and SHALL NOT mark the choice as replaced.

#### Scenario: The first card is illegal

- **WHEN** the talon is exhausted, the stub holds a card of the led suit and another card, and the supplied selector proposes the other card first
- **THEN** the trick is unchanged, the same seat is still to play, and the stub is asked again

#### Scenario: The second card is illegal

- **WHEN** the stub's first and second proposals are both cards the engine refuses
- **THEN** one predetermined legal action is applied and the table shows that the choice was replaced

#### Scenario: The first card is legal

- **WHEN** the stub's first proposal is a legal plain play
- **THEN** that card is played and the choice is not marked as replaced
