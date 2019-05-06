from strategy.strategy import Strategy


# Exploitation strategy: from previous training data, try and perform as best as possible
class HitStandTestStrategy(Strategy):
    def __init__(self, training_data, results_table):
        super().__init__(results_table)
        self.training_data = training_data

    def run_game(self, game):
        result = game.run_managed_game(self.run_strategy_base)
        self.record_result(result)

    def run_strategy(self, player_score, dealer_score):
        training_actions = self.training_data[player_score][dealer_score]
        actions_by_score = sorted(training_actions.items(), key=lambda x: x[1]['WIN_RATE'], reverse=True)
        best_action = actions_by_score[0][0]
        if best_action == 'HIT+STAND':
            best_action = 'HIT'
        return best_action

    def record_result(self, result):
        self.results_table[self.player_score_history[0]][self.dealer_score][result] += 1
