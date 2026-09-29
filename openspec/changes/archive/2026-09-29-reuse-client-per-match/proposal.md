# Proposal

## Why

Each Jev turn opens a new TypeSafe client, and each LLM turn opens a new ChatGPT connection. Both close before the next turn. A match is a long series of those turns, so automatic play spends time on a fresh connection for every decision. Each player should keep one client for the match and replace it only when the next match starts.

## What Changes

- A match that asks Jev uses one live TypeSafe client for every Jev turn of that match, including the second ask after an illegal choice and including later deals of the same match. Both Jev seats share that client.
- A match that asks the LLM uses one ChatGPT connection for every live LLM turn of that match, including the second ask after an illegal reply and including later deals of the same match. Both LLM seats share that connection. A scripted reply still makes no HTTP call.
- The two clients are separate. A match of Jev against the LLM holds one of each. A Jev turn does not open the ChatGPT connection, and an LLM turn does not open the TypeSafe client.
- Starting the next match closes whichever of those clients the match opened, and the next match opens its own on the first request that needs one. A match that never asks a player opens no client for that player.
- A caller that supplies a Jev client keeps ownership of it. The game uses that client for Jev and does not open or close it. The LLM connection is still one per match.
- The text sent to Jev and to ChatGPT, the legal-action checks, the missing-key stops, and `decide.py` stay as they are. `decide.py` is a single call outside a match and stays a single client.

## Capabilities

### New Capabilities

### Modified Capabilities

- `schnapsen-jev-player`: One TypeSafe client covers every Jev turn of a match, and the next match uses a new client.
- `schnapsen-llm-player`: One ChatGPT connection covers every live LLM turn of a match, and the next match uses a new connection.

## Impact

- `schnapsen/turn.py` and `schnapsen/jev_player.py` open the live TypeSafe client once for a match instead of inside each turn. `schnapsen/llm_player.py` keeps one ChatGPT connection on the match instead of calling `urlopen` for every turn.
- `schnapsen/server.py` closes both when a new match replaces the one on the table, and when the server stops.
- `schnapsen/harness.py` and `schnapsen/prompt_harness.py` close both at the end of each match. The prompt harness asks only Jev, so it opens no ChatGPT connection. Turns of a match, including both seats, reuse the client that player already opened.
- Tests that pass a Jev client in still own that client. Tests that watch construction count one TypeSafe client per match that asks Jev, and one ChatGPT connection per match that asks the LLM.
- No new package. The request bodies stay as they are.
