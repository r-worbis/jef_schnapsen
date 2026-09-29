# schnapsen-table Specification

## Purpose

Give the human seat a local page that shows that seat's cards and the match score, and accepts only legal actions.

## Requirements

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

### Requirement: Show the computer's completed action

After the computer seat plays, the page SHALL show the card it played, using the selected pack's drawing and the selected pack's card name, and any marriage, trump exchange, talon close, or declaration it made, without showing any card that remains in its hand.

#### Scenario: Played card becomes visible

- **WHEN** the computer seat plays a card to the trick
- **THEN** the page shows that card in the trick using the selected pack and still hides the computer seat's remaining cards

#### Scenario: Notice uses the doppeldeutsche name

- **WHEN** the computer seat plays Karo Dame and Doppeldeutsch is selected
- **THEN** the notice names that card as Schelle Ober

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

### Requirement: Offer the random player and the LLM

The page SHALL offer, on the right-seat choice, Mensch, Jev, Zufall, and LLM. The page SHALL offer, on the left-seat choice, Jev, Zufall, and LLM, and SHALL NOT offer Mensch. Zufall SHALL bind the random player. LLM SHALL bind the LLM player. The kind id `stub` SHALL NOT appear as a choice. The default choice SHALL still show Mensch on the right and Jev on the left. Wherever the page names a seat by its player kind, it SHALL use Mensch, Jev, Zufall, or LLM for those four kinds.

#### Scenario: Both AI kinds are offered

- **WHEN** the page shows the two player choices
- **THEN** the right choice includes Mensch, Jev, Zufall, and LLM, and the left choice includes Jev, Zufall, and LLM and does not include Mensch

#### Scenario: An AI seat is called by its kind

- **WHEN** the right seat is the LLM, the left seat is the random player, and it is the right seat's turn
- **THEN** the turn line names LLM and does not name that seat Zufall or Du

#### Scenario: The old stub label is gone

- **WHEN** the page shows the two player choices
- **THEN** neither choice offers a stub kind

### Requirement: Show a missing chat.api key

When the seat to play is the LLM and `chat.api` is missing, unreadable, or blank, the table SHALL show a German notice that names `chat.api` and SHALL NOT show the key. The page SHALL NOT request that turn. A missing `jef.api` SHALL NOT by itself stop an LLM turn or a random turn, and SHALL NOT replace this notice. A missing `chat.api` SHALL NOT by itself stop a Jev turn or a random turn, and SHALL NOT replace the existing notice that names `jef.api`. The page SHALL still request a random turn while either key file is missing. The response SHALL NOT include a face of a card still held by the LLM or by the random player. An LLM turn SHALL NOT place that seat's hand into the Jev reveal.

#### Scenario: The LLM waits on chat.api

- **WHEN** the seat to play is the LLM and `chat.api` is missing or blank
- **THEN** the page shows a German notice naming `chat.api`, does not request that turn, and shows no card from the LLM's hand

#### Scenario: A missing key does not stop Zufall

- **WHEN** `jef.api` and `chat.api` are missing and the seat to play is the random player
- **THEN** the page requests that turn and does not show a missing-key notice for it

#### Scenario: Jev's missing key does not stop the LLM

- **WHEN** `jef.api` is missing, `chat.api` contains a key, and the seat to play is the LLM
- **THEN** the page requests that LLM turn and does not show the notice that names `jef.api` for this turn

#### Scenario: The chat key does not stop Jev

- **WHEN** `chat.api` is missing, `jef.api` contains a key, and the seat to play is Jev
- **THEN** the page does not show the `chat.api` notice for this turn and the missing `chat.api` file does not stop the Jev request

### Requirement: Keep the seen pause for the person

When the person is playing the right seat and has led, an answering card from Jev, the random player, or the LLM SHALL wait for the person's confirmation under the existing seen rule. When the right seat is not the person, an answering card SHALL NOT wait for that confirmation.

#### Scenario: The person still confirms an LLM answer

- **WHEN** the person has led and the LLM plays the answering card
- **THEN** both cards stay in the trick until the person confirms

#### Scenario: Two AIs do not wait

- **WHEN** the random player has led and the LLM plays the answering card
- **THEN** the page offers no confirmation button and the trick is awarded without one
