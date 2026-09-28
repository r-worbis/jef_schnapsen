# schnapsen-table Specification

## Purpose

Give the human seat a local page that shows that seat's cards and the match score, and accepts only legal actions.

## Requirements

### Requirement: Show the human seat its table

The page SHALL show the human seat's own cards face up, the computer seat's card count with faces hidden, the face-up trump while it remains visible, the number of face-down talon cards, whether the talon is closed, the cards in the current trick, which seat is to play, the human seat's own won tricks, the computer seat's first won trick, each seat's eyes in the current deal, each seat's game points still needed, and each seat's Bummerl count.

#### Scenario: Opening view

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the human seat sees its five cards, a face-down count of five for the computer, the trump card, a talon count of nine, seven points still needed for each seat, and zero Bummerl for each seat

#### Scenario: Score during a Bummerl

- **WHEN** the human seat has won a deal worth two game points from a fresh Bummerl
- **THEN** the page shows five points still needed for the human seat and seven for the computer seat

### Requirement: Hide the computer's private cards

The page and the data sent to the browser for the human seat SHALL NOT include the computer seat's current card faces or the order of the face-down talon. The computer seat's won tricks after its first trick SHALL NOT be shown face up during the deal.

#### Scenario: Computer hand stays hidden

- **WHEN** the human seat loads the table during a deal
- **THEN** the response contains no face of a card still held by the computer seat

#### Scenario: Talon order stays hidden

- **WHEN** the human seat loads the table while face-down talon cards remain
- **THEN** the response contains the talon count and does not contain the identity of those face-down cards

### Requirement: Accept only legal human actions

On the human seat's turn, the page SHALL offer every action that is legal for that seat and SHALL offer no action that is illegal. Offered actions SHALL include playing a legal card and, when the rules allow them, exchanging the trump Bube, closing the talon, declaring a marriage, and declaring 66 eyes. Choosing an action SHALL send that action to the game. The page SHALL NOT change the deal when the game refuses the action.

#### Scenario: Only legal cards can be played

- **WHEN** it is the human seat's turn to follow and the talon is exhausted
- **THEN** the page offers only the cards the game considers legal plays

#### Scenario: Declare when eligible

- **WHEN** the human seat has just won a trick and has at least 66 counting eyes
- **THEN** the page offers a declaration that ends the deal

#### Scenario: Refused action

- **WHEN** the human seat submits an action the game refuses
- **THEN** the cards and scores shown are unchanged and the human seat is still to play

### Requirement: Show the computer's completed action

After the computer seat plays, the page SHALL show the card it played, and any marriage, trump exchange, talon close, or declaration it made, without showing any card that remains in its hand.

#### Scenario: Played card becomes visible

- **WHEN** the computer seat plays a card to the trick
- **THEN** the page shows that card in the trick and still hides the computer seat's remaining cards

### Requirement: Show the end of a deal and of the match

When a deal ends, the page SHALL show which seat won, the game points awarded, and both seats' counting eyes. When the match ends, the page SHALL show which seat won the match and each seat's Bummerl count. The page SHALL offer another deal while the match is unfinished, and SHALL NOT offer another deal after the match has ended.

#### Scenario: Deal result

- **WHEN** a deal ends because a seat declared 66 eyes
- **THEN** the page shows the winner, the game points awarded, and both eye totals

#### Scenario: Match result

- **WHEN** a seat is charged its second Bummerl
- **THEN** the page names the other seat as the match winner and does not start another deal

### Requirement: Table copy is German

The human table SHALL present its headings, turn and dealer lines, score-row names, talon and trump notes, banners, action button labels, and face-down card names in German. Action ids, JSON field names, and card tokens SHALL stay unchanged. The document language SHALL be German.

#### Scenario: Opening chrome is German

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the section headings and the dealer and turn line are in German, and the document language is German

#### Scenario: Action buttons are German

- **WHEN** it is the human seat's turn and legal actions include playing a card, exchanging the trump Bube, closing the talon, declaring a marriage, or declaring 66
- **THEN** each offered action's visible label is German and the action id is the same as before

#### Scenario: Result banners are German

- **WHEN** a deal or the match ends, or the table reports a missing API key or a replaced computer choice
- **THEN** the banner text shown to the human seat is German
