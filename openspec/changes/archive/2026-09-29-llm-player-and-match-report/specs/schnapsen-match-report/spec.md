# Spec Delta

## Purpose

Play a fixed number of rounds of every AI player against every other AI player, with no person seated, and write an HTML report of how they did.

## ADDED Requirements

### Requirement: Play n rounds of every AI against every other AI

The harness SHALL seat only Jev, the random player, and the LLM. It SHALL NOT seat the person. It SHALL play every ordered pair of two different players from that set. For each pair it SHALL play the number of rounds the caller requests, and SHALL play 10 rounds when the caller does not request a number. One round SHALL be one deal. The first player of the pair SHALL sit on the left and the second SHALL sit on the right. A player SHALL NOT be paired with itself. Each deal SHALL continue until it ends, and each turn SHALL be taken by the player bound to the seat that is to play. The harness SHALL start the next deal itself. It SHALL NOT ask a player to choose the action that starts the next deal. When a match ends before that pair's requested rounds are done, the harness SHALL start a new match with the same two players in the same seats and SHALL continue until that pair's rounds have ended, then SHALL go on to the next pair.

#### Scenario: The default run covers six pairings

- **WHEN** the harness is started without a round count
- **THEN** it plays ten rounds of each of Jev against the random player, the random player against Jev, Jev against the LLM, the LLM against Jev, the random player against the LLM, and the LLM against the random player, and it seats no person

#### Scenario: A requested count replaces the default

- **WHEN** the harness is started with a round count of 2
- **THEN** each of those six pairings is played for two rounds and then the run stops

#### Scenario: A player does not play itself

- **WHEN** the harness builds its pairings
- **THEN** it does not play Jev against Jev, the random player against the random player, or the LLM against the LLM

#### Scenario: A finished match does not stop the pairing

- **WHEN** a match ends and that pairing still has rounds remaining
- **THEN** a new match starts with the same two players in the same seats and rounds continue until that pairing's count is done

#### Scenario: The next deal is not a player choice

- **WHEN** a deal ends and the match has not ended
- **THEN** the next deal starts without a decision request to Jev or to ChatGPT

### Requirement: Stop before the first deal when a key is missing

Before the first card is played, the harness SHALL require a usable `jef.api` and a usable `chat.api`. When either file is missing, unreadable, or blank, the harness SHALL play no round, SHALL write no report, and SHALL stop with a failure. It SHALL NOT call Jev and SHALL NOT call ChatGPT in that case.

#### Scenario: The chat key is missing

- **WHEN** the harness is started and `chat.api` is missing or blank
- **THEN** no round is played, no report file is written, and ChatGPT is not called

#### Scenario: Jev's key is missing

- **WHEN** the harness is started and `jef.api` is missing or blank
- **THEN** no round is played, no report file is written, and Jev is not called

### Requirement: Write a self-contained HTML report

After every pairing's rounds have ended, the harness SHALL write one HTML file. When the caller does not name a path, that file SHALL be `reports/ai-rounds.html` under the repository root. The file SHALL show its contents without loading any other file or making a network request. It SHALL name the model `gpt-6-sol` and the number of rounds per pairing. It SHALL show each of the six pairings, and for every round in a pairing the winner, both players' counting eyes, and the game points awarded. For Jev, the random player, and the LLM, across all rounds that player sat, it SHALL show deals won, matches won, game points scored, the sum of that player's counting eyes at the end of each of those rounds, Bummerl charges against that player, and the number of turns finished by the predetermined legal action. It SHALL name the players Jev, Random, and LLM. It SHALL NOT contain either API key.

#### Scenario: The default file is written

- **WHEN** the default run finishes and the caller did not name a report path
- **THEN** `reports/ai-rounds.html` exists and names `gpt-6-sol`, Jev, Random, LLM, and ten rounds per pairing

#### Scenario: Each player is summarized across opponents

- **WHEN** the report is opened after a finished run
- **THEN** it shows a section for each pairing and, for each of the three players, deals won, matches won, game points, summed counting eyes, Bummerl charges, and predetermined-action turns

#### Scenario: The report stands alone

- **WHEN** the HTML file is opened with no network and without the rest of the repository
- **THEN** the pairing sections and the player summary are visible

#### Scenario: Keys are absent

- **WHEN** the report is written
- **THEN** the file does not contain the contents of `jef.api` or `chat.api`

### Requirement: Supplied answers do not call out

When the caller supplies the Jev answers, the random cards, and the LLM replies, the harness SHALL play every pairing with those supplies and SHALL NOT call Jev or ChatGPT. The report SHALL still be written for the rounds that were played.

#### Scenario: Scripted players finish offline

- **WHEN** the harness is run for one round per pairing with supplied Jev answers, supplied random cards, and supplied LLM replies
- **THEN** all six pairings are recorded in the report and neither Jev nor ChatGPT is called
