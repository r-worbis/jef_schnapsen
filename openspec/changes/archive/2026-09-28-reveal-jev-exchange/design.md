# Design

## Context

See proposal.md for why the last Jev exchange should be visible. Today `jev_state` in `schnapsen/view.py` builds one string: the `RULES` text, a blank line, then the computer hand, the public table, and the legal actions. `_ask` in `schnapsen/player.py` sends that string as `state` and reads only `response.choices["play"].choice`. `Match` keeps `notice` and `choice_replaced`, and `human_view` does not include the request or the answer. `schnapsen/page.html` renders whatever `human_view` returns. The opening-view test serializes that whole payload and rejects any computer-hand face in it.

## Goals / Non-Goals

**Goals:**

- Keep the exact text that was sent, split into the rules statement and the remainder, plus each returned choice, on the match.
- Show that split in three boxes behind one German toggle. The data is in the human view so a reload still has it.
- Leave the sent string, the applied action, and the fallback path as they are.

**Non-Goals:**

- Changing `decide.py`, showing probabilities, or adding a new HTTP route.
- Remembering whether the toggle was open across a reload.

## Decisions

### Keep one exchange on the match

Add a small record on `Match`: the rules string, the remainder string, the choice strings in order, and whether a request failed. `None` means no request has been sent yet. `_decide` writes it when it is about to ask, appends each returned choice, and sets the failure flag when `system_one` raises or the choice cannot be read. A missing-key return happens before that write, so the previous record stays. `start_deal` does not clear it. The next request replaces the whole record.

Alternative: a log of every turn. The table only needs the last exchange, so one record is enough.

### Split the existing state string, do not rewrite it

Build the rules and the remainder from the same lines `jev_state` already joins, and send `rules + "\n\n" + remainder`, which is the current string. The rules box shows `RULES`. The cards box shows the remainder, starting at `Your cards:`. Store those two strings at send time so a later play does not rewrite the hand that was asked about.

Alternative: show a live `jev_state` when the button is clicked. That would not be the text that was sent.

### Put the record on the existing human view

`human_view` adds one object, empty when no request has been sent. The page reads only that object for the three boxes. Computer-hand faces and later won tricks may appear inside the remainder string and nowhere else. The API key is not copied onto the match or into the view. No new route: `GET /api/state` and the action responses already return `human_view`.

### Toggle in the page, German copy

One button in the aside, labeled `Jev anzeigen` while the boxes are hidden and `Jev ausblenden` while they are shown. Headings: `Spielregeln`, `Karten und Optionen`, `Ergebnis`. Empty text: `Noch keine Anfrage.` Failure text: `Die Anfrage ist fehlgeschlagen.` Returned choice ids are shown in order, and the failure sentence is added when the flag is set. The existing replaced-choice banner stays. The open or closed state is page state only; a reload starts closed and still contains the texts.

## Risks / Trade-offs

- [The cards box shows the computer hand and later tricks] → The boxes stay closed until the button is used, and every other field still omits those faces. The opening-view payload test stays valid because an empty exchange contains no card names.
- [A failed call has no choice string] → The result box says the request failed and does not invent an id. A choice that was returned before a later failure is still listed.

## Migration Plan

The exchange lives on the in-memory match. Restarting the server drops it, as it drops the deal. No stored data to migrate.
