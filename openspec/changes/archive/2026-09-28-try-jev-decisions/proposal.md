# Proposal

## Why

This repository has no application yet, and Jev cannot be tried from the model picker. A first script needs a TypeSafe account, an API key, and one call that sends state plus typed questions and prints the decisions.

## What Changes

- Add a small synchronous Python script that calls TypeSafe's Jev model (`jev-latest`) through the official `typesafe-sdk` package.
- The script sends one sample document and, in a single `system_one` call, asks one Noul, one Choice, and one Score, then prints each typed answer with its probabilities.
- The sample document and questions are the support-ticket example from the TypeSafe quick start, so the first run checks the key against a known request. Replacing that sample with other decisions is out of scope until those decisions are named.
- Account signup and key creation stay manual. The script reads `TYPESAFE_API_KEY` from the environment and never stores the key.

## Capabilities

### New Capabilities

- `jev-decisions`: Run one Jev decision call from a Python script and print Choice, Score, and Noul answers for a sample document.

### Modified Capabilities

- None. The project has no existing specs.

## Impact

- New script in an otherwise empty repository, plus a dependency on `typesafe-sdk` (Python 3.10 or newer; this machine has Python 3.14.4).
- Outbound HTTPS to `https://api.typesafe.ai/v1/systemone`. A TypeSafe account and API key are required before the script can succeed.
- No existing code, APIs, or specs change.
