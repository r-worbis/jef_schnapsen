# Proposal

## Why

The Schnapsen table and the sample decision script refuse to call Jev unless `TYPESAFE_API_KEY` is set in the environment. The key the operator wants to use is already stored as a single token in `jef.api` at the repository root. Production and tests should read that file, and the file should stay untracked so the token is not committed.

## What Changes

- Read the TypeSafe API key from `jef.api` at the repository root for the Schnapsen computer seat, `decide.py`, and the tests that need a key.
- Pass that key into `TypeSafeClient` explicitly. The SDK otherwise still reads `TYPESAFE_API_KEY`, which would keep the environment variable in force.
- Treat a missing, unreadable, empty, or whitespace-only file the same way a missing environment key is treated today: no decision request, and no computer action or printed answers.
- **BREAKING**: `TYPESAFE_API_KEY` is no longer consulted. A process that has only the environment variable set, and no usable `jef.api`, stops as if the key were missing.
- Tell the table and the server docstring to look for `jef.api` instead of `TYPESAFE_API_KEY`.
- Add `jef.api` to `.gitignore` so the key file is not tracked. Programs still do not write the key into any other file.
- Tests that need a key read `jef.api` the same way production does. They do not patch `TYPESAFE_API_KEY` with a fake token. They do not print the key.

Assumption: both callers switch. The file sits at the repository root and both programs currently share the same environment variable.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `schnapsen-jev-player`: The computer seat reads the API key from `jef.api` instead of the environment. Tests that exercise a computer turn with a key also read that file. A missing or empty file still blocks the decision request and the computer action, and the table still shows that the key is missing. `jef.api` is gitignored.
- `jev-decisions`: `decide.py` and its tests that need a key read `jef.api` instead of the environment. A missing or empty file still exits non-zero without printing answers. The script still does not write the key. `jef.api` is gitignored.

## Impact

- `schnapsen/player.py` currently gates on `os.environ["TYPESAFE_API_KEY"]` and then constructs `TypeSafeClient()` with no `api_key`.
- `schnapsen/server.py` documents `TYPESAFE_API_KEY=... python -m schnapsen`.
- `schnapsen/page.html` tells the human seat to set `TYPESAFE_API_KEY`.
- `decide.py` uses the same environment check before `TypeSafeClient()`.
- `tests/test_table.py` patches `TYPESAFE_API_KEY` for successful turns, the missing-key path, and the server docstring. Those patches go away in favor of `jef.api`.
- There is no root `.gitignore` today. One is added with `jef.api`.
- Main specs `openspec/specs/schnapsen-jev-player/spec.md` and `openspec/specs/jev-decisions/spec.md` require the environment as the key source. Those requirements change. The "do not write the key" behavior stays, with `jef.api` kept out of version control.
- No new dependency. `jef.api` already exists as one line with no `=` and no internal whitespace.
