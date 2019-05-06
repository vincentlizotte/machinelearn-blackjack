from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(self, results_table):
        self.results_table = results_table
        self.player_score_history = []
        self.dealer_score = None

    def run_strategy_base(self, player_score, dealer_score):
        self.player_score_history.append(player_score)
        self.dealer_score = dealer_score
        return self.run_strategy(player_score, dealer_score)

    @abstractmethod
    def run_strategy(self, player_score, dealer_score):
        raise NotImplementedError()