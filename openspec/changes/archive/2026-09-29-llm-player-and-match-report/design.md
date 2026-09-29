# Design

## Context

See proposal.md for why. `schnapsen/stub_player.py` proposes `play:` plus a card drawn by an injected `choose` callable, or by `random.Random().choice` when none is injected. `schnapsen/turn.py` asks that player when the kind is `stub`, or asks Jev, and applies the proposal only through `apply_action`. A second illegal proposal applies `sorted(legal_action_ids)[0]` and sets `choice_replaced`. A Jev call failure does that immediately. A missing `jef.api` sets `notice` to `missing-key` and plays nothing.

`schnapsen/view.py` `jev_state` is the text Jev already receives. `schnapsen/engine.py` `is_legal` and `_legal_follow` are the Farbzwang-then-Stichzwang gate once the talon is closed or nothing remains to draw. The page kind id is `stub`, labeled Zufall. The server allows `human`, `jev`, and `stub`, and the left seat cannot be `human`. `schnapsen/keyfile.py` reads only `jef.api`. `requirements.txt` lists `typesafe-sdk` and no OpenAI package. `chat.api` is present at the repository root and is not listed in `.gitignore`.

## Goals / Non-Goals

**Goals:**

- The kind id `random` keeps today's uniform plain-play behavior, and `stub` is rejected.
- A new kind `llm` makes one Chat Completions call and returns the played card as a legal action id.
- The harness plays every ordered pairing of Jev, the random player, and the LLM, and writes one HTML file from a results object.

**Non-Goals:**

- A second follow check, or any edit to `_legal_follow`, marriages, exchange, closing, drawing, or scoring.
- Seating the person on the left, or seating the person in the harness.
- A player against itself in the harness.
- Putting the ChatGPT prompt or an AI hand into the Jev reveal.
- A card-by-card replay in the report.
- Calling OpenAI or Jev from the unit tests.
- Adding a package.

## Decisions

### Rename the stub and add the LLM beside it

`stub_player.py` becomes `schnapsen/random_player.py`. The class proposes `play:` plus one card from its hand. `choose` stays, and the default remains `random.Random().choice`. The kind id stored on the match is `random`. `POST /api/match` rejects `stub` with 400 and does not replace the match.

`schnapsen/llm_player.py` is new. It has no card selector. `propose` calls ChatGPT, or returns a failure. `turn.py` branches on `jev`, `random`, and `llm`. The server allows `human`, `jev`, `random`, and `llm` on the right, and `jev`, `random`, and `llm` on the left.

Alternative: keep the id `stub` and only change the label. Rejected. The request is to rename that player and add the LLM as another kind.

### Send `jev_state` as the user message

The HTTP call is `POST https://api.openai.com/v1/chat/completions` through `urllib.request`. The body sets `model` to `gpt-6-sol` and `temperature` to `0`. The system message tells the model to answer with exactly one action id from the legal list and no other text. The user message is `jev_state(match)` for the seat to play. The `Authorization` header is `Bearer` plus the stripped contents of `chat.api`. A new function in `schnapsen/keyfile.py` reads that path the same way `read_api_key` reads `jef.api`. The reply text is `choices[0].message.content`. A transport error, a non-200 status, or a body without that text is a failed call.

Alternative: depend on the `openai` package. Rejected. One request does not justify a new dependency.

### Accept an action id, or one card when it is unambiguous

The first non-empty line of the reply is trimmed, and one pair of surrounding quotes or a trailing period is removed. If that text is a current legal action id, it is the proposal. If it is a card token (`Herz-Ass`) or a card label (`Herz Ass`) and exactly one legal action plays that card, that action is the proposal. Otherwise the reply is illegal. `turn.py` asks the LLM once more on an illegal reply. A failed call does not ask again. The second illegal reply, or the failed call, applies the existing predetermined id and sets `choice_replaced`. The random player's illegal card uses that same retry, as it does today.

Alternative: accept only `play:` ids and drop marriages. Rejected. Jev is offered those actions from the same text, and the comparison would hide them from the LLM.

### A missing chat key is a different notice

