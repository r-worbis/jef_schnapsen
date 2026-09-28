# Design

## Context

See proposal.md for why. The repository is a Python 3.14 project with `decide.py`, `requirements.txt` (`typesafe-sdk`), and the `jev-decisions` sample. Jev is reached only through `TypeSafeClient.system_one`, which accepts a state document and typed questions (`Choice`, `Score`, `Noul`) and defaults to `jev-latest`. The client reads `TYPESAFE_API_KEY`. There is no web stack, no game code, and no local model.

## Goals / Non-Goals

**Goals:**

- A rules engine that can be driven and tested with no network and no API key.
- A human view that is a filtered projection of that engine, not a second copy of the rules.
- One Jev `Choice` per computer decision, limited to actions the engine already marked legal.

**Non-Goals:**

- Saving a match across process restarts, accounts, or more than one table at a time.
- Card-image assets, a frontend build, or a new web framework.
- Changing `decide.py` or calling any host other than `api.typesafe.ai`.
- Live Jev calls inside the automated tests.

## Decisions

### Engine, view, and player stay separate

Add a `schnapsen` package with three layers:

- The engine owns the pack, the deal, legal actions, and scoring. Callers pass an action in and get a new state or a refusal. Tests inject the shuffle and the dealer draw so deals are repeatable.
- A view function builds the human payload and the Jev state from the same engine state. It drops the computer seat's current faces, the face-down talon order, and either seat's tricks after the first trick when that payload is for the other seat.
- The Jev player asks for a choice only when the engine says it is the computer's decision. The HTTP handler never embeds rule checks of its own.

`decide.py` stays at the repository root.

Alternatives:

- One script that mixes dealing, prompting, and `print` cannot offer the human a card table, and it cannot test scoring without a key.
- Letting Jev answer in free text and parsing a card name makes illegal plays a normal case. `Choice` already restricts the answer to named alternatives, which is how `decide.py` asks questions.

### One compound action per decision

A computer decision is one complete step, chosen from ids the engine generates:

- On lead: optional trump exchange, optional close, then either a legal lead or a marriage plus one of its two cards. If a marriage would end the deal by declaration, "marry and declare" is its own id and does not also lead.
- On follow: optional trump exchange, then one legal reply.
- After the computer's own trick or marriage has produced at least 66 counting eyes: declare, or continue.

The `Choice` criteria are those ids. Their descriptions say what the action does in card names. Applying the chosen id applies every part of it and nothing else. The fallback, used only after a bad or failed call, is the first id in sorted order. That sort is fixed so the fallback is predetermined.

The human page offers the same ids as buttons or as cards. A click sends the id. A refused id leaves the state as it was.

Alternatives:

- A separate Jev call for exchange, then close, then the card, multiplies cost and latency and can stop halfway through a turn.
- Encoding every rule as a Noul ("should I trump?") and then picking a card in code hides the actual play from Jev. The request is supposed to ask how to play.

### Rules text is original

The state document includes a short rules statement written for this game, covering trump, open versus closed play, marriages, the exchange, closing, declaration, the last trick, and Bummerl scoring. It is not a copy of the Wikipedia article. The statement is stored in the package so the engine and the prompt cannot drift onto two different rule texts. Card names in the prompt match the engine: `Herz Ass`, `Karo Zehner`, and so on.

The state also includes the computer's hand and the public table from the view: visible trump, talon count, closed flag, current trick, the computer's tricks, the human's first trick, both eye totals, points still needed, Bummerl, and whose turn it is. Eye totals are included because the human page shows them. Hidden faces are not.

### Local page on the standard library

Serve one page and a JSON API with the Python standard-library HTTP server, bound to localhost. No new install beyond `typesafe-sdk`.

- `GET` of the table returns the human view and does not call Jev.
- `POST` of an action applies a human id, then, if it is the computer's decision, calls Jev before responding.
- If the computer must act as soon as a deal is dealt, the page sends an empty "computer to move" request; loading the page does not itself call Jev.
- The page shows own cards face up, the computer's count face down, the trump, the talon count, the trick, eyes, points still needed, and Bummerl. Suits are drawn with text and CSS, not image files.
- A missing or blank `TYPESAFE_API_KEY` is checked before any request. The response tells the page to show that the key is missing, and no card is played. A failed or illegal Jev answer is retried once; the second failure applies the fallback and the page says the choice was replaced.

Alternatives:

- FastAPI or Flask is a new dependency for a single local page.
- A terminal UI cannot show the hand and the score the way the table spec requires.

### Tests stay offline

Engine tests cover dealing, open and closed tricks, marriages with and without a trick, the trump exchange, closing and its frozen eyes, declaration, a false declaration, the last trick, Schneider, and the match ending at two Bummerl. View tests assert the human JSON and the Jev state omit hidden faces. Player tests use a fake client that records the state and returns a chosen id, an unknown id, or an error. They do not open a network connection.

## Risks / Trade-offs

- [Jev chooses a legal but weak line, or the call is slow] → The engine still rejects illegal play. The page waits on the action request and shows a pending state. Fallback keeps a failed call from stalling the deal.
- [A rules bug ships because the prompt and the engine disagree] → One rules statement, and tests drive the engine with fixed decks rather than the prompt.
- [Showing both eye totals reveals more than a physical weiches table] → The specs require those totals on the human page. Jev receives the same totals and still does not receive hidden faces.
- [Each computer card spends account credit] → One `system_one` call per decision, not per candidate card. Automated tests use a fake client.
- [In-memory state vanishes on restart] → Acceptable for a local match. Rollback is deleting the `schnapsen` package, its page, and its tests. `decide.py` is untouched.

## Migration Plan

Nothing to migrate. Start the local server with `TYPESAFE_API_KEY` set in the environment. Stopping the process discards the match.

## Open Questions

None. Suit symbols and the exact wording of the rules statement can be settled while implementing; they do not change the action model or the specs.
