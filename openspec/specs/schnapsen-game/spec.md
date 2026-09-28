# schnapsen-game Specification

## Purpose

Deal, play, and score a two-player game of weiches Schnapsen, including eyes, game points, Bummerl, and a match to two Bummerl.

## Requirements

### Requirement: Twenty-card pack

The pack SHALL contain exactly twenty cards: the suits Herz, Karo, Pik, and Kreuz, and in each suit the ranks Ass, Zehner, König, Dame, and Bube. Card eyes SHALL be Ass 11, Zehner 10, König 4, Dame 3, and Bube 2. Within one suit, rank order for taking a trick SHALL be Ass, then Zehner, then König, then Dame, then Bube.

#### Scenario: Pack contents

- **WHEN** a deal begins
- **THEN** the pack contains each of those twenty cards once and no other card

#### Scenario: Eye values

- **WHEN** a trick is scored
- **THEN** each card in it contributes the eye value of its rank

### Requirement: Choose the dealer

The first dealer of a match SHALL be the seat that draws the higher card from a shuffled pack. Equal cards SHALL be redrawn. After every deal, the seats SHALL exchange the roles of dealer and forehand. Forehand is the non-dealer and leads to the first trick.

#### Scenario: Higher card deals

- **WHEN** the two drawn cards have different trick ranks
- **THEN** the seat that drew the higher rank is the dealer for the first deal

#### Scenario: Equal ranks are redrawn

- **WHEN** the two drawn cards have the same rank
- **THEN** both cards are returned and the seats draw again

#### Scenario: Roles swap

- **WHEN** a deal ends and the match has not ended
- **THEN** the previous forehand is the dealer of the next deal

### Requirement: Deal five cards and a trump

The dealer SHALL shuffle the pack and deal three cards to forehand, three to the dealer, one face-up trump card, two more to forehand, and two more to the dealer. The remaining nine cards SHALL form a face-down talon placed so the trump card stays visible. The trump suit SHALL be the suit of that face-up card. Each seat SHALL hold five cards.

#### Scenario: Opening layout

- **WHEN** a deal has just been dealt
- **THEN** each seat has five cards, one trump card is face up, and nine cards remain face down in the talon

### Requirement: Play while the talon is open

While the talon is still open and cards remain to draw, the follower SHALL be allowed to play any card. The follower wins the trick by playing a higher card of the led suit, or by playing a trump when the led card is not a trump. Otherwise the leader wins. The winner of a trick leads to the next trick.

#### Scenario: Follower may discard

- **WHEN** the talon is open and the follower plays an off-suit card that is not a trump
- **THEN** the leader wins the trick

#### Scenario: Trump captures a plain lead

- **WHEN** the talon is open, the lead is not a trump, and the follower plays a trump
- **THEN** the follower wins the trick

### Requirement: Draw after an open trick

After a trick while the talon is open and the winner does not already have at least 66 counting eyes, the winner SHALL draw the top talon card and the opponent SHALL draw the next card. The face-up trump SHALL be the last card drawn. No seat SHALL draw after the talon is closed or after it has been exhausted.

#### Scenario: Winner draws first

- **WHEN** a trick is won, the winner has fewer than 66 counting eyes, and at least two cards remain in the talon
- **THEN** the winner receives the first of those cards and the opponent receives the second

#### Scenario: No draw from a closed talon

- **WHEN** a trick is won after the talon was closed
- **THEN** neither seat draws a card

### Requirement: Follow suit after the talon is exhausted or closed

Once the talon is exhausted or has been closed, the follower SHALL play a higher card of the led suit when they have one. Otherwise they SHALL play a lower card of the led suit when they have one. Otherwise they SHALL play a trump when they have one. Otherwise they SHALL play any remaining card. A trump SHALL NOT be played when the follower can follow the led suit.

#### Scenario: Must beat the led suit

- **WHEN** the talon is exhausted and the follower holds a higher card of the led suit
- **THEN** the only legal plays are those higher cards of the led suit

#### Scenario: Suit before trump

- **WHEN** the talon is closed and the follower holds a card of the led suit and a trump, but no higher card of the led suit
- **THEN** the legal plays are the cards of the led suit and do not include the trump

### Requirement: Marriages

A seat that holds König and Dame of the same suit, and is about to lead, SHALL be allowed to declare that marriage before leading. A trump marriage SHALL be worth 40 eyes and any other marriage 20 eyes. The seat SHALL then lead either the König or the Dame of that suit unless the deal ends first. A marriage SHALL score no eyes for a seat that has won no trick in that deal. Forehand SHALL be allowed to declare a marriage before the first lead.

#### Scenario: Trump marriage

- **WHEN** a seat that is about to lead declares König and Dame of the trump suit and has already won a trick in the deal
- **THEN** that seat gains 40 eyes and the next lead is one of those two cards

#### Scenario: Marriage without a trick

