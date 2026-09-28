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

The page and the data sent to the browser for the human seat SHALL NOT include the computer seat's current card faces or the order of the face-down talon, except inside the cards box of the Jev reveal. That cards box SHALL contain the cards-and-options text of the last decision request, including any computer-seat card that was named in that request. No other field SHALL contain a face of a card still held by the computer seat. The computer seat's won tricks after its first trick SHALL NOT be shown face up during the deal except as part of that same cards-box text. The cards box SHALL NOT contain the identity of a face-down talon card.

#### Scenario: Computer hand stays hidden

- **WHEN** the human seat loads the table during a deal
- **THEN** the response contains no face of a card still held by the computer seat outside the reveal cards text

#### Scenario: Talon order stays hidden

- **WHEN** the human seat loads the table while face-down talon cards remain
- **THEN** the response contains the talon count and does not contain the identity of those face-down cards

#### Scenario: Requested hand is only in the cards box

- **WHEN** a decision request named a card that the computer seat still holds
- **THEN** that card appears in the reveal cards text and in no other field of the response

### Requirement: Accept only legal human actions

On the human seat's turn, the page SHALL offer every action that is legal for that seat and SHALL offer no action that is illegal. A plain card play SHALL be offered only by clicking that card in the hand, and SHALL NOT also be offered as a text button. Every other legal action SHALL still be offered as a text button, including exchanging the trump jack, closing the talon, declaring a marriage, confirming a seen reply, and starting the next deal, including when exchange or closing is combined with a play or a marriage. Choosing an offered action SHALL send that action to the game. The page SHALL NOT change the deal when the game refuses the action. The page SHALL NOT offer a 66 declaration or a continue action.

#### Scenario: Only legal cards can be played

- **WHEN** it is the human seat's turn to follow and the talon is exhausted
- **THEN** the page offers only the cards the game considers legal plays, by a click on those cards, and offers no text button for playing a card

#### Scenario: Plain play has no text button

- **WHEN** it is the human seat's turn and a card in the hand is a legal plain play
- **THEN** clicking that card sends that play, and the actions row has no button for that same play

#### Scenario: Marriage stays a button

- **WHEN** it is the human seat's turn to lead and both a plain play of a marriage card and declaring that marriage are legal
- **THEN** clicking the card sends the plain play, and a text button remains for declaring the marriage

#### Scenario: No declaration when sixty-six is reached

- **WHEN** the human seat has just won a trick and has at least 66 counting eyes
- **THEN** the deal is already ended and the page does not offer a declaration that ends the deal

#### Scenario: Refused action

- **WHEN** the human seat submits an action the game refuses
- **THEN** the cards and scores shown are unchanged and the human seat is still to play

### Requirement: Show the computer's completed action

After the computer seat plays, the page SHALL show the card it played, using the selected pack's drawing and the selected pack's card name, and any marriage, trump exchange, talon close, or declaration it made, without showing any card that remains in its hand.

#### Scenario: Played card becomes visible

- **WHEN** the computer seat plays a card to the trick
- **THEN** the page shows that card in the trick using the selected pack and still hides the computer seat's remaining cards

#### Scenario: Notice uses the doppeldeutsche name

- **WHEN** the computer seat plays Karo Dame and Doppeldeutsch is selected
- **THEN** the notice names that card as Schelle Ober

### Requirement: Confirm a computer answer before the trick is taken

When the computer seat has played a card in answer to the human seat's lead and that trick has not yet been awarded, the page SHALL show both cards face up. It SHALL offer one confirmation button whose label is German, and SHALL offer no card play, marriage, trump exchange, talon close, or declaration. Choosing that button SHALL send the confirmation to the game. Until the game awards the trick, the eyes and won tricks on the page SHALL be those from before the answer. The page SHALL NOT ask the computer seat to move while the answer is waiting. Loading the page again during the wait SHALL show the same two cards and the same confirmation button.

#### Scenario: Both cards stay on the table

- **WHEN** the human seat has led, the computer seat has answered, and the human seat has not confirmed
- **THEN** the page shows the human seat's card and the computer seat's answering card face up, and the eyes and won tricks do not include that trick

#### Scenario: Confirmation is the only offered action

