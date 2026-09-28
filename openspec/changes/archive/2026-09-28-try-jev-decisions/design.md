# Design

## Context

See proposal.md for why. The repository has no application code. Python 3.14.4 is available, which satisfies the SDK's Python 3.10 minimum. Jev is reached only as a hosted API. There is no local model and no self-hosted weights.

## Goals / Non-Goals

**Goals:**

- One synchronous script that performs a single `system_one` call and prints the three answers.
- The first run matches the official quick start sample, so a bad key or a wrong package is obvious.
- The API key stays in the environment.

**Non-Goals:**

- A CLI that accepts arbitrary documents or user-defined questions.
- Async clients, retries beyond the SDK default, HTTP/2, or a typed Pydantic response model.
- Calling the parody Jef MCP server, or any gateway other than `api.typesafe.ai`.

## Decisions

### Official Python SDK, sync client

Use `typesafe-sdk` and `TypeSafeClient` from `typesafe_sdk`. The client reads `TYPESAFE_API_KEY` and defaults to `jev-latest`, then `POST`s `https://api.typesafe.ai/v1/systemone`.

Alternatives:

- Raw HTTP with `curl` or `urllib` repeats the request shape the SDK already types, and drops the default retry and error types.
- The PyPI names `typesafe` and `typesafe-ai` are not TypeSafe's package. `typesafe` is unrelated. `typesafe-ai` is a third-party shim. Install `typesafe-sdk` only.
- The hosted parody at `https://typosafe.lol/mcp` is a different product and is not used.

### One script, one dependency file

Add `decide.py` at the repository root and `requirements.txt` containing `typesafe-sdk`. The repository has no package layout yet, so a virtualenv plus `pip install -r requirements.txt` is enough. The script uses the sync client because it runs once and exits.

### Fixed sample from the quick start

Hard-code the Stripe support-ticket text and the three questions (team Choice, frustration Score, urgency Noul) from the TypeSafe quick start. Do not assert the published example's exact labels in a test. Model versions move, and the contract is the answer shape, not a frozen classification.

### Key handling

The script never accepts the key as an argument and never writes it. Document `export TYPESAFE_API_KEY=...` in the task list. Do not add a `.env` file to the repository. If a local env file is used later, it stays untracked.

## Risks / Trade-offs

- [The account and key are created in a browser by the operator] → Tasks list the console URLs as manual steps. Implementation of the script can proceed, and a live call waits on the key.
- [A live call spends the account credit] → The sample is one short document. Published price is $0.042 per million input tokens, so one run is negligible against the starting credit.
- [Docs show specific answers for the sample] → The script prints whatever Jev returns. Success is a typed answer of the right shape, not a match to the quick start's printed numbers.
- [Network or a rejected key] → Let the SDK raise. A missing key exits before any request. Other API failures surface as the SDK's error and a non-zero exit.

## Migration Plan

Nothing to migrate. Rollback is deleting `decide.py` and `requirements.txt`.

## Open Questions

None. The operator's own decisions replace the sample in a later change, after this call succeeds.
