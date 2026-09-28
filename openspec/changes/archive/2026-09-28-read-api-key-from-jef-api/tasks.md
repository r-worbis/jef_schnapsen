# Tasks

## 1. Key file reader and ignore rule

- [x] 1.1 Add a repository-root `.gitignore` that lists `jef.api`, and verify a test reads `.gitignore` and finds that name without reading the key file into an assertion.

- [x] 1.2 Add `schnapsen/keyfile.py` that resolves `jef.api` as `Path(__file__).resolve().parents[1] / "jef.api"`, returns the file text stripped, and returns `""` when the file is missing or cannot be read. Verify with a unit test that a missing or whitespace-only path returns `""`, and that when the real `jef.api` is present the helper returns a non-empty stripped token without printing it.

## 2. Schnapsen computer seat

- [x] 2.1 Change `perform_computer_turn` in `schnapsen/player.py` so a non-empty helper result (from `jef.api`) is passed as `TypeSafeClient(api_key=...)`, and an empty result still sets `missing-key` and returns before any client is constructed. Do not read or set `TYPESAFE_API_KEY`. Update `tests/test_table.py` so computer-turn cases that need a key call the helper on `jef.api` instead of patching `TYPESAFE_API_KEY` with `"test-key"`. Verify `python -m unittest tests.test_table.PlayerTests` passes when `jef.api` exists.

- [x] 2.2 Update the `schnapsen/server.py` docstring and the missing-key banner in `schnapsen/page.html` so they name `jef.api` and do not mention `TYPESAFE_API_KEY`. Point the docstring assertion and the served-page check in `tests/test_table.py` at that wording. For the HTTP missing-key case, hide or redirect the helper away from `jef.api` while `TYPESAFE_API_KEY` is set, then restore it. Verify `python -m unittest tests.test_table.ServerTests` passes and that the served page contains `jef.api`.

## 3. Sample decision script

- [x] 3.1 Change `decide.py` so it uses the same helper and passes a non-empty result from `jef.api` as `TypeSafeClient(api_key=...)`. When the helper returns `""`, exit non-zero and print no urgency, team, or frustration answer, even if `TYPESAFE_API_KEY` is set. Do not write the key to any file. Verify a missing-key test that does not use the real file, and a test that constructs the client with the helper's return value from `jef.api` without printing that value. Keep the fixed sample document and the three questions, and verify `python -m unittest tests.test_table.MatchTests` still sees `SAMPLE` and `system_one` in `decide.py`.
