# Spec Delta

## ADDED Requirements

### Requirement: Choose who plays each seat

The page SHALL offer a choice for the right seat and a choice for the left seat on the same row as the title, the pack choice, and the turn line. The right seat's choice SHALL be Mensch, Jev, or Zufall. The left seat's choice SHALL be Jev or Zufall, and SHALL NOT include Mensch. The labels SHALL be those German words. The default SHALL show Mensch for the right seat and Jev for the left seat. Choosing an allowed pair SHALL start a new match with that binding. The page SHALL keep offering the deal and match controls of the match that is already on the table until that new match replaces it.

#### Scenario: Default labels

- **WHEN** the page is opened and no pair has been chosen in this visit
- **THEN** the right seat's choice shows Mensch and the left seat's choice shows Jev

#### Scenario: Zufall against Jev starts a new match

- **WHEN** a deal is in progress and the person chooses Zufall for the right seat and Jev for the left seat
- **THEN** the page shows a new deal played by the stub on the right and Jev on the left

#### Scenario: Mensch is not offered on the left

- **WHEN** the page shows the choice for the left seat
- **THEN** the only offered kinds are Jev and Zufall

### Requirement: Advance an AI seat

When the seat to play is Jev or the stub, the deal is not over, and no answer is waiting for the person to confirm, the page SHALL request that one turn. The page SHALL NOT request a further turn while a confirmation is waiting. The page SHALL NOT request a Jev turn while the table shows that the key is missing. The page SHALL still request a stub turn while the key is missing. After a turn, if another AI seat is to play under these same conditions, the page SHALL request that next turn. Each request SHALL take one AI turn.

#### Scenario: The opening lead is requested

- **WHEN** a deal has just been dealt, the left seat is to lead, and that seat's player is Jev or the stub
- **THEN** the page requests that seat's turn without a click on a card

#### Scenario: The answer is a second request

- **WHEN** an AI has led and the other seat is an AI that is now to follow
- **THEN** the page requests that following turn, and that request plays one card

#### Scenario: No request while Gesehen is waiting

- **WHEN** the person has led and the answering card is waiting for confirmation
- **THEN** the page does not request another AI turn

#### Scenario: A missing key stops only Jev

- **WHEN** the table shows that the key is missing and the seat to play is Jev
- **THEN** the page does not request that turn

#### Scenario: A missing key does not stop Zufall

- **WHEN** `jef.api` is missing and the seat to play is the stub
- **THEN** the page requests that stub turn

## MODIFIED Requirements

### Requirement: Show the human seat its table

The page SHALL show the face-up trump while it remains visible, the number of face-down talon cards, whether the talon is closed, the cards in the current trick, which seat is to play, each seat's eyes in the current deal, each seat's game points still needed, and each seat's Bummerl count. When the person is playing the right seat, the page SHALL show that seat's own cards face up, the left seat's card count with faces hidden, the right seat's own won tricks, and the left seat's first won trick. When the right seat's player is Jev or the stub, the page SHALL show a face-down count for both seats and SHALL NOT show either seat's current card faces. While the person is playing the right seat, the score names, the turn line, the dealer line, and the seat headings SHALL keep calling that seat Du and the left seat the computer. When the right seat's player is not the person, those same texts SHALL name each seat by its kind, using Mensch, Jev, or Zufall.

#### Scenario: Opening view

- **WHEN** a deal has just been dealt and the person is playing the right seat
- **THEN** the right seat's five cards are face up, the left seat has a face-down count of five, the trump card is shown, the talon count is nine, seven points are still needed for each seat, and each seat has zero Bummerl

#### Scenario: Score during a Bummerl

- **WHEN** the right seat has won a deal worth two game points from a fresh Bummerl and the person is playing that seat
- **THEN** the page shows five points still needed for the right seat and seven for the left seat

#### Scenario: Both AI hands stay face down

- **WHEN** a deal has just been dealt and the right seat's player is the stub or Jev
- **THEN** both seats are shown as a face-down count of five and neither seat's card faces are shown

#### Scenario: AI seats are named by their kind

- **WHEN** the right seat is the stub, the left seat is Jev, and it is the right seat's turn
- **THEN** the turn line names Zufall and does not call that seat Du

### Requirement: Hide the computer's private cards

The page and the data sent to the browser SHALL NOT include the current card faces of a seat whose player is not the person, or the order of the face-down talon, except inside the cards box of the Jev reveal. That cards box SHALL contain the cards-and-options text of the last decision request, including any card of the seat that was asked that was named in that request. No other field SHALL contain a face of a card still held by a seat whose player is not the person. Won tricks of a hidden seat after its first trick SHALL NOT be shown face up during the deal except as part of that same cards-box text. The cards box SHALL NOT contain the identity of a face-down talon card. When the person is playing the right seat, that seat's own cards SHALL still be shown face up.

