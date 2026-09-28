# Spec Delta

## MODIFIED Requirements

### Requirement: Accept only legal human actions

On the human seat's turn, the page SHALL offer every action that is legal for that seat and SHALL offer no action that is illegal. A plain card play SHALL be offered only by clicking that card in the hand, and SHALL NOT also be offered as a text button. Every other legal action SHALL still be offered as a text button, including exchanging the trump jack, closing the talon, declaring a marriage, declaring 66 eyes, continuing without declaring, confirming a seen reply, and starting the next deal, including when exchange or closing is combined with a play or a marriage. Choosing an offered action SHALL send that action to the game. The page SHALL NOT change the deal when the game refuses the action.

#### Scenario: Only legal cards can be played

- **WHEN** it is the human seat's turn to follow and the talon is exhausted
- **THEN** the page offers only the cards the game considers legal plays, by a click on those cards, and offers no text button for playing a card

#### Scenario: Plain play has no text button

- **WHEN** it is the human seat's turn and a card in the hand is a legal plain play
- **THEN** clicking that card sends that play, and the actions row has no button for that same play

#### Scenario: Marriage stays a button

- **WHEN** it is the human seat's turn to lead and both a plain play of a marriage card and declaring that marriage are legal
- **THEN** clicking the card sends the plain play, and a text button remains for declaring the marriage

#### Scenario: Declare when eligible

- **WHEN** the human seat has just won a trick and has at least 66 counting eyes
- **THEN** the page offers a declaration that ends the deal

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

### Requirement: Table copy is German

The human table SHALL present its headings, turn and dealer lines, score-row names, talon and trump notes, banners, deck-choice labels, action button labels, and face-down card names in German. Player-visible card names SHALL follow the selected pack: French names stay the engine tokens, and Doppeldeutsch uses Herz, Schelle, Grün, Eichel, Ass, Zehner, König, Ober, and Unter. Action ids, JSON field names, and card tokens SHALL stay unchanged. The document language SHALL be German.

#### Scenario: Opening chrome is German

- **WHEN** a deal has just been dealt and the page is shown to the human seat
- **THEN** the section headings, the dealer and turn line, and the deck-choice labels are in German, and the document language is German

#### Scenario: Action buttons are German

- **WHEN** it is the human seat's turn and legal actions include exchanging the trump jack, closing the talon, declaring a marriage, or declaring 66
- **THEN** each offered text button's visible label is German, the action id is the same as before, and no text button is shown for a plain card play

#### Scenario: Trump exchange uses Unter

- **WHEN** Doppeldeutsch is selected and exchanging the trump jack is offered
- **THEN** the button names the Unter and does not name the Bube

#### Scenario: Result banners are German

- **WHEN** a deal or the match ends, or the table reports a missing API key or a replaced computer choice
- **THEN** the banner text shown to the human seat is German

## ADDED Requirements

### Requirement: Choose the pack on the table

The page SHALL offer a choice between Französisch and Doppeldeutsch. Choosing a pack SHALL change the face drawings and the player-visible card names immediately, including cards already on the table, and SHALL NOT change the deal, the scores, or whose turn it is. The choice SHALL be remembered and reused by the table and by the deck preview. Until the player chooses, the page SHALL use Französisch.

#### Scenario: Switch drawings without touching the deal

- **WHEN** the human seat selects Doppeldeutsch during a deal
- **THEN** face-up cards show the doppeldeutsche drawings and the deal, the scores, and the turn are unchanged

#### Scenario: Choice is remembered

- **WHEN** the human seat has selected Doppeldeutsch and opens the table again
- **THEN** the table still shows Doppeldeutsch
