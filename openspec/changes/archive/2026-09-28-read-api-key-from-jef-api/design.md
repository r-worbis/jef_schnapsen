# Design

## Context

See proposal.md for why. `schnapsen/player.py` and `decide.py` each refuse to call Jev when `TYPESAFE_API_KEY` is missing or blank, then construct `TypeSafeClient()` with no `api_key`. The SDK treats an omitted `api_key` as a request to read that same environment variable, so a file check alone would not retire it. `jef.api` is already a single token on one line at the repository root. There is no root `.gitignore`. The "do not write the key" requirements stay, with the key file kept untracked.

## Goals / Non-Goals

**Goals:**

- One read of `jef.api` that production and tests use, resolved from the package location so the working directory does not matter.
- Pass the stripped file text as `TypeSafeClient(api_key=...)`.
- Keep today's missing-key outcomes: Schnapsen sets `missing-key` and plays nothing; `decide.py` exits non-zero and prints no answers.
- Ignore `jef.api` in git so the token is not committed.

**Non-Goals:**

- Creating or rewriting the contents of `jef.api`.
- Accepting `.env` files, command-line key arguments, or a fallback to `TYPESAFE_API_KEY`.
- Changing the questions sent to Jev or the Schnapsen rules.
- Printing the key in tests, logs, or the table page.

## Decisions

### Read the file from a helper next to the game package

Add `schnapsen/keyfile.py` with a path of `Path(__file__).resolve().parents[1] / "jef.api"` and a function that returns the stripped file text, or `""` when the file is missing or cannot be read. `perform_computer_turn`, `decide.py`, and tests that need a key call that function. `decide.py` imports it from `schnapsen`, which is importable when the script is launched from the repository root or by path.

Alternative: duplicate the read in each file. Rejected because the two gates already drifted into the same environment check and would drift again. Alternative: resolve `jef.api` from the process working directory. Rejected because `python -m schnapsen` can be started from another directory and would then miss the file.

### Pass `api_key` and do not touch the environment

After a non-empty read, construct `TypeSafeClient(api_key=key)`. Do not assign `os.environ["TYPESAFE_API_KEY"]`. An empty read keeps the existing early return and never constructs the live client.

Alternative: copy the file into the environment and keep `TypeSafeClient()`. Rejected because the SDK would still be using the environment variable the change is removing, and a leaked process environment would keep the old contract alive.

### Tests read `jef.api`

Tests that today patch `TYPESAFE_API_KEY` to `"test-key"` instead call the same helper and use whatever token is in `jef.api`. They do not invent a substitute key and do not print the token. Game-logic tests may still inject a fake Jev client so they do not hit the network; the gate that decides whether a turn is allowed uses the real file.

Missing-key tests must not rely on an empty environment variable. They temporarily point the helper at a missing or whitespace-only path, or they run with the real file hidden, while `TYPESAFE_API_KEY` is set, so the suite proves the environment variable is ignored. Restore the real file afterward.

Tests that construct the live `TypeSafeClient` pass the helper's return value as `api_key`. If `jef.api` is missing, those tests skip or fail with a message that names `jef.api`, not a request to set `TYPESAFE_API_KEY`.

The server module docstring drops the `TYPESAFE_API_KEY=...` start line and names `jef.api`. The missing-key banner in `schnapsen/page.html` names `jef.api` and no longer tells the player to set the environment variable. `tests/test_table.py` currently asserts the docstring contains `TYPESAFE_API_KEY`; that assertion changes with the docstring.

### Gitignore the key file

Add a repository-root `.gitignore` that lists `jef.api`. Do not put the token into any tracked file. A test reads `.gitignore` and asserts the line is present; it does not read `jef.api` into an assertion string.

## Risks / Trade-offs

- [Plaintext key stays in `jef.api` on disk] → Gitignore keeps it untracked. Programs and tests do not copy it into the page, the HTTP view, logs, specs, or assertion messages. A failed read is treated as a missing key, not as an exception that might include the path contents in a response.
- [Operators who only export `TYPESAFE_API_KEY` will see a missing key] → The table and the server docstring name `jef.api`. Rollback is restoring the environment check.
- [Tests that need a key fail when `jef.api` is absent] → That is the same condition as a live run without a key. Missing-key tests cover the empty-file path without requiring the operator file to be deleted permanently.
- [A key with internal whitespace passes the empty check and then fails inside the SDK] → The current file has no internal whitespace. That failure uses the existing request-failure path (Schnapsen fallback, or an exception from `decide.py`) and is not a new key source.

## Migration Plan

1. Add `.gitignore` with `jef.api`, add the helper, and switch both callers and the tests.
2. Update the banner, docstring, and tests so they name `jef.api` and read that file.
3. Start `python -m schnapsen` with no `TYPESAFE_API_KEY` set. The computer seat calls Jev when `jef.api` has the key, and shows the missing-key banner when that file is absent.
4. Rollback by returning the environment check and the `TypeSafeClient()` call with no `api_key`, and by dropping the ignore rule if it is unused.
