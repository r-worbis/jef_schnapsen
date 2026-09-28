# Tasks

## 1. Pack, dealer, and deal

- [x] 1.1 Add a `schnapsen` package with the twenty-card pack (Herz, Karo, Pik, Kreuz; Ass, Zehner, König, Dame, Bube), eye values, and trick rank, and verify a test asserts each card once and the eye values 11, 10, 4, 3, and 2
- [x] 1.2 Implement the first-dealer draw and the swap of dealer and forehand after each deal, using an injected shuffle, and verify tests for a higher card dealing, an equal rank redrawing, and the roles swapping
- [x] 1.3 Implement the deal (three, three, face-up trump, two, two, nine face-down talon) and verify a test of the opening layout: five cards each, one face-up trump, nine face-down cards

## 2. Tricks and the talon

- [x] 2.1 Implement open-talon trick winning and "any card may be played", and verify tests that a discard loses and a trump captures a plain lead
- [x] 2.2 Implement the draw (winner first, face-up trump last) and the ban on drawing from a closed or empty talon, and verify those two tests
- [x] 2.3 Implement follow-suit and must-beat once the talon is exhausted or closed, and verify tests that a higher card of the led suit is required and that a trump is illegal when the led suit can be followed

## 3. Marriages, exchange, closing, and the match

- [x] 3.1 Implement marriages (40 for trump, 20 otherwise, lead König or Dame, no eyes with no trick, forehand may marry before the first lead) and verify those cases
- [x] 3.2 Implement the trump-Bube exchange, including when one face-down card remains, and verify the exchange succeeds then and is refused after the trump is drawn or the talon is closed
- [x] 3.3 Implement closing the talon (at least two face-down cards, leader only, no further draws, opponent eyes frozen at closing) and verify a legal close, a refusal on the last face-down card, and a one-point award when the opponent had 33 or more eyes at closing
- [x] 3.4 Implement declaration, a false declaration, closer failure (three points if the opponent was trickless at closing, otherwise two), and the last-trick win with the same 3/2/1 thresholds, and verify each of those outcomes
- [x] 3.5 Implement Bummerl countdown from seven, Schneider as two Bummerl, and a match ending at two Bummerl, with no carry into the next Bummerl, and verify those three cases
- [x] 3.6 Implement compound action ids for a lead, a follow, and a 66 declaration, and verify that applying an illegal id leaves cards and scores unchanged and that a legal id applies only the parts named in it

## 4. Human view and Jev state

- [x] 4.1 Add an original rules statement in the package covering trump, open and closed play, marriages, the exchange, closing, declaration, the last trick, and Bummerl, and verify a test that the statement contains those topics and does not contain a Wikipedia URL
- [x] 4.2 Implement the human view and verify a test of a fresh deal: five face-up own cards, computer count five, trump, talon count nine, seven points each, zero Bummerl, and no computer face or face-down talon identity in the payload
- [x] 4.3 Implement the Jev state from the same engine state and verify a test that it includes the computer hand, the rules statement, the public table, and the legal action ids, and omits the human hand and the face-down talon order

## 5. Jev player

- [x] 5.1 Implement the computer decision with `TypeSafeClient.system_one` and one `Choice` over the legal ids, and verify with a fake client that the recorded state contains the hand and the rules and that the chosen id is the only action applied
- [x] 5.2 Implement one retry, then the first sorted legal id as fallback, and the missing-key stop, and verify fake-client tests for an illegal first answer, a second illegal answer, a failed request, and a missing key that sends no request and applies no card

## 6. Local table

- [x] 6.1 Serve the human view and actions with the standard-library HTTP server on localhost, document `TYPESAFE_API_KEY` and the start command in the module docstring, and verify tests that GET does not call Jev, POST applies a human id, a refused id leaves the deal unchanged, and the docstring names the environment variable
- [x] 6.2 Add the page that shows the human cards, a face-down computer count, trump, talon, current trick, eyes, points still needed, Bummerl, and only the legal action ids, and verify by loading a dealt test state in the browser that those regions render and that a computer face is not in the page
- [x] 6.3 Show the computer's played card, marriage, exchange, close, and declaration, plus deal and match results, the missing-key message, and the replaced-choice message, and verify handler tests for each of those payloads and a browser check that a completed computer play shows the played card while the remaining computer cards stay face down

## 7. Match integration

- [x] 7.1 Drive a full match through the HTTP API with a fake Jev client until one seat has two Bummerl, and verify the response names the match winner and that `decide.py` is unchanged