Before a live LLM call, `take_ai_turn` reads `chat.api`. When the file is missing, unreadable, or blank, it sets `notice` to `missing-chat-key` and returns without a request or a play. `missing-key` remains the Jev case. The random player never sets either notice. `human_view` exposes `missingChatKey` beside `missingKey`. The page does not request a turn when the seat is `llm` and `missingChatKey` is set. It still requests a random turn when either notice would have been set for another player, and it still requests an LLM turn when only `missingKey` is set. The banner for `missingChatKey` is German and names `chat.api`. Neither banner includes the key. An LLM turn does not write `jev_exchange`.

The page keeps the label Zufall for `random` and adds LLM for `llm` on both selects and in the seat names. The default select values stay Mensch and Jev.

### The harness walks six pairings

`python -m schnapsen.harness` accepts `--rounds` (default 10) and `--report` (default `reports/ai-rounds.html`). It checks both key files first and exits non-zero without writing a report or calling either API when either file is missing or blank.

The pairings, in this order, are left seat then right seat: Jev and random, random and Jev, Jev and llm, llm and Jev, random and llm, llm and random. Seat ids stay `computer` for the left and `human` for the right. For each pairing it builds a match with that binding. The random seat uses `RandomPlayer` with no injected `choose`. The LLM seat uses the live proposer. Jev uses `TypeSafeClient` when the caller does not pass one.

While the deal phase is `play`, it calls `take_ai_turn` once. If that call sets `missing-key` or `missing-chat-key`, or leaves the same seat to play with the deal unchanged, the harness stops with a failure and does not write a success report. After each call it attributes `choice_replaced` to the player kind that was asked. Two AI seats never enter the acknowledge phase, so the harness does not send `seen`. When the deal has ended and the match has not, it calls `start_deal`. When `match_winner` is set before the pairing's rounds are done, it records the match and starts `new_match` with the same binding. A per-deal cap of 80 turns aborts a stuck deal. After that pairing's rounds, it starts the next pairing.

The HTML writer takes one results object for the whole run: model name, rounds per pairing, one section per pairing, and totals for Jev, Random, and LLM across every round they sat. Totals are deals won, matches won, game points, summed end-of-deal counting eyes, Bummerl charges, and predetermined-action turns. Each round row names the winner, both players' counting eyes, and the game points. The file is a single HTML document with a `<style>` block, no scripts, and no URLs. Tests call the harness with a fake Jev client, a `RandomPlayer(choose=...)`, and a scripted LLM reply, for `--rounds 1`, and assert six pairings and no socket.

### Tests stay offline

A unit test points the chat reader at a temporary file, replaces `urlopen`, and asserts the JSON model, that the user message equals `jev_state` for that match, and that the Authorization header equals `Bearer ` plus that temporary file's text. The assertion uses the temporary secret, and the test does not print it or read the repository `chat.api`. A second test asserts `.gitignore` contains the line `chat.api`. Existing selector tests construct the random player with `choose`. The page source test expects Zufall and LLM, and expects the computer-turn request to stop for `missingChatKey` only when the seat is `llm`. A binding test rejects `stub`.

## Risks / Trade-offs

- [The model name is rejected by the API] → The call is a failure, the predetermined action is played, and the report counts that turn. The requested name stays `gpt-6-sol`.
- [The model answers with a sentence] → The first line is parsed, a unique card is accepted, and anything else is retried once and then replaced. The report shows how often that happened.
- [Six pairings at ten rounds are slow and cost money] → That is the requested matrix. Jev and the LLM each sit four pairings, so the default run is 40 rounds for each of them. Unit tests use one scripted round per pairing. The harness is not part of the default test run's network.
- [A missing chat notice is confused with the Jev notice] → The notice value and the banner name the file that is actually missing, and one missing file does not block the other players. The random player ignores both.
- [`choice_replaced` is one flag on the match] → The harness reads it after the turn that was just asked, before the next turn clears it.
- [A stuck deal would loop] → Eighty turns in one deal, or a turn that does not change the deal, abort the run without a success report.
- [Callers still send `stub`] → The server returns 400 and keeps the current match. The page no longer sends that id.

## Migration Plan

No saved match and no action-id change. Add `chat.api` to `.gitignore` without committing the file. A page that still posts `stub` gets a 400 until it is reloaded with the new choices. Rollback restores the `stub` id, removes the LLM kind, and deletes the harness. A live server process picks up the new kinds on restart.
