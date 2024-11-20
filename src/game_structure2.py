import random
import json
from collections import defaultdict


class Card:
    def __init__(self, name, categories):
        self.name = name
        self.categories = categories

    def get_best_category_index(self):
        best_category, best_value = max(
            self.categories.items(), key=lambda item: item[1]
        )
        return list(self.categories.keys()).index(best_category)

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["categories"])


class Player:
    def __init__(self, name, cards):
        self.name = name
        self.cards = cards

    def choose_category(self):
        if not self.cards:
            return None
        top_card = self.cards[0]
        return top_card.get_best_category_index()

    def play_card(self):
        return self.cards.pop(0) if self.cards else None

    def receive_cards(self, cards):
        self.cards.extend(cards)


class Game:
    def __init__(self, players):
        self.players = players
        self.round_winner = None
        self.round_count = 0
        self.category_choice_counts = defaultdict(int)
        self.tie_count = 0
        self.tie_history = set()  # Track combinations of tie states to detect loops

    def start_round(self):
        self.round_count += 1
        if self.round_count > 1000:
            print("Stopping game due to too many rounds (possible loop).")
            return False

        if self.round_winner is None:
            self.round_winner = random.randint(0, len(self.players) - 1)

        category_index = self.players[self.round_winner].choose_category()
        if category_index is None:
            print(f"Player {self.players[self.round_winner].name} has no cards left.")
            return False

        self.category_choice_counts[category_index] += 1

        round_cards = []
        scores = []

        for player in self.players:
            if player.cards:
                card = player.play_card()
                round_cards.append(card)
                scores.append(card.categories[category_index])

        max_score = max(scores)
        winners = [
            player for player, score in zip(self.players, scores) if score == max_score
        ]

        if len(winners) > 1:
            self.tie_count += 1
            tie_state = tuple(
                (player.name, player.cards[0].name if player.cards else "None")
                for player in winners
            )
            if tie_state in self.tie_history:
                print(
                    "Detected looped tie state, breaking tie with random category choice."
                )
                category_index = random.choice(range(len(round_cards[0].categories)))
            self.tie_history.add(tie_state)

            if not self.handle_tie(winners, round_cards, category_index):
                return False
        else:
            self.round_winner = self.players.index(winners[0])

        self.players[self.round_winner].receive_cards(round_cards)
        return True

    def handle_tie(self, tied_players, round_cards, original_category_index):
        """Resolve ties with dynamic tie-breaking if excessive rounds occur."""
        print("Resolving tie...")
        tie_round_counter = 0

        while len(tied_players) > 1:
            # If tie-rounds reach threshold, switch to a random category
            if tie_round_counter > 3:
                print(
                    "Detected looped tie state, breaking tie with random category choice."
                )
                tie_break_category = random.randint(
                    0, len(round_cards[0].categories) - 1
                )
            else:
                tie_break_category = original_category_index
            print(
                f"Tie-break category chosen by previous winner or random: {tie_break_category}"
            )

            scores = []
            for player in tied_players:
                if player.cards:
                    next_card = player.play_card()
                    round_cards.append(next_card)
                    scores.append(next_card.categories[tie_break_category])
                    print(
                        f"{player.name} plays {next_card.name} with score {scores[-1]} in tie-break category {tie_break_category}"
                    )
                else:
                    scores.append(-1)

            max_score = max(scores)
            new_tied_players = [
                player
                for player, score in zip(tied_players, scores)
                if score == max_score
            ]

            if len(new_tied_players) == 1:
                self.round_winner = self.players.index(new_tied_players[0])
                print(f"{self.players[self.round_winner].name} wins the tie!")
                break
            else:
                tied_players = new_tied_players
                tie_round_counter += 1

            if tie_round_counter >= 5:
                print("Stopping due to too many tie-breaking rounds.")
                break

        if self.round_winner is not None:
            self.players[self.round_winner].receive_cards(round_cards)

    def play_game(self):
        while True:
            active_players = [player for player in self.players if player.cards]
            if len(active_players) == 1:
                self.round_winner = self.players.index(active_players[0])
                print(f"{self.players[self.round_winner].name} wins the game!")
                break
            if not self.start_round():
                print("Ending game due to unresolved rounds or excessive ties.")
                break


def simulate_games(num_simulations=1, json_file="src/card_data.json"):
    with open(json_file, "r") as f:
        card_data = json.load(f)

    for _ in range(num_simulations):
        cards = [Card.from_json(card) for card in card_data]
        random.shuffle(cards)
        players = [Player(f"Player {i+1}", cards[i::4]) for i in range(4)]

        game = Game(players)
        game.play_game()


if __name__ == "__main__":
    simulate_games(10)
