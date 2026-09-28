# Spec Delta

## ADDED Requirements

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
