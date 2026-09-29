# Proposal

## Why

Each LLM turn is a new two-message Chat Completions request, and the user message repeats the full weiches Schnapsen rules. Those rules are paid for on every card, and the provider has no stable prefix to cache. One deal should be one conversation so the rules are stated once for that deal and later turns of the deal reuse that prefix.

## What Changes

- Each seat bound to the LLM keeps one Chat Completions conversation for the current deal. The next deal, including a later deal of the same match, starts a new conversation and does not keep the previous deal's messages. The left and right seats do not share a conversation, so one seat's unplayed cards are never written into the other seat's messages.
- The rules statement and the standing instruction to answer with one action id are the first system message. Later user messages of that deal do not repeat the rules. That first message is resent unchanged on every later turn of the deal, which is what lets prompt caching reuse it. The next deal sends the rules once, in its own first message.
- Each turn adds one user message with the same hand, public table, and legal actions that Jev already receives for that seat, without the rules text. The reply that is accepted is appended as the assistant message. An illegal first reply is not appended; the retry sends the same message list. When the choice is replaced, the assistant message is the predetermined action that was applied.
- Earlier messages of the deal are not edited, reordered, or given a new timestamp. The request sets `prompt_cache_key` to a value that stays the same for that seat for the whole deal and differs between seats and between deals.
- Jev still receives the rules on every request. The engine still applies only a legal action. Farbzwang and then Stichzwang, once the talon is exhausted or closed, stay the engine's check. The model stays `gpt-6-sol` and the key stays `chat.api`. One game is one deal.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `schnapsen-llm-player`: The ChatGPT request for an LLM seat becomes one append-only conversation per deal, with the rules only in the first message of that deal and a stable cache prefix until the next deal. This capability is specified by the unarchived change `llm-player-and-match-report` and is not yet under `openspec/specs/`. That change's requirement that every question contain the rules statement together with the hand is what this change narrows: the rules stay in the deal's conversation once, and each new user message carries the current position only.

## Impact

- `schnapsen/llm_player.py` builds the message list and keeps completed turns. The history follows the current `Deal` object. `start_deal` replaces that object, which is how the next deal starts empty without an extra reset call. The page and the harness reuse one `LlmPlayer` across deals.
- `tests/test_llm.py` currently expects the second message to equal the full `jev_state`, including the rules. That assertion changes. Jev's request in `schnapsen/player.py` does not.
- The call stays `POST https://api.openai.com/v1/chat/completions` with the Python standard library. No package is added. The Jev reveal, the random player, and the engine's legality checks are unchanged.
