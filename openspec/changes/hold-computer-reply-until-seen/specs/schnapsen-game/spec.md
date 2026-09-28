# Spec Delta

## ADDED Requirements

### Requirement: Hold a computer answer until the human has seen it

When the human seat leads a card and the computer seat plays a card in answer, the game SHALL leave both cards in the current trick. Until the human seat confirms they have seen that answer, the game SHALL NOT award the trick, change either seat's eyes, draw any card, change who leads next, or end the deal because of that trick. Confirmation SHALL be legal only for the human seat, and only while such an answer is waiting. After confirmation, the game SHALL award the trick under the existing taking, drawing, declaration, and last-trick rules. When the human seat follows a lead by the computer seat, the game SHALL award the trick as soon as the human seat's card is played, with no confirmation.

#### Scenario: Computer answer stays uncollected

- **WHEN** the human seat leads a card and the computer seat plays an answering card
- **THEN** both cards remain in the current trick, neither seat's eyes change, no card is drawn, the leader is unchanged, and the deal is not over

#### Scenario: Confirmation collects and counts the trick

- **WHEN** an answering card from the computer seat is waiting and the human seat confirms they have seen it, and that card does not win the trick, and the talon is still open with cards left to draw
- **THEN** the trick is awarded to the human seat, the human seat's eyes include both cards, the human seat draws first, and the human seat leads next

#### Scenario: A winning answer is counted only after confirmation

- **WHEN** an answering card from the computer seat is waiting, that card wins the trick, and the winner would have at least 66 counting eyes after the award
- **THEN** the eyes stay below that award and the deal stays in play until the human seat confirms

#### Scenario: The last trick waits for confirmation

- **WHEN** the computer seat's answering card is the last card of a deal whose talon was not closed, and the human seat has not confirmed
- **THEN** the deal is not over

#### Scenario: Confirmation of the last trick ends the deal

- **WHEN** the human seat confirms they have seen the computer seat's answering card on that last trick
- **THEN** the winner of the trick wins the deal under the last-trick scoring rules

#### Scenario: A human follow is still collected at once

- **WHEN** the computer seat leads a card and the human seat plays a following card
- **THEN** the trick is awarded immediately and no confirmation is required

#### Scenario: Confirmation is refused when nothing is waiting

- **WHEN** no computer answer is waiting and a confirmation is submitted
- **THEN** the confirmation is refused and the cards, eyes, and scores are unchanged