- **WHEN** a seat declares a marriage and wins no trick in the deal
- **THEN** those marriage eyes are not included in that seat's total

### Requirement: Exchange the trump jack

A seat that holds the trump Bube SHALL be allowed, on its turn and before it plays a card, to exchange that Bube for the face-up trump, including forehand before the first lead. The exchange SHALL remain available when only one face-down card lies on the trump. The exchange SHALL NOT be available after the trump has been drawn, after the talon is closed, or when the seat does not hold the trump Bube.

#### Scenario: Exchange before playing

- **WHEN** it is a seat's turn, that seat holds the trump Bube, and the trump card is still face up
- **THEN** the seat may take the face-up trump and put the trump Bube in its place before playing a card

#### Scenario: Last face-down card still allows the exchange

- **WHEN** one face-down card lies on the face-up trump and the seat to play holds the trump Bube
- **THEN** the exchange is legal

### Requirement: Close the talon

A seat that is about to lead SHALL be allowed to close the talon when at least two face-down cards remain on the trump. Closing SHALL turn the trump face down across the remaining talon, end all further draws, and apply the exhausted-talon play rules from the next card. Closing SHALL NOT be legal when only one face-down card remains on the trump, when the seat is following, or after the talon is exhausted. The opponent's eyes for scoring a deal won by the closer SHALL be the opponent's eyes at the moment of closing. Eyes the opponent gains after closing SHALL NOT change that award.

#### Scenario: Close with cards remaining

- **WHEN** a seat is about to lead and at least two face-down cards lie on the trump
- **THEN** the seat may close the talon, and neither seat draws for the rest of the deal

#### Scenario: Cannot close on the last face-down card

- **WHEN** only one face-down card lies on the trump
- **THEN** closing is not legal

#### Scenario: Award uses eyes at closing

- **WHEN** the closer later reaches at least 66 counting eyes and the opponent had 33 or more eyes when the talon was closed
- **THEN** the closer wins one game point even if the opponent's later tricks would have changed that total

### Requirement: Declare sixty-six

After a seat wins a trick or declares a marriage that counts, if that seat's counting eyes are at least 66, the game SHALL end the deal at once. No seat SHALL choose to continue the deal or to declare 66. Game points SHALL be awarded as for a correct declaration: three if the opponent has won no trick, two if the opponent has 32 or fewer eyes, and one if the opponent has 33 or more. After a closed talon, if the opponent of the closer reaches 66 first, that opponent SHALL win three game points if they had won no trick at the moment of closing, and two otherwise. A false declaration SHALL NOT be offered.

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

- **WHEN** the computer seat's answering card would give the trick winner at least 66 counting eyes
- **THEN** the deal stays in play until the human seat confirms they have seen the answer, and after that confirmation the deal ends under this requirement

#### Scenario: Closer fails

- **WHEN** the talon was closed and the closer never reaches 66 eyes
- **THEN** the opponent wins the deal, scoring three game points if the opponent was trickless at closing and two otherwise

### Requirement: Last trick

If the talon was not closed and neither seat has reached 66 counting eyes before the last card is led, the last card SHALL be played. The winner of that last trick SHALL win the deal and SHALL score game points by the same thresholds as a deal ended at 66, using each seat's counting eyes. This last-trick win SHALL NOT apply when the talon was closed.

#### Scenario: Last trick awards the deal

- **WHEN** the talon is exhausted, neither seat has reached 66, and a seat wins the trick of the last two cards
- **THEN** that seat wins the deal

#### Scenario: Closed talon ignores the last trick

- **WHEN** the talon was closed and neither seat reaches 66
- **THEN** the winner is the opponent of the closer, not whoever took the last trick

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

### Requirement: Reject illegal actions

The engine SHALL refuse an action that the rules forbid. A refused action SHALL leave the cards, eyes, and scores unchanged.

#### Scenario: Illegal card

- **WHEN** a seat plays a card that is not a legal play for the current trick
- **THEN** the trick is unchanged and the same seat is still to play

### Requirement: Bummerl and match

Both seats SHALL start a Bummerl with seven game points still needed. Game points won SHALL be subtracted from that total. The Bummerl SHALL end when a seat's remaining total reaches zero. If the other seat still has seven at that moment, the loser SHALL be charged two Bummerl (Schneider). Otherwise the loser SHALL be charged one Bummerl. A match SHALL end when one seat has been charged two Bummerl. Points won beyond those needed to reach zero SHALL NOT carry into the next Bummerl.

#### Scenario: Count down from seven

- **WHEN** a seat that still needs four game points wins two
- **THEN** that seat still needs two game points

#### Scenario: Schneider

- **WHEN** a seat reaches zero game points remaining while the other seat still needs seven
- **THEN** the other seat is charged two Bummerl

#### Scenario: Match to two Bummerl

- **WHEN** a seat is charged its second Bummerl
- **THEN** the match ends and the other seat wins
