# Spec Delta

## ADDED Requirements

### Requirement: The engine alone accepts a play

Every card that enters a trick SHALL be accepted by the engine's legality check before it is applied. The person, Jev, and the stub SHALL all be subject to that same check, including when both seats are played by an AI. A player SHALL NOT place a card that the check refuses. Once the talon is exhausted or has been closed, a follow SHALL be accepted only when it obeys Farbzwang and then Stichzwang. Farbzwang means the follower plays a card of the led suit when they have one. Stichzwang means the follower takes the trick when they can: a higher card of the led suit when they have one, otherwise a lower card of that suit when they have one, otherwise a trump when they have one, otherwise any remaining card. A trump SHALL NOT be accepted when the follower can follow the led suit. The plays offered for a seat SHALL be exactly the plays this check accepts. A refused play SHALL leave the cards, eyes, and scores unchanged, and the same seat SHALL still be to play. The talon is exhausted only when no face-down talon card remains and the face-up trump has been drawn.

#### Scenario: A trump is refused while the led suit is held

- **WHEN** the talon is exhausted, the follower holds a card of the led suit and a trump, and the proposed card is the trump
- **THEN** the trump is not played, the current trick is unchanged, and the same seat is still to play

#### Scenario: A higher card of the led suit is accepted

- **WHEN** the talon is exhausted, the follower holds a higher card of the led suit, and that card is proposed
- **THEN** that card is played onto the trick

#### Scenario: The right seat is refused the same way

- **WHEN** the talon is exhausted, the right seat is to follow, that seat holds the led suit, and the proposed card is a different suit
- **THEN** the proposal is refused and the right seat is still to play

#### Scenario: An AI follower is refused the same way

- **WHEN** both seats are played by an AI, the talon is exhausted, the follower holds the led suit, and the proposed card is a different suit
- **THEN** the proposal is refused, the cards and scores are unchanged, and that AI seat is still to play

## MODIFIED Requirements

### Requirement: Declare sixty-six

After a seat wins a trick or declares a marriage that counts, if that seat's counting eyes are at least 66, the game SHALL end the deal at once. No seat SHALL choose to continue the deal or to declare 66. Game points SHALL be awarded as for a correct declaration: three if the opponent has won no trick, two if the opponent has 32 or fewer eyes, and one if the opponent has 33 or more. After a closed talon, if the opponent of the closer reaches 66 first, that opponent SHALL win three game points if they had won no trick at the moment of closing, and two otherwise. A false declaration SHALL NOT be offered. When the person is playing the right seat and has led, an answering card that would reach 66 SHALL wait for that person to confirm before the deal ends. When the right seat's player is not the person, that answering card SHALL end the deal without a confirmation.

#### Scenario: Opponent has no trick

- **WHEN** a seat's counting eyes reach at least 66 and the opponent has won no trick
- **THEN** that seat wins three game points and the deal ends without a further action

#### Scenario: Opponent has thirty-three

- **WHEN** a seat's counting eyes reach at least 66 and the opponent has 33 or more eyes
- **THEN** that seat wins one game point and the deal ends without a further action

#### Scenario: Marriage that reaches sixty-six

- **WHEN** a seat that has already won a trick declares a marriage that brings its counting eyes to at least 66
- **THEN** the deal ends at once and that seat does not lead a marriage card

#### Scenario: Computer answer reaches sixty-six only after it is seen

- **WHEN** the person is playing the right seat and has led, and the left seat's answering card would give the trick winner at least 66 counting eyes
- **THEN** the deal stays in play until the person confirms they have seen the answer, and after that confirmation the deal ends under this requirement

#### Scenario: An AI answer that reaches sixty-six does not wait

- **WHEN** the right seat's player is not the person and an answering card would give the trick winner at least 66 counting eyes
- **THEN** the deal ends under this requirement without a confirmation

#### Scenario: Closer fails

- **WHEN** the talon was closed and the closer never reaches 66 eyes
- **THEN** the opponent wins the deal, scoring three game points if the opponent was trickless at closing and two otherwise

### Requirement: Hold a computer answer until the human has seen it

When the person is playing the right seat, that seat leads a card, and the left seat plays a card in answer, the game SHALL leave both cards in the current trick. Until the person confirms they have seen that answer, the game SHALL NOT award the trick, change either seat's eyes, draw any card, change who leads next, or end the deal because of that trick. Confirmation SHALL be legal only for the person, and only while such an answer is waiting. After confirmation, the game SHALL award the trick under the existing taking, drawing, declaration, and last-trick rules. When the person follows a lead by the left seat, the game SHALL award the trick as soon as the person's card is played, with no confirmation. When the right seat's player is Jev or the stub, the game SHALL award the trick as soon as the answering card is played, with no confirmation, whichever seat answered.

#### Scenario: Computer answer stays uncollected

- **WHEN** the person is playing the right seat, that seat leads a card, and the left seat plays an answering card
- **THEN** both cards remain in the current trick, neither seat's eyes change, no card is drawn, the leader is unchanged, and the deal is not over

#### Scenario: Confirmation collects and counts the trick

- **WHEN** an answering card from the left seat is waiting and the person confirms they have seen it, and that card does not win the trick, and the talon is still open with cards left to draw
- **THEN** the trick is awarded to the right seat, the right seat's eyes include both cards, the right seat draws first, and the right seat leads next

#### Scenario: A winning answer is counted only after confirmation

- **WHEN** an answering card from the left seat is waiting for the person, that card wins the trick, and the winner would have at least 66 counting eyes after the award
- **THEN** the eyes stay below that award and the deal stays in play until the person confirms

#### Scenario: The last trick waits for confirmation

- **WHEN** the left seat's answering card is the last card of a deal whose talon was not closed, the person led that trick, and the person has not confirmed
- **THEN** the deal is not over

#### Scenario: Confirmation of the last trick ends the deal

- **WHEN** the person confirms they have seen the left seat's answering card on that last trick
- **THEN** the winner of the trick wins the deal under the last-trick scoring rules

#### Scenario: A human follow is still collected at once

- **WHEN** the left seat leads a card and the person plays a following card
- **THEN** the trick is awarded immediately and no confirmation is required

#### Scenario: Two AIs do not wait

- **WHEN** both seats are bound to the stub, one seat has led, and the other seat plays an answering card
- **THEN** the trick is awarded immediately and confirmation is not legal

#### Scenario: Confirmation is refused when nothing is waiting

- **WHEN** no answer is waiting and a confirmation is submitted
- **THEN** the confirmation is refused and the cards, eyes, and scores are unchanged
