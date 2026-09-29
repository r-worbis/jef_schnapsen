# Tasks

## 1. One request prefix per deal

- [x] 1.1 In `schnapsen/llm_player.py`, send `role: system` as a module constant of the rules statement, a blank line, and the standing action-id instruction, with no hand, legal ids, or timestamp in that string. Send `role: user` as `jev_parts(match)[1]` only. Set `prompt_cache_key` to `str(id(match.deal))` plus the seat to play. Keep `model` `gpt-6-sol` and the legal-id `response_format`. Store completed messages in a `WeakKeyDictionary` keyed by the current `Deal`, with a separate list per seat, and do not append inside `propose`. Leave the scripted `reply` path on the current interpreter, with no HTTP body. Update `tests/test_llm.py` `test_request_uses_the_jev_state_and_gpt_6_sol` so the system message contains the rules and not the hand, the user message equals the `jev_parts` remainder, the rules text occurs once, and `prompt_cache_key` is present. Verify `python -m unittest tests.test_llm.ProposalTests` passes.

## 2. Commit only the play that was applied

- [x] 2.1 Add `commit(match, seat, assistant_text)` that appends the user message from the request just sent for that seat and one assistant message. In `schnapsen/turn.py` `_llm_turn`, remember `deal.to_play` before `apply_action`. On an accepted reply, commit the raw reply text. On a second illegal reply or a failed call, commit the predetermined action id and not the rejected text. Do not commit between the two tries, so the second HTTP body is the same message list as the first. Verify with patched `urlopen` in `tests/test_llm.py` that an illegal first reply leaves the deal unchanged and the second body equals the first, that a later turn of the same deal starts with the previous messages unchanged and then the accepted reply, and that a replaced turn's next assistant message is the predetermined action id. Verify `python -m unittest tests.test_llm` passes.

## 3. Separate seats and the next deal

- [x] 3.1 Using the same player instance, verify a test that both seats bound to the LLM get different `prompt_cache_key` values and that the second seat's request does not contain a card the first seat still holds. Verify a test that `start_deal` on the same match produces a first request with no messages from the previous deal, a different `prompt_cache_key`, and the rules statement once. Verify that a Jev or random turn adds nothing to the LLM lists, and that the existing Jev tests still expect `jev_state` to include the rules. Verify `python -m unittest tests.test_llm tests.test_harness tests.test_table` passes.
