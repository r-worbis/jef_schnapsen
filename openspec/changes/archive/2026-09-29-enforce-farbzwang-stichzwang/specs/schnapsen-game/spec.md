# Spec Delta

## MODIFIED Requirements

### Requirement: Follow suit after the talon is exhausted or closed

Once the talon is exhausted or has been closed, the engine SHALL accept a follow only when it obeys Farbzwang and then Stichzwang, for the human seat and for the computer seat. Farbzwang means the follower plays a card of the led suit when they have one. Stichzwang means the follower takes the trick when they can. The follower SHALL play a higher card of the led suit when they have one, and every such higher card SHALL be legal. Otherwise they SHALL play a lower card of the led suit when they have one. Otherwise they SHALL play a trump when they have one. Otherwise they SHALL play any remaining card. A trump SHALL NOT be played when the follower can follow the led suit. When the lead is itself a trump, the trump suit is the led suit, so a non-trump SHALL be legal only when the follower holds no trump. The engine SHALL refuse a card that breaks this order. A refused card SHALL leave the cards, eyes, and scores unchanged, and the same seat SHALL still be to play. The actions offered to the human seat and the actions offered to the computer seat SHALL be exactly the follows this check accepts. The talon is exhausted only when no face-down talon card remains and the face-up trump has been drawn. While a card remains to draw, including while the face-up trump is still to be drawn, these obligations SHALL NOT apply.

#### Scenario: Must beat the led suit

- **WHEN** the talon is exhausted and the follower holds a higher card of the led suit
- **THEN** the only legal plays are those higher cards of the led suit

#### Scenario: Suit before trump

- **WHEN** the talon is closed and the follower holds a card of the led suit and a trump, but no higher card of the led suit
- **THEN** the legal plays are the cards of the led suit and do not include the trump

#### Scenario: Must trump when void

- **WHEN** the talon is exhausted, the lead is not a trump, and the follower holds no card of the led suit and at least one trump
- **THEN** the only legal plays are those trumps

#### Scenario: Any card when void and without a trump

- **WHEN** the talon is exhausted and the follower holds neither a card of the led suit nor a trump
- **THEN** every card in the follower's hand is a legal play

#### Scenario: Must beat a trump lead

- **WHEN** the talon is exhausted, the lead is a trump, and the follower holds a higher trump and a lower trump
- **THEN** the only legal plays are the higher trumps

#### Scenario: Must follow a trump that cannot be beaten

- **WHEN** the talon is closed, the lead is a trump, and the follower holds a lower trump and a card of another suit
- **THEN** the only legal plays are those lower trumps

#### Scenario: Either seat is refused

- **WHEN** the talon is exhausted or closed and the seat to follow, whether human or computer, plays a card this requirement forbids
- **THEN** the play is refused, the trick and the hands are unchanged, and that same seat is still to play

#### Scenario: Open stock does not oblige a follow

- **WHEN** the talon is open and the face-up trump has not yet been drawn, and the follower holds the led suit
- **THEN** a card of another suit is a legal play
