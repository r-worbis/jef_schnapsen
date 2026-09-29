# Proposal

## Why

The random card player and Jev cannot be compared with a ChatGPT player, because that player does not exist yet. The same facts Jev already receives should be asked of ChatGPT, and a fixed number of rounds of every AI against every other AI should show how each one did.

## What Changes

- The current stub is renamed to the random player and stays in the game. Its kind id becomes `random`. It still proposes one plain play drawn uniformly from its own hand, and a supplied selector still makes that draw repeatable. It does not marry, exchange the trump, close the talon, call ChatGPT, or read either key file. **BREAKING**: the kind id `stub` is no longer accepted.
- A new player kind, `llm`, is added beside the person, Jev, and the random player. Either AI seat may be Jev, the random player, or the LLM. The person remains allowed only on the right. The default binding stays the person on the right and Jev on the left.
- The LLM calls ChatGPT. The model is `gpt-6-sol`. The API key is read from `chat.api` at the repository root and is not read from the environment. The question carries the same facts Jev already receives for that seat: the weiches Schnapsen rules, that seat's own cards, the public table, and the legal actions. The model's reply is the played card, as exactly one of those legal action ids. The player does not apply it.
- A reply that is not one legal action id is refused by the engine and asked once more. A second illegal reply, or a failed call, applies one predetermined legal action and the table shows that the choice was replaced. A missing or blank `chat.api` does not call ChatGPT and does not play the LLM seat. A missing `jef.api` still stops only Jev. A missing key does not stop the random player. Farbzwang and then Stichzwang, once the talon is exhausted or closed, stay the engine's check.
- `chat.api` is listed in `.gitignore`. The key is not written into any tracked file and is not printed by tests or by the report.
- On the page, the random player is still labeled Zufall and the new player is labeled LLM. Both appear on the right-seat choice and the left-seat choice. Mensch stays off the left-seat choice.
- The harness seats no person. The AI players are Jev, the random player, and the LLM. For every ordered pair of two different players it plays n rounds, default 10, with the first player on the left and the second on the right. One round is one deal. A player does not play itself. If a match ends before that pair's n rounds are done, a new match starts with the same two players. The harness writes one self-contained HTML report of every pairing and of each player across all of its rounds.
- Assumption: a bare card token or card label is accepted only when exactly one legal action plays that card. Several actions for the same card, or any other text, are not a legal reply.
- Assumption: the report is results, not a card-by-card replay. It names the model, the round count, and for each player deals won, matches won, game points, counting eyes, Bummerl charges, and turns finished by the predetermined action, grouped by pairing as well as overall.

## Capabilities

### New Capabilities

- `schnapsen-random-player`: Rename the stub to the random player, keep its uniform plain-play proposal, and refuse the old `stub` kind id.
- `schnapsen-llm-player`: Ask ChatGPT, with `gpt-6-sol` and the key in `chat.api`, for the same decision facts Jev receives, and take only a reply that names one legal played card.
- `schnapsen-match-report`: Play n rounds, default 10, of every AI player against every other AI player, with no person seated, and write an HTML report of the results.

### Modified Capabilities

- `schnapsen-table`: Offer Zufall and LLM as seat choices, and show that `chat.api` is missing without playing the LLM seat or revealing a hidden hand.

## Impact

- `schnapsen/stub_player.py` becomes the random player. A new LLM module proposes the ChatGPT action. `schnapsen/turn.py` asks Jev, the random player, or the LLM, and `apply_action` remains the only way a card is played.
- `schnapsen/server.py` accepts `random` and `llm` and rejects `stub`. The right seat may be the person, Jev, the random player, or the LLM. The left seat may be any of those except the person.
- `schnapsen/view.py` reuses the existing Jev state text as the LLM question. A new reader loads `chat.api` the same way `jef.api` is loaded, and does not log it.
- `schnapsen/page.html`: Zufall stays, LLM is added, and a missing `chat.api` stops only the LLM.
- A new harness module plays the six pairings and writes `reports/ai-rounds.html` by default. Unit tests supply scripted answers and do not call OpenAI or Jev.
- `.gitignore` gains `chat.api`. No new package is added; the call uses the Python standard library. `jef.api` and the Jev request stay as they are.
