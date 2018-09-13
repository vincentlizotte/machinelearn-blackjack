A player's score in Blackjack can be represented as an acyclic finite state machine. While at first it might appear possible to go back to a previous score, such as having a hand with an Ace and 7 (score of 18) and drawing a 6 (score of 14 with the Ace now counted as 1), this becomes a different state when considering that we've moved from a soft hand (ace treated as 11) to a hard hand (ace treated as 1). Considering that a hand with 2 hard aces is not survivable (score of 22), going from soft to hard can only happen once, and once done one cannot go back. There is definitely some innapropriate joke that can be worked here.
Any hand without an ace is considered neutral. It is possible to go from a neutral to a soft hand by drawing an ace, turning a score of n into n+11. If that would overflow 21, the hand is now a hard n+1.
A hard-3 is the same as a soft-13, but by convention, the hand is considered to be the soft variant until it cannot be anymore.

The minimum score a player can hold is 4: a pair of 2s. A pair of aces becomes a soft-12, and an ace with a 2 is a soft-13.
Building upon that, the lowest soft score one can have is a 12.
Above 10, there is no distinction between a neutral and hard hand: any ace drawn will have to be treated as a 1.

The state machine thus becomes something along the lines of:
[12-20]-soft -> [13-21]-soft (draw anything without going past 21)
[12-21]-soft -> [12-21]-hard (draw anything and go past 21, looping back to 11 by going hard on an ace)
[11-20]-neutral -> [12-21]-hard (draw an ace, but forced to treat it as 1)
[4-10]-neutral -> [15-21]-soft (draw an ace, turning a neutral hand soft)
[4-20]-neutral -> [6-21]-neutral (draw anything that fits under 21)
[4-20]-hard -> [5-21]-hard (draw anything that fits under 21)
[12-21]-neutral -> death (draw past 21)
[12-21]-hard -> death (draw past 21)

It is impossible to die on a soft hand
There is no winning final state in Blackjack. There is a clear lose state, but in every situation where a player hasn't lost, they always have the possibility to hit further.
Anyone who's played more than 8 minutes of Blackjack will realize some of those transitions are silly, such as going from a soft-21 to a hard-16. But that's the computer's job to figure out.

