import random


class Game:
    def __init__(self, decks_count, reset_on_dealer_blackjack):
        self.deck = Deck(decks_count)
        self.reset_on_dealer_blackjack = reset_on_dealer_blackjack

    def start_round(self):
        self.deck.reset()
        game_round = Round(self.deck)
        return game_round

    def run_managed_game(self, round_callback):
        game_round = self.start_round()

        if self.reset_on_dealer_blackjack:
            while game_round.dealer_has_blackjack():
                game_round = self.start_round()

        while game_round.is_player_alive():
            action = round_callback(game_round.player_sum, game_round.dealer_sum)
            if action == 'HIT':
                game_round.draw_for_player()
            elif action == 'STAND':
                return game_round.resolve_round()
            else:
                raise ValueError(f"Invalid player action: {action}")
        return 'LOSE'


class Deck:
    def __init__(self, decks_count=1):
        self.deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4 * decks_count  # 4 suits. All 10-valued cards are identical in behavior
        self.drawn_cards_indices = set()
        self.reset()

    def reset(self):
        self.drawn_cards_indices = set()

    # Draw a card by picking a random one until we pick one we've not chosen before.
    # Since we pick such a low fraction of the deck each game, this is much faster than shuffling or removing from the deck
    # There's a time and place for functional programming; this isn't it.
    def draw(self):
        if len(self.drawn_cards_indices) >= len(self.deck):
            raise RuntimeError("Tried to pick a card from an empty deck")

        while True:
            drawn_card_index = random.randrange(len(self.deck))
            if drawn_card_index not in self.drawn_cards_indices:
                self.drawn_cards_indices.add(drawn_card_index)
                return self.deck[drawn_card_index]


class Round:
    def __init__(self, deck):
        self.deck = deck
        self.dealer_cards_visible = [self.deck.draw()]
        self.dealer_cards_hidden = [self.deck.draw()]
        self.player_cards = [self.deck.draw(), self.deck.draw()]

    def sum_cards(self, cards):
        current_sum = sum([c for c in cards if c != 1])
        aces = [11 for c in cards if c == 1]

        # Treat aces as 11. If the score busts 21, downgrade aces from 11 to 1 one at a time
        while current_sum + sum(aces) > 21 and 11 in aces:
            aces[aces.index(11)] = 1
        return current_sum + sum(aces)

    @property
    def dealer_sum(self):
        return self.sum_cards(self.dealer_cards_visible)

    @property
    def player_sum(self):
        return self.sum_cards(self.player_cards)

    def dealer_has_blackjack(self):
        # Dealer blackjack requires a visible 10 and hidden Ace, or vice-versa
        if len(self.dealer_cards_hidden) == 1 and len(self.dealer_cards_visible) == 1 and (
                    (self.dealer_cards_visible[0] == 1 and self.dealer_cards_hidden[0] == 10) or
                    (self.dealer_cards_visible[0] == 10 and self.dealer_cards_hidden[0] == 1)):
            return True
        else:
            return False

    def is_player_alive(self):
        return self.player_sum <= 21 and self.dealer_has_blackjack() is False

    def draw_for_player(self):
        self.player_cards.append(self.deck.draw())

    def start_round(self):
        self.dealer_cards_visible.append(self.deck.draw())
        self.dealer_cards_hidden.append(self.deck.draw())
        self.player_cards.extend([self.deck.draw(), self.deck.draw()])

    def resolve_round(self):
        self.dealer_cards_visible.extend(self.dealer_cards_hidden)
        self.dealer_cards_hidden = []

        # Dealer had first turn blackjack. Instant loss.
        if self.dealer_sum == 21:
            return 'LOSE'

        if self.player_sum > 21:
            return 'LOSE'

        while self.dealer_sum < 17:
            self.dealer_cards_visible.append(self.deck.draw())

        if self.dealer_sum > 21:
            return 'WIN'
        if self.dealer_sum == self.player_sum:
            return 'DRAW'
        elif self.player_sum > self.dealer_sum:
            return 'WIN'
        else:
            return 'LOSE'

