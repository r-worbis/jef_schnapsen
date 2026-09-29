# Design

## Context

See proposal.md for why. `take_ai_turn` in `schnapsen/turn.py` and `_jev_turn` in `schnapsen/prompt_harness.py` each construct `TypeSafeClient` inside a `with` block for one turn, so the HTTP client closes before the next card. `LlmPlayer.propose` calls `urllib.request.urlopen` for every live turn, which opens and closes a connection each time. A caller may already pass a Jev client; the table's `Table.client` and both harness `client` arguments exist for that, and unit tests pass a fake. The LLM tests patch `urlopen` or pass a scripted `reply`. One `LlmPlayer` is reused for the whole harness run, so a connection stored on the player would outlive the match. `Match` is an engine dataclass and is not a place for an HTTP field the view would copy. `decide.py` is a single call outside a match.

## Goals / Non-Goals

**Goals:**

- One entered TypeSafe client for every Jev request of one `Match`, and one ChatGPT connection for every live LLM request of that same match. Each is closed when that match is finished or replaced.
- The same open/close rule on the table, the AI-round harness, and the prompt harness. The prompt harness asks only Jev, so it opens no ChatGPT connection.
- A caller-supplied Jev client stays untouched.

**Non-Goals:**

- Changing the request text, the conversation transcript, `prompt_cache_key`, the retry of an illegal answer, or either missing-key stop.
- Sharing one object between Jev and ChatGPT. They are different APIs.
- Opening a client for a player the match never asks.
- Adding a timeout the current `urlopen` call does not have.

## Decisions

### Open on the first request and keep each client on that match

Add one Jev helper used by both Jev turn paths. When no Jev client is supplied and the key is present, the first Jev request of a match constructs `TypeSafeClient`, enters it, and stores it on that match instance under a name the engine and the view do not read. Later Jev requests of that match, including the illegal-answer retry, the other seat, and the next deal, use the stored client. A missing key returns before construction, as it does now.

Add one LLM helper used by `LlmPlayer.propose`. When the player has no scripted `reply` and the chat key is present, the first live request of a match opens one `http.client.HTTPSConnection` for the host in the chat URL, stores it on that match the same way, and sends later live requests of that match on it. A scripted reply and a missing chat key return before a connection is opened. The request body stays the JSON `propose` already builds. Existing tests that patch `urlopen` move to a send function on that connection so they still see each request, and so they can count connections.

`close_match_clients(match)` exits a stored TypeSafe client and closes a stored ChatGPT connection, then drops both. It does nothing for a client the match does not hold. A supplied Jev client is never stored, so this close does not touch it.

Alternative: open at `new_match()` before any turn. Rejected. A match that never asks a player would open a client the spec forbids, and a missing key would open one before the key check.

Alternative: store the ChatGPT connection on `LlmPlayer`. Rejected. The harness keeps one player for every match, so the connection would survive into the next match.

Alternative: a module dict keyed by `id(match)`. Rejected. After a match is discarded, a new match can reuse that id. The instance attribute dies with the match it belongs to.

### Callers close at the match boundary

The helpers do not know when a match is over. Each owner calls `close_match_clients` in a `finally` so an error still closes both:

- `start_match` closes the clients of the match being replaced, then installs the new match. `main` closes the table's current match when the server stops.
- `play_rounds` and `play_prompts` close the clients of each `new_match()` when that match's loop ends, before the next match is created, and after the last match.

The prompt harness stops opening its own `with` block and uses the Jev helper, so a prompt match cannot drift back to one TypeSafe client per turn.

Alternative: leave closing to garbage collection. Rejected. Exiting the TypeSafe client and closing the HTTPS connection is what releases them, and a dropped match would not do that.

## Risks / Trade-offs

- [A new call site forgets `close_match_clients`] → The table and both harnesses are the only owners of a live match loop. Tests that open a client through a turn without a supplied Jev client must close the match. `test_live_client_receives_jef_api_key` today expects `__exit__` inside the turn; it will expect one `__enter__` and an `__exit__` only from the match close.
- [LLM tests patch `urlopen`] → Those patches move to the send function. The assertions on URL, model, messages, and `prompt_cache_key` stay. New assertions count one connection per match.
- [The table serves requests on several threads] → `submit_action` and `advance_computer` already hold `table.lock` across the AI call. The stored clients are used only under that lock.
- [A long match holds one connection per player it asked] → That is the point of the change. The SDK timeout and retry stay on the TypeSafe client. A later match still gets new clients.

## Migration Plan

No stored data. Rollback is restoring the per-turn `with` block and the per-turn `urlopen`, and dropping the close calls.

## Open Questions

None.
