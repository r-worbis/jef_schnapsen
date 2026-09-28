"""Original rules statement sent to Jev with the computer seat's cards."""

RULES = """
Weiches Schnapsen is played by two seats with a 20-card pack. The trump is the suit of the face-up card under the talon. Card eyes are Ass 11, Zehner 10, König 4, Dame 3, and Bube 2. Within a suit, Ass beats Zehner, then König, then Dame, then Bube. A trump beats any card of another suit.

While the talon is open and cards remain to draw, the follower may play any card. The follower wins by playing a higher card of the led suit, or by playing a trump against a lead from another suit. After the trick, the winner draws first and the opponent draws next. The face-up trump is the last card drawn.

Once the talon is exhausted, or after closing, the follower must play a higher card of the led suit, otherwise a lower card of that suit, otherwise a trump, otherwise any card. Following suit comes before trumping.

A marriage is König and Dame of one suit, declared on lead. A trump marriage is worth 40 eyes and any other marriage is worth 20. The seat then leads the König or the Dame, unless the deal ends first. Marriage eyes count only if that seat wins a trick in the deal.

A seat holding the trump Bube may exchange it for the face-up trump before playing a card, including when one face-down card remains on the trump. The exchange is unavailable after the trump is drawn or the talon is closed.

The leader may close the talon when at least two face-down cards remain. Closing ends further draws. A closer who later reaches 66 scores from the opponent's eyes at the moment of closing. If the closer never reaches 66, the opponent wins: three game points if that opponent was trickless at closing, otherwise two.

The deal ends as soon as a seat has at least 66 counting eyes after winning a trick or a marriage that counts. There is no declaration to choose, and play does not continue past 66. That seat scores three game points if the opponent has no trick, two if the opponent has 32 or fewer eyes, and one if the opponent has 33 or more. If nobody has reached 66 before the last card is led and the talon was not closed, the last trick wins the deal and scores by those same thresholds.

Game points are counted down from seven. Reaching zero wins the Bummerl. If the other seat still needs seven, the loss is Schneider and counts as two Bummerl. Otherwise it counts as one. The match ends when a seat has two Bummerl.
""".strip()