#### Scenario: Computer hand stays hidden

- **WHEN** the person loads the table during a deal
- **THEN** the response contains no face of a card still held by the left seat outside the reveal cards text

#### Scenario: Talon order stays hidden

- **WHEN** the table is loaded while face-down talon cards remain
- **THEN** the response contains the talon count and does not contain the identity of those face-down cards

#### Scenario: Requested hand is only in the cards box

- **WHEN** a decision request named a card that a Jev seat still holds
- **THEN** that card appears in the reveal cards text and in no other field of the response

#### Scenario: The right seat's AI hand stays hidden

- **WHEN** the right seat's player is the stub or Jev and the table is loaded during a deal
- **THEN** the response contains no face of a card still held by the right seat outside the reveal cards text

### Requirement: Accept only legal human actions

On the person's turn, the page SHALL offer every action that is legal for the right seat and SHALL offer no action that is illegal. A plain card play SHALL be offered only by clicking that card in the hand, and SHALL NOT also be offered as a text button. Every other legal action SHALL still be offered as a text button, including exchanging the trump jack, closing the talon, declaring a marriage, confirming a seen reply, and starting the next deal, including when exchange or closing is combined with a play or a marriage. Choosing an offered action SHALL send that action to the game. The page SHALL NOT change the deal when the game refuses the action. The page SHALL NOT offer a 66 declaration or a continue action. When the seat to play is Jev or the stub, the page SHALL offer no card to click and no play, marriage, trump exchange, or talon close.

#### Scenario: Only legal cards can be played

- **WHEN** it is the person's turn to follow and the talon is exhausted
- **THEN** the page offers only the cards the game considers legal plays, by a click on those cards, and offers no text button for playing a card

#### Scenario: Plain play has no text button

- **WHEN** it is the person's turn and a card in the hand is a legal plain play
- **THEN** clicking that card sends that play, and the actions row has no button for that same play

#### Scenario: Marriage stays a button

- **WHEN** it is the person's turn to lead and both a plain play of a marriage card and declaring that marriage are legal
- **THEN** clicking the card sends the plain play, and a text button remains for declaring the marriage

#### Scenario: No declaration when sixty-six is reached

- **WHEN** the person has just won a trick and the right seat has at least 66 counting eyes
- **THEN** the deal is already ended and the page does not offer a declaration that ends the deal

#### Scenario: Refused action

- **WHEN** the person submits an action the game refuses
- **THEN** the cards and scores shown are unchanged and the right seat is still to play

#### Scenario: An AI turn offers no card

- **WHEN** the seat to play is the stub or Jev
- **THEN** the page offers no card click and no button for a play, a marriage, a trump exchange, or closing the talon

### Requirement: Confirm a computer answer before the trick is taken

When the person is playing the right seat, that seat has led, the left seat has played a card in answer, and that trick has not yet been awarded, the page SHALL show both cards face up. It SHALL offer one confirmation button whose label is German, and SHALL offer no card play, marriage, trump exchange, talon close, or declaration. Choosing that button SHALL send the confirmation to the game. Until the game awards the trick, the eyes and won tricks on the page SHALL be those from before the answer. The page SHALL NOT ask an AI seat to move while the answer is waiting. Loading the page again during the wait SHALL show the same two cards and the same confirmation button. When the right seat's player is not the person, the page SHALL NOT offer that confirmation, because the trick is already awarded.

#### Scenario: Both cards stay on the table

- **WHEN** the person has led, the left seat has answered, and the person has not confirmed
- **THEN** the page shows both cards of the trick face up, and the eyes and won tricks do not include that trick

#### Scenario: Confirmation is the only offered action

- **WHEN** that answering card is waiting
- **THEN** the only action the page offers is a German confirmation button

#### Scenario: Choosing confirmation collects the trick

- **WHEN** the person chooses the confirmation button
- **THEN** the page sends that confirmation and then shows the trick awarded, including the updated eyes

#### Scenario: The computer is not asked to move during the wait

- **WHEN** that answering card is waiting
- **THEN** the page does not request another move from an AI seat

#### Scenario: Reloading keeps the answer visible

- **WHEN** the page is loaded again while the answering card is still waiting
- **THEN** both cards are face up and the confirmation button is offered again

#### Scenario: Two AIs show no confirmation

- **WHEN** the right seat's player is the stub or Jev and an answering card has just been played
- **THEN** the page offers no confirmation button and the trick is no longer waiting to be awarded