- **WHEN** that answering card is waiting
- **THEN** the only action the page offers is a German confirmation button

#### Scenario: Choosing confirmation collects the trick

- **WHEN** the human seat chooses the confirmation button
- **THEN** the page sends that confirmation and then shows the trick awarded, including the updated eyes

#### Scenario: The computer is not asked to move during the wait

- **WHEN** that answering card is waiting
- **THEN** the page does not request another move from the computer seat

#### Scenario: Reloading keeps the answer visible

- **WHEN** the page is loaded again while the answering card is still waiting
- **THEN** both cards are face up and the confirmation button is offered again

### Requirement: Show the end of a deal and of the match

When a deal ends, the page SHALL show which seat won, the game points awarded, and both seats' counting eyes. When the match ends, the page SHALL show which seat won the match and each seat's Bummerl count. The page SHALL offer another deal while the match is unfinished, and SHALL NOT offer another deal after the match has ended.

#### Scenario: Deal result

- **WHEN** a deal ends because a seat reached 66 counting eyes
- **THEN** the page shows the winner, the game points awarded, and both eye totals

#### Scenario: Match result

- **WHEN** a seat is charged its second Bummerl
- **THEN** the page names the other seat as the match winner and does not start another deal

### Requirement: Table copy is German

The human table SHALL present its headings, turn and dealer lines, score-row names, talon and trump notes, banners, deck-choice labels, action button labels, and face-down card names in German. Player-visible card names SHALL follow the selected pack: French names stay the engine tokens, and Doppeldeutsch uses Herz, Schelle, Grün, Eichel, Ass, Zehner, König, Ober, and Unter. Action ids, JSON field names, and card tokens SHALL stay unchanged. The document language SHALL be German.

#### Scenario: Opening chrome is German

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the section headings, the dealer and turn line, and the deck-choice labels are in German, and the document language is German

#### Scenario: Action buttons are German

- **WHEN** it is the human seat's turn and legal actions include exchanging the trump jack, closing the talon, or declaring a marriage
- **THEN** each offered text button's visible label is German, the action id is the same as before, and no text button is shown for a plain card play

#### Scenario: Trump exchange uses Unter

- **WHEN** Doppeldeutsch is selected and exchanging the trump jack is offered
- **THEN** the button names the Unter and does not name the Bube

#### Scenario: Result banners are German

- **WHEN** a deal or the match ends, or the table reports a missing API key or a replaced computer choice
- **THEN** the banner text shown to the human seat is German

### Requirement: Choose the pack on the table

The page SHALL offer a choice between Französisch and Doppeldeutsch. Choosing a pack SHALL change the face drawings and the player-visible card names immediately, including cards already on the table, and SHALL NOT change the deal, the scores, or whose turn it is. The choice SHALL be remembered and reused by the table and by the deck preview. Until the player chooses, the page SHALL use Französisch.

#### Scenario: Switch drawings without touching the deal

- **WHEN** the human seat selects Doppeldeutsch during a deal
- **THEN** face-up cards show the doppeldeutsche drawings and the deal, the scores, and the turn are unchanged

#### Scenario: Choice is remembered

- **WHEN** the human seat has selected Doppeldeutsch and opens the table again
- **THEN** the table still shows Doppeldeutsch

### Requirement: Reveal the last text sent to Jev and the answer

The page SHALL offer one button that shows and hides three boxes for the last decision request sent to Jev. The boxes SHALL be hidden until the human seat uses that button. The visible button label and the three box headings SHALL be German. The headings SHALL name the game rules, the current cards and options, and the result.

The rules box SHALL show the rules statement from that request and nothing else. The cards box SHALL show the remainder of that same request, including the computer seat's cards as they were when the request was sent, the public table, and the legal actions. The result box SHALL show each answer Jev returned for that turn, in the order the answers were returned. The three boxes together SHALL be the text that was sent and the answers that came back. They SHALL NOT include the API key.

Before any decision request has been sent, each box SHALL say that nothing has been sent yet and SHALL NOT show rules, cards, options, or an answer. A later turn that sends no request SHALL leave the three boxes unchanged. Reloading the page SHALL show the same three texts.

