import csv
import random
import time

import io

from blackjack import Game

if __name__ == '__main__':
    # The fun thing about this simplified blackjack is that it doesn't matter how you got to a score of X. 2 cards, 7 cards. It won't affect the decision of "should I hit or stay"
    # So no need to track state. Current score is sufficient.
    results = [[{'hit': {'win': 0, 'lose': 0, 'draw': 0}, 'hold': {'win': 0, 'lose': 0, 'draw': 0}} for i in range(12)] for j in range(22)]
    games_played = 0
    time_start = time.time()
    game = Game(1)
    while (time.time() - time_start) < 2:
        game_round = game.start_round()
        initial_player_score = game_round.player_sum
        initial_dealer_score = game_round.dealer_sum
        action = 'nothing'
        #print(f'Round start: {initial_player_score}. Dealer: {initial_dealer_score}')
        while game_round.is_player_alive():
            initial_player_score = game_round.player_sum
            initial_dealer_score = game_round.dealer_sum
            action = random.choice(['hit', 'hold'])
            #print(f'Player is {action} on Player: {initial_player_score}. Dealer: {initial_dealer_score}')

            if action == 'hit':
                game_round.draw_for_player()
                if game_round.is_player_alive():
                    results[initial_player_score][initial_dealer_score][action]['win'] += 1
            else:
                break

        # Dealer had blackjack. Instant loss, no decision. Skip that game.
        if action == 'nothing':
            continue

        # We only ever get here on a 'hold' action
        result = game_round.resolve_round()
        if result == 'WIN':
            results[initial_player_score][initial_dealer_score][action]['win'] += 1
        elif result == 'LOSE':
            results[initial_player_score][initial_dealer_score][action]['lose'] += 1
        elif result == 'DRAW':
            results[initial_player_score][initial_dealer_score][action]['draw'] += 1

        games_played += 1

    with io.StringIO() as stringstream:
        csv_writer = csv.writer(stringstream, delimiter=',')
        csv_writer.writerow(['player', 'dealer', 'action', 'win', 'lose', 'draw', 'winrate'])

        # Skip some impossible scores: players cant have under 4, dealers cant have under 2
        for player_score in range(4, 22):
            for dealer_score in range(2, 12):
                score_object = results[player_score][dealer_score]
                for action in ['hit', 'hold']:
                    total_games = score_object[action]['win'] + score_object[action]['lose']  # + score_object[action]['draw']
                    winrate = score_object[action]['win'] / total_games if total_games is not 0 else 0
                    csv_writer.writerow([player_score, dealer_score, action, score_object[action]['win'], score_object[action]['lose'], score_object[action]['draw'], winrate])

        with open("data/test.csv", "w", newline='') as file:
            file.write(stringstream.getvalue())

        print(results)
        print(games_played)
