# Design

## Context

See proposal.md for why. `schnapsen/llm_player.py` `propose` posts one Chat Completions request whose messages are a short system line plus `jev_state(match)`. `jev_state` is the rules statement plus the position. The next turn builds that pair again from scratch, so the rules are a new suffix every time and nothing in the prefix stays stable.

`jev_parts` already splits that text into the rules and the remainder. The remainder is the hand, the public table, and the legal action ids. `turn.py` `_llm_turn` calls `propose`, applies a legal id through `apply_action`, and on a second illegal reply or a failed call applies `sorted(legal_action_ids)[0]`. A scripted `reply` callable skips HTTP. The page and the harness keep one `LlmPlayer` and replace the `Match`. Jev still sends `jev_state` on every request. `tests/test_llm.py` asserts the user message equals `jev_state`.

## Goals / Non-Goals

**Goals:**

- One append-only message list per LLM seat per deal, sent to the existing Chat Completions endpoint.
- A byte-stable first message that holds the rules, and a `prompt_cache_key` that stays with that seat for that deal.

**Non-Goals:**

- Switching to the Responses API or `previous_response_id`.
- Padding the prompt so the first turn crosses a cache minimum.
- Changing Jev's request, the Jev reveal, the random player, or `_legal_follow`.
- A conversation for the scripted `reply` path, which never calls ChatGPT.

## Decisions

### Keep the history on the deal object, outside the engine

`llm_player.py` holds a `WeakKeyDictionary` from `Deal` to a dict of seat to completed messages. `start_deal` assigns a new `Deal` to `match.deal`, so the next request looks up an empty key and starts a new conversation. `new_match` does the same, because it calls `start_deal`. The two seats are two lists under the current deal. A Jev or random turn does not touch the dictionary.

Alternative: a field on `Match`. Rejected. The engine would store ChatGPT transcripts, and the match object survives the next deal. Alternative: one list on `LlmPlayer`. Rejected. That object is reused across deals and across both seats, so the next deal would inherit the previous hand.

### Put the rules only in the first message

The first message is `role: system`. Its content is the rules statement, a blank line, and the standing instruction to answer with one action id. That string is a module constant. It does not include the hand, the legal ids, or a timestamp.

Each turn's new message is `role: user` and its content is `jev_parts(match)[1]`, the remainder Jev already uses, without the rules. `response_format` still restricts `action` to the current legal ids. That schema changes every turn, so it stays outside the message list.

The request body sets `prompt_cache_key` to `str(id(match.deal))` plus the seat. The same deal object keeps the same id for every turn of that deal; the other seat and the next `start_deal` get different keys.

Alternative: repeat the rules in every user message and also keep history. Rejected. The rules would be paid for on every turn, and the prefix would change. Alternative: one conversation for the whole match. Rejected. The next deal is a new hand, and the request is that one deal is one conversation. The rules are sent again on the first turn of the next deal, and that deal then keeps its own prefix.

### Commit a turn only after an action is applied

`propose` builds `completed + [current user message]` and does not append. The retry therefore sends the same list, and the rejected reply is absent. `_llm_turn` remembers the seat before `apply_action`, because the seat to play changes when the action is applied.

After a legal reply is applied, `commit` appends the user message and an assistant message whose content is the raw reply text. After the predetermined action is applied, `commit` appends the user message and an assistant message whose content is that action id, not the rejected text and not the error. A failed call is not retried. The scripted `reply` path does not commit, because it does not send a request.

The next request starts with those completed messages unchanged, then the new user message. The cached prefix is the previous request's message list.

Alternative: append the assistant message inside `propose` before `turn.py` accepts it. Rejected. An illegal reply would then be in the retry, which the spec forbids, and a fallback would disagree with what the transcript says was played.

### Tests stay offline

Update `test_request_uses_the_jev_state_and_gpt_6_sol` so the system message contains the rules and not the hand, the user message equals the `jev_parts` remainder, the rules text occurs once, and `prompt_cache_key` is present. Add a scripted `urlopen` test that commits one applied reply and checks the second request of the same deal starts with the first request's messages. Add a retry test whose second body equals the first. Add a two-seat test and a `start_deal` test whose next request has no messages from the previous deal and a different cache key. Do not call OpenAI. Leave the Jev state tests asserting that Jev still receives the rules on that request.

## Risks / Trade-offs

- [The rules alone are shorter than the provider's cache minimum, so the first turns miss the cache] → Later turns cache the growing unchanged prefix, which includes the rules. The prompt is not padded.
- [An unknown `prompt_cache_key` field is rejected by the API] → That is a failed call. The predetermined action is played, and the requested field stays. The message prefix is the part that makes a later request cacheable even if the key is ignored.
- [`id(deal)` is reused after the deal object is collected] → The dictionary entry is gone with the object, and the next deal has no old messages to collide with. The key only has to be stable while that deal is in play.
- [Each new deal sends the rules again] → That is the requested boundary. Turns inside the deal still share one prefix. The prompt is not padded, and the previous deal's transcript is not kept.
- [A structured reply is JSON and the fallback line is a bare action id] → Both name the action that was applied. The parser already accepts both on the way in; the stored assistant text is not parsed again.
- [`schnapsen-llm-player` is not in `openspec/specs/` yet] → This delta uses MODIFIED against the requirement in the unarchived change `llm-player-and-match-report`. Archiving this change before that one is refused. Implementation does not wait on that archive.

## Migration Plan

No saved match and no action-id change. Restart the server process so the new request shape is loaded. Rollback restores the two-message `jev_state` request and deletes the transcript dictionary. Archive `llm-player-and-match-report` before archiving this change.