When a request fails, the result box SHALL say that the request failed and SHALL NOT show an answer that was not returned.

#### Scenario: Button reveals three boxes

- **WHEN** a computer turn has sent a decision request and the human seat uses the reveal button
- **THEN** the page shows a rules box, a cards-and-options box, and a result box, with German headings, and those boxes were hidden before the button was used

#### Scenario: Rules and cards split the sent text

- **WHEN** the three boxes are shown after a decision request
- **THEN** the rules box is the rules statement from that request, the cards box is the rest of that request, and neither box contains the API key

#### Scenario: Result is the returned answer

- **WHEN** Jev returns one legal action and the three boxes are shown
- **THEN** the result box shows that returned answer

#### Scenario: A second answer stays in order

- **WHEN** Jev is asked twice on one turn and the three boxes are shown
- **THEN** the result box shows the first returned answer and then the second, and the rules and cards boxes still show the one shared request

#### Scenario: A failed request has no invented answer

- **WHEN** a decision request fails and the three boxes are shown
- **THEN** the result box says the request failed and does not show an action id

#### Scenario: Nothing sent yet

- **WHEN** the human seat opens the three boxes before any decision request has been sent
- **THEN** each box says that nothing has been sent yet

#### Scenario: Reload keeps the last exchange

- **WHEN** the human seat reloads the page after a decision request
- **THEN** the three boxes still show that request and its answers

### Requirement: Lay the board out horizontally

The page SHALL place the computer seat, the center of the table, and the human seat in one horizontal row. The computer seat's cards SHALL be to the left of the center. The human seat's cards SHALL be to the right of the center. The center SHALL contain the current trump, or the note that replaces it once the trump card is gone, the current talon, and the cards of the current trick. The title, the pack choice, and the turn line SHALL share one row above the board. Deal or match banners SHALL stay above the board. Action buttons, including the confirmation that a computer answer has been seen, SHALL stay with the human seat. Augen, the game points still needed, and the Bummerl counts SHALL be shown below that row. The control that reveals the last text sent to Jev SHALL be in that same lower area. The playing surface SHALL use the full available screen width, and the card drawings SHALL scale with that width. The page SHALL NOT keep the board in a narrower fixed-width column than the viewport. The center SHALL be one row of about one card height: trump, a compact face-down talon stack with its count, and the current trick beside each other. The page SHALL NOT stack a full face-down card for every remaining talon card. When no deal or match banner is shown, Augen, points still needed, and Bummerl SHALL be visible in the same viewport as the two hands.

#### Scenario: Opening seats face each other

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the computer seat's five face-down cards are left of the trump and talon, the human seat's five cards are right of the trump and talon, and Augen, points still needed, and Bummerl are below both hands

#### Scenario: The trick stays between the hands

- **WHEN** the current trick contains one or two cards
- **THEN** those cards are shown in the center, between the computer seat and the human seat, and are not shown inside either hand

#### Scenario: The talon stays in the center when it is closed

- **WHEN** the talon is closed
- **THEN** the closed-talon note is in the center, between the two hands

#### Scenario: Scores and the Jev control sit below the cards

- **WHEN** the page is shown during a deal
- **THEN** Augen, points still needed, Bummerl, and the Jev reveal control are below the computer hand, the center, and the human hand

#### Scenario: Play controls stay with the human seat

- **WHEN** it is the human seat's turn, or a computer answer is waiting to be confirmed
- **THEN** the offered action buttons are in the human seat's region, to the right of the center

#### Scenario: The board fills the screen width

- **WHEN** the page is shown in a viewport
- **THEN** the playing surface spans that viewport's width, and the cards scale with that width instead of remaining a fixed size inside a narrower column

#### Scenario: Title, pack, and turn share one row

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the title, the pack choice, and the turn line sit on one row above the board

#### Scenario: The talon is a short stack

- **WHEN** nine face-down talon cards remain
- **THEN** the center shows the talon count and a compact face-down stack whose height is about one card, not nine separate card heights

#### Scenario: Scores stay on the opening screen

- **WHEN** a deal has just been dealt and no deal or match banner is shown
- **THEN** Augen, points still needed, and Bummerl are visible in the same viewport as the two hands
