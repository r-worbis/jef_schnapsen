# Spec Delta

## MODIFIED Requirements

### Requirement: Draw after an open trick

After a trick while the talon is open and the winner does not already have at least 66 counting eyes, the winner SHALL draw the top talon card and the opponent SHALL draw the next card. The face-up trump SHALL be the last card drawn. No seat SHALL draw after the talon is closed or after it has been exhausted.

#### Scenario: Winner draws first

- **WHEN** a trick is won, the winner has fewer than 66 counting eyes, and at least two cards remain in the talon
- **THEN** the winner receives the first of those cards and the opponent receives the second

#### Scenario: No draw from a closed talon

- **WHEN** a trick is won after the talon was closed
- **THEN** neither seat draws a card

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
