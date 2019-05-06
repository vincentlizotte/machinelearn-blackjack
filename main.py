import csv
import random
import time
import io

import pandas as pd

from blackjack import Game
from strategy import HitStandTrainStrategy, HitStandTestStrategy

if __name__ == '__main__':
    algorithm = "OriginalPrototypeRandomExploration"
    test_train_iterations_to_run = 10
    seconds_to_run = 2
    original_prototype_seconds_to_run = time.time()

    game = Game(1, reset_on_dealer_blackjack=True)

    # Train by playing X games randomly, then use that knowledge to play another X games intelligently
    if algorithm == "TrainAndTest":
        # Generating a
        training_results = [[{'STAND': {'WIN': 0, 'LOSE': 0, 'DRAW': 0}, 'HIT+STAND': {'WIN': 0, 'LOSE': 0, 'DRAW': 0}} for i in range(12)] for j in range(22)]
        for i in range(test_train_iterations_to_run):
            strategy = HitStandTrainStrategy(training_results)
            strategy.run_game(game)

        for x in training_results:
            for y in x:
                for action, result in y.items():
                    total_games = result['WIN'] + result['LOSE']
                    result['WIN_RATE'] = result['WIN'] / total_games if total_games is not 0 else 0

        best_move = [['STAND' if j['STAND']['WIN_RATE'] > j['HIT+STAND']['WIN_RATE'] else 'HIT' for j in i] for i in training_results]
        best_move_df = pd.DataFrame(data=best_move, columns=range(12))
        best_move_possible = best_move_df.iloc[4:22, 2:12]
        best_move_possible.to_csv("data/hitstand_bestmove.csv", sep=';')

        test_results = [[{'WIN': 0, 'LOSE': 0, 'DRAW': 0} for i in range(12)] for j in range(22)]
        for i in range(test_train_iterations_to_run):
            strategy = HitStandTestStrategy(training_results, test_results)
            strategy.run_game(game)

        overall_games = 0
        overall_wins = 0
        for x in test_results:
            for result in x:
                total_games = result['WIN'] + result['LOSE']
                result['WIN_RATE'] = result['WIN'] / total_games if total_games is not 0 else 0
                overall_games += total_games
                overall_wins += result['WIN']

        print(f"games: {overall_games}. wins: {overall_wins}. Win rate: {overall_wins / overall_games}")

        winrates = [[j['WIN_RATE'] for j in i] for i in test_results]
        winrate_df = pd.DataFrame(data=winrates, columns=range(12))
        winrate_possible = winrate_df.iloc[4:22, 2:12]
        winrate_possible.to_csv("data/hitstand_winrate.csv", sep=';')

    # Original first prototype, preserved for posterity
    elif algorithm == 'OriginalPrototypeRandomExploration':
        # The fun thing about this simplified blackjack is that it doesn't matter how you got to a score of X. 2 cards, 7 cards. It won't affect the decision of "should I hit or stay"
        # So no need to track state. Current score is sufficient.
        results = [[{'hit': {'win': 0, 'lose': 0, 'draw': 0}, 'hold': {'win': 0, 'lose': 0, 'draw': 0}} for i in range(12)] for j in range(22)]
        games_played = 0

        while (time.time() - original_prototype_seconds_to_run) < seconds_to_run:
            game_round = game.start_round()
            initial_player_score = game_round.player_sum
            initial_dealer_score = game_round.dealer_sum
            action = 'nothing'
            print(f'Round start: {initial_player_score}. Dealer: {initial_dealer_score}')
            while game_round.is_player_alive():
                initial_player_score = game_round.player_sum
                initial_dealer_score = game_round.dealer_sum
                action = random.choice(['hit', 'hold'])
                print(f" - Player: {action.upper()} on {initial_player_score} vs Dealer's {initial_dealer_score}")

                if action == 'hit':
                    game_round.draw_for_player()
                    if game_round.is_player_alive():
                        results[initial_player_score][initial_dealer_score][action]['win'] += 1
                else:
                    break

            # Dealer had blackjack. Instant loss, no decision, no learning. Skip that game.
            if action == 'nothing':
                continue

            result = game_round.resolve_round()
            if result == 'WIN':
                results[initial_player_score][initial_dealer_score][action]['win'] += 1
            elif result == 'LOSE':
                results[initial_player_score][initial_dealer_score][action]['lose'] += 1
            elif result == 'DRAW':
                results[initial_player_score][initial_dealer_score][action]['draw'] += 1

            games_played += 1

        with io.StringIO() as stringstream:
            csv_writer = csv.writer(stringstream, delimiter=';')
            csv_writer.writerow(['player', 'dealer', 'action', 'win', 'lose', 'draw', 'winrate'])

            # Skip some impossible scores: players cant have under 4, dealers cant have under 2
            for player_score in range(4, 22):
                for dealer_score in range(2, 12):
                    score_object = results[player_score][dealer_score]
                    for action in score_object.keys():
                        total_games = score_object[action]['win'] + score_object[action]['lose']  # + score_object[action]['draw']
                        winrate = score_object[action]['win'] / total_games if total_games is not 0 else 0
                        csv_writer.writerow([player_score, dealer_score, action, score_object[action]['win'], score_object[action]['lose'], score_object[action]['draw'], winrate])

            with open("data/test.csv", "w", newline='') as file:
                file.write(stringstream.getvalue())

            #print(results)
            print(games_played)
