# Tasks

## 1. Exhausted and closed follows

- [x] 1.1 In `tests/test_game.py`, add cases beside `test_must_beat_the_led_suit_and_suit_before_trump` for the scenarios in the modified follow requirement: exhausted and void with a trump (only those trumps are legal); exhausted and void with no trump (every card in hand is legal); exhausted trump lead holding a higher and a lower trump (only the higher trumps); closed trump lead holding a lower trump and another suit (only the lower trumps); a forbidden follow by the computer and by the human, each refused by `apply_action` with `current_trick`, `to_play`, and `snapshot` unchanged; an open talon whose face-up trump is still undrawn, where an off-suit card is legal even though the follower holds the led suit. Keep the two cases that test already locks. In `schnapsen/engine.py`, keep `_legal_follow` as the only follow order, called from `is_legal` and from `_candidates` with `not stock_open(deal)`, and keep `apply_action` returning false before `_execute` when that check fails. Change `_legal_follow` only where a new case fails. Verify with `python -m unittest tests.test_game`.

- [x] 1.2 Leave `schnapsen/view.py` and `schnapsen/player.py` on `legal_action_ids`, with no second follow filter in the page or in the Jev request. Verify with `python -m unittest tests.test_table`.
