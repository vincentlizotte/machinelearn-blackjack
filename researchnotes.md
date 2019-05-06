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

**The issues with the simple statistical approach**

The main difficulty with building such a Blackjack AI is that one of the actions, Hitting, doesn't lead to an immediate Win or Lose situation. Instead, it leads to a Survive or Lose situation. It is easy to build a statistical model for Standing: the action results in x% chance to win and 1-x% chance to lose. But Hitting is not a terminal action. One can never win from it, only survive or lose. Hitting must eventually be followed by a Stand action to have any hope of winning. 

As such, after the learning phase, if presented with a hand of 13 against a dealer holding a 9, the AI would look at its options table and see that Standing results in 30% win / 70% lose, while hitting results in 60% survive / 40% lose. These are apples and oranges. They cannot be compared to decide the right option. 

A possible solution to this would be to replace the Hit action during training with a "Hit then Stand" action, ensuring a terminal action and a Win / Lose outcome. While certainly better because we can now compare apples to apples, it implies that hitting multiple time is not a valid Blackjack strategy. This severely inders the win rate of small starting hands, because Hit+Stand is a in general a terrible choice for a hand of 3.

Another alternative would be to let the AI hit an arbitrary amount of times before standing, thus allowing for multi-hit strategies. The issue now becomes determining when to stop hitting. This assumes prior knowledge from attempting to stand at various hand values and observing the results. 

With all this in mind, it appears an iterative method is needed, one where each game round isn't completely independant from the previous ones, but uses knowledge gleaned previously in order to direct further learning.

**The straightforward Hit + Stand tactic**

Still, let us consider the Hit + Stand approach, if only to later compare it with more complex ones. This strategy is simple: we either Stand, or Hit + Stand. Both options will result in an immediate Win or Lose scenario. We can then build a table of [Player Score] x [Dealer Score] with each cell being the win rate of Hit and Hit + Stand, letting us pick the best option.

There are obvious issues with this approach: 
 - It fails miserable on low scores, where multiple Hits are needed to improve odds of winning. The AI will learn that hitting and standing on a 3 has the same odds of winning, which is true if a single hit is allowed, but not if multiple are.
 - It fails similarly on Soft hands, such as hitting on a soft 17 and turning it into a hard 12 then standing. The AI might wrongly learn that hitting on a soft hand is bad, because it led to a worse state, but that worse state could have been improved by hitting again, possibly making it even better than the initial soft state hand. Essentially, it gets caught in a local maxima. 

The first problem can be remedied by forcing a hit on a hand of 11 or lower, since hitting on those can never worsen our situation. But this should ideally be something the AI learns for itself.

From this strategy, 2 result sets will be built:
 - Random choice between Stand and Hit + Stand
 - Similar, but always hit for hands of 11 or lower
 
**Aiming for a draw: a valid strategy**

So far, we've only been interested in winning or losing. But there is a third possible outcome: a draw. We've ignored it and assumed that a draw was a wasted game, and we can just play another one instead. However, in some situations, a player can aim for a draw, because that is most reasonable outcome.

For instance, let's say that on 15, hitting results in 30% win, 50% loss and 20% draw. Ignoring the draws, this is a 37.5% win, 62.5% loss. Let's say standing on 15 also results in 37.5% win and 62.5% loss. 
Let's playing 1000 games at 1$. A win gives 2$, a draw returns the 1$ bid, and a loss gives 0$.
If we always hit on 15, it will result in 300 wins (600$), 500 losses (0$) and 20% draws (200$) for a total of 800$, a 20% loss on investment.
If we always stand on 15, it will result in 375 wins (750$) and 625 losses (0$) for a total of 750$, a 25% loss on investment.
As we can see, in a bad situation, aiming to draw can increase our returns, because it helps us "invalidate" that game. The inverse is true in a good situation.

Our previous Hit + Stand tactics was throwing away this possibility, whereas we can make it work for us, aiming to draw in bad situations and avoiding it in good situations.

We shall then run a similar Hit + Stand tactic as described in the previous section, but will now also track draws. Instead of a percent chance to Win or Lose, the results table will now hold a numerical score. A win shall give +1 point, a loss -1 point, and a draw 0 point. When we have to take a decision, we will simply take the action with the greater score, which in many situation will have us choose the least negative of two negatives, picking the lesser of two evils.

**A multi-step, state machine-based approach**

Let us then try a more general solution that handles hitting multiple times.

The core issue is to determine the chance of winning if we Hit. As discussed previously, this is not as simple as the Stand action, since we only learn whether we survive, not win. How can we convert "Hitting on 13 has a 60% chance to survive and 40% chance to lose" into "Hitting on 13 has a 35% chance to win and 65% chance to lose"? By realizing that Hitting transports us to another state, which has its own "Win / Lose on a Stand" and "Survive / Lose on a Hit" ratios. And each of those state transitions has a certain probability of happening. Thus, the odds of winning or losing on a Hit becomes the weighted chance of winning / losing on the various states we can reach by hitting, weighted by how likely we are to reach that state.

However, for every state but the final one, a score of 21, only a survive / lose ratio can be computed at first, because the win / lose ratio depends on other states. Thus, we have to work backward. The state diagram of a blackjack game being acyclic, we can represent it as a tree, and work up from the leaves.

As an example, the process to determine the odds of winning if we hit on 18 would be (percentages are approximative to simplify illustration):
 - From 19, we can Hit and reach 20 (10%), 21 (10%), or lose (80%). We can also Stand (85% win, 15% lose)
 - From 20, we can Hit and reach 21 (10%), or lose (90%). We can also Stand (90% win, 10% lose)
 - From 21, hitting makes no sense, so we can only Stand (100% win)
 
Win rate from Hitting at 20 is 10% of the win rate at 21, thus 10%. Therefore, Standing is a much better choice, with 90% win.
Win rate from Hitting at 19 is 10% of the win rate at 20 + 10% of the win rate at 21, so 9% + 10% = 19%. Standing is still a better choice, with 85% win.

As we build this table towards lower numbers, the odds propagate, and we learn that hitting on low numbers is better than standing since it leads to states with higher win probability.

Let's then split the learning phase into 3 distinct problems:

The first phase will be simply standing on every starting hand. Since every score can be reached with a starting hand, this will allow us to build a complete table of [Player Score] x [Dealer Score], with each cell being the win rate of the Stand strategy. In this case, there is no distinction between a soft or hard score, since they behave the same.

The second phase will let always hitting. The goal here isn't to win: it's to study the state transitions. We will end up building a lower triangular matrix of [State] x [State], indicating the odds of moving from one state to the other. In this case, there must be a distinction between soft and hard hands. To simplify representation, a hand will be considered soft if it can accomodate an ace treated as 11, regardless of it it currently has one or not.

The third phase will not involve simulating games, but simply propagating the odds of winning on a hit based on the odds of reaching a state and the odds of winning at that state.

