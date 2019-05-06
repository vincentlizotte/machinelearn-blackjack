import random
from strategy.strategy import Strategy


# Exploration strategy: from a blank slate, play randomly and figure out what are good and bad moves
class HitStandTrainStrategy(Strategy):
    def __init__(self, results_table):
        super().__init__(results_table)
        self.action_taken = None

    def run_game(self, game):
        result = game.run_managed_game(self.run_strategy_base)
        self.record_result(result)

    def run_strategy(self, player_score, dealer_score):
        if self.action_taken == 'HIT+STAND':
            action = 'STAND'
        else:
            action = random.choice(['HIT', 'STAND'])
            if action == 'HIT':
                self.action_taken = 'HIT+STAND'
            else:
                self.action_taken = action

        return action

    def record_result(self, result):
        self.results_table[self.player_score_history[0]][self.dealer_score][self.action_taken][result] += 1