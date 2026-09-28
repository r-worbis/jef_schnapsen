# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
