# Design

## Context

See proposal.md for why. `schnapsen/engine.py` already accepts a play only in `apply_action`, which returns false before `_execute` when `is_legal` is false. `is_legal` and `_candidates` both call `_legal_follow` with `not stock_open(deal)`. That function is the Farbzwang-then-Stichzwang order once the talon is closed or nothing remains to draw. The open change `enforce-farbzwang-stichzwang` owns the remaining cases of that order. This change does not add a second copy.

The seats are the strings `human` (right) and `computer` (left) on `Match`, `Deal`, the view, and the page. `schnapsen/player.py` is only Jev: `perform_computer_turn` asks when `to_play == "computer"`. `POST /api/action` applies the posted id and then, if that seat is to play, asks Jev once. The page calls `POST /api/computer` while `toPlay === "computer"`. `_play_card` enters the acknowledge phase when the answering seat is `computer`.

## Goals / Non-Goals

**Goals:**

- One driver that asks whichever non-person player is bound to the seat to play, then applies the proposal only through `apply_action`.
- A stub player that proposes one plain play of a card from its own hand.
- The acknowledge pause depends on the person sitting on the right, not on the seat id `computer`.

**Non-Goals:**

- A live LLM call, a new model client, or a prompt for the stub.
- Renaming the seat ids, or seating the person on the left.
- A second follow check in the page, the stub, or the Jev request.
- Changing marriage, exchange, closing, drawing, or the eye awards.
- Editing `_legal_follow` except where a test from `enforce-farbzwang-stichzwang` already requires it. Do not weaken that order.

## Decisions

### Keep the seat ids and store a player kind beside them

`Match` gains `players: dict[Seat, str]`, default `{"human": "human", "computer": "jev"}`. The allowed values are `human`, `jev`, and `stub`. `new_match` and `match_with_deal` use that default so existing tests keep a person against Jev. The engine reads `players` only to decide the acknowledge pause. Legality does not read it.

Alternative: rename the seats to `left` and `right`. Rejected. Scores, tricks, action tests, and the page all use `human` and `computer`. The kinds are a binding, not a new place at the table.

### Three flat modules replace the single computer player

- `schnapsen/jev_player.py` holds the current Jev request from `schnapsen/player.py`: build the request for `deal.to_play`, call `system_one`, and return the choice or a failure. It does not call `apply_action`.
- `schnapsen/stub_player.py` holds the stub. Its constructor takes a callable `choose(hand) -> Card`. The default callable draws uniformly with `random.Random().choice`. Tests pass a queue. The proposal is `play:` plus that card's token. No marriage, exchange, or close, and no read of `jef.api`.
- `schnapsen/turn.py` holds `take_ai_turn(match, client)`. If `to_play` is not bound to `jev` or `stub`, or the phase is not `play`, it returns. For Jev with a missing key it sets `notice` to `missing-key` and returns without a request, as today. Otherwise it asks the bound player. A Jev request failure applies the predetermined legal action immediately, matching the current Jev requirement. An illegal proposal, including a stub card `apply_action` refuses, leaves the deal unchanged and asks that player once more. A second illegal proposal, or a second failure, applies the predetermined legal action and sets `choice_replaced`. A first legal proposal applies that proposal and clears `choice_replaced`. The predetermined action stays `sorted(legal_action_ids(match))[0]`.

`schnapsen/player.py` is removed after `server.py` and the tests import `take_ai_turn` and the Jev ask from the new modules. `view.jev_parts` takes the seat it is asking, which is `deal.to_play`, instead of the hardcoded left seat.

Alternative: leave Jev in `player.py` and add the stub beside it. Rejected. The file is the computer turn, the key check, and the fallback in one path. Splitting the ask from the driver is what lets a stub and a second Jev share the engine gate.

### The pause follows the person, not the left seat

In `_play_card`, after the second card, enter `acknowledge` and set `to_play` to `human` only when `players["human"] == "human"` and the leader of that trick is `human`. Every other answering card calls `_resolve_trick` immediately. `seen` stays legal only in that waiting phase. A match whose right seat is `jev` or `stub` never offers `seen`.

### The page chooses the pair and advances one AI turn per request

`POST /api/match` with JSON `{"human": "...", "computer": "..."}` replaces `table.match` with `new_match()` and then sets `players`. `computer: "human"` returns 400 and does not replace the match. Any other unknown kind does the same. The default server match is unchanged.

`POST /api/action` still applies the posted id and then, when the seat now to play is an AI and the phase is `play`, calls `take_ai_turn` once. That preserves the person's lead and the opponent's answer in one response. `POST /api/computer` calls `take_ai_turn` once for whichever AI is to play, and does nothing during `acknowledge` or on the person's turn.

The page adds two selects on the title row. The right select is Mensch, Jev, Zufall (`human`, `jev`, `stub`). The left select is Jev and Zufall. Changing either select sends `POST /api/match` and reloads. While the person is on the right, headings and the turn line stay Du and Der Computer. Otherwise the turn line, dealer line, seat headings, score names, and deal or match banners use Mensch, Jev, and Zufall for the two kinds.

`human_view` includes `players`. When the right kind is not `human`, `yourHand` is empty and `yourCount` is that hand's length; the page draws that many backs in the right-hand row, the same way it draws `opponentCount` on the left. `yourTurn` is true only when the person is the right seat and it is that seat's turn. Card faces of a non-person seat stay out of every field except the Jev cards box.

The page requests `POST /api/computer` when `players[toPlay]` is `jev` or `stub`, the deal is not over, `missingKey` is false or the player is `stub`, and the phase is not the seen wait. After each response it repeats while that condition holds. It does not loop on `missingKey` for Jev.

### Tests inject the stub's selector and keep the engine gate

A game test seats two stubs, feeds selectors, and asserts a lead and an answer award the trick with no `seen` id. A second test exhausts the talon, makes the selector propose an off-suit card while the led suit is held, and asserts the first `take_ai_turn` step does not apply it. The retry and the predetermined fallback are asserted with two illegal selections. Existing `apply_action` refusal tests stay. Table tests cover `POST /api/match`, a hidden right-hand AI, and that a stub turn sends no client call when the key file is absent.

## Risks / Trade-offs

- [The page loops because an AI turn does not change `toPlay`] → Jev with a missing key returns before a play and sets `missingKey`, and the page stops. A stub or a failed Jev request applies a legal id when one exists, so `toPlay` moves. If `legal_action_ids` is empty, `take_ai_turn` returns without calling the player.
- [`yourHand` would reveal a right-seat AI] → The view sends an empty `yourHand` and a count. A table test rejects any face of that hand outside the Jev cards text.
- [Person-versus-Jev acknowledgement regresses] → The new condition is true for the default binding, and the existing seen tests stay on that binding.
- [`_legal_follow` and a new player check disagree] → Players return an id. Only `apply_action` mutates the deal. The stub does not call `_legal_follow`.
- [Jev versus Jev spends two requests per trick] → That is the existing one-request-per-decision cost, once per seat. The stub never calls out.

## Migration Plan

No saved match and no action-id change. Rollback is reverting the new modules, the `players` field, and the page selects. A match already running in the dev server is replaced on the next process start.
