# Tasks

## 1. Account and API key

These steps happen in the browser and in your shell. They are not something the script can do for you.

- [X] 1.1 Open https://console.typesafe.ai/ and create an account, or log in if you already have one. Verify you reach the TypeSafe console rather than the marketing site at https://typesafe.ai/.
- [X] 1.2 Open https://console.typesafe.ai/keys and create an API key. Verify the keys page shows the new key. Copy it when it is shown. Do not paste it into this repository, into chat, or into a committed file.
- [X] 1.3 Optional check before writing code: open https://console.typesafe.ai/playground, paste any short text as state, and add one Noul question. Verify the playground returns a probability. The quick start sample and question shapes are at https://docs.typesafe.ai/introduction/quickstart.
- [X] 1.4 In the shell you will use to run the script, set the key with `export TYPESAFE_API_KEY='your-key'`. Verify it is set without printing it: `test -n "$TYPESAFE_API_KEY" && echo "TYPESAFE_API_KEY is set"`.

## 2. Script

- [x] 2.1 Add `requirements.txt` containing only `typesafe-sdk`. Create a virtualenv with Python 3.10 or newer and install it with `pip install -r requirements.txt`. Verify with `python -c "import typesafe_sdk"` from that virtualenv. Package page: https://pypi.org/project/typesafe-sdk/. SDK docs: https://docs.typesafe.ai/sdk/python. Do not install the PyPI packages named `typesafe` or `typesafe-ai`.
- [x] 2.2 Add `decide.py` using `TypeSafeClient` from `typesafe_sdk`. It reads `TYPESAFE_API_KEY` from the environment, sends the quick start support-ticket sample in one `system_one` call, and asks for team (Choice: billing, technical, sales), frustration (Score: calm, frustrated but civil, very angry), and urgency (Noul). On success it prints the urgency probability, the chosen team with a probability for each team, and the frustration score with a probability for each level. If the key is unset or empty, it exits non-zero and prints none of those answers. It does not take the key as an argument and does not write a `.env` file. Verify the missing-key path with `env -u TYPESAFE_API_KEY python decide.py`; the exit status is non-zero and the output contains no team, score, or urgency answer.
- [x] 2.3 Confirm the key is not stored. Verify `decide.py` and `requirements.txt` contain no API key, and `git status` shows no `.env` file.

## 3. Live call

- [x] 3.1 With `TYPESAFE_API_KEY` set, run `python decide.py`. Verify it prints an urgency probability between 0 and 1, a team of billing, technical, or sales with three probabilities, and a frustration score with one probability per level. The request goes to `https://api.typesafe.ai/v1/systemone` (reference: https://docs.typesafe.ai/api). Do not treat the sample numbers on the quick start page as the expected output.
