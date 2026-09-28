# Spec Delta

## MODIFIED Requirements

### Requirement: Accept only legal human actions

On the human seat's turn, the page SHALL offer every action that is legal for that seat and SHALL offer no action that is illegal. Offered actions SHALL include playing a legal card and, when the rules allow them, exchanging the trump Bube, closing the talon, and declaring a marriage. Choosing an action SHALL send that action to the game. The page SHALL NOT change the deal when the game refuses the action. The page SHALL NOT offer a 66 declaration or a continue action.

#### Scenario: Only legal cards can be played

- **WHEN** it is the human seat's turn to follow and the talon is exhausted
- **THEN** the page offers only the cards the game considers legal plays

#### Scenario: No declaration when sixty-six is reached

- **WHEN** the human seat has just won a trick and has at least 66 counting eyes
- **THEN** the deal is already ended and the page does not offer a declaration that ends the deal

#### Scenario: Refused action

- **WHEN** the human seat submits an action the game refuses
- **THEN** the cards and scores shown are unchanged and the human seat is still to play

### Requirement: Show the end of a deal and of the match

When a deal ends, the page SHALL show which seat won, the game points awarded, and both seats' counting eyes. When the match ends, the page SHALL show which seat won the match and each seat's Bummerl count. The page SHALL offer another deal while the match is unfinished, and SHALL NOT offer another deal after the match has ended.

#### Scenario: Deal result

- **WHEN** a deal ends because a seat reached 66 counting eyes
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

- **WHEN** it is the human seat's turn and legal actions include playing a card, exchanging the trump Bube, closing the talon, or declaring a marriage
- **THEN** each offered action's visible label is German and the action id is the same as before

#### Scenario: Result banners are German

- **WHEN** a deal or the match ends, or the table reports a missing API key or a replaced computer choice
- **THEN** the banner text shown to the human seat is German
