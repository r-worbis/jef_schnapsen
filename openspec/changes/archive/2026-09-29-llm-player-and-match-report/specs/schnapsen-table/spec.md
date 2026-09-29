# Spec Delta

## ADDED Requirements

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
