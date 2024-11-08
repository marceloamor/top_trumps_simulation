import random
import json
import os


class Card:
    def __init__(self, name, categories):
        self.name = name
        self.categories = (
            categories  # Expecting a dictionary with category names and scores
        )

    def get_best_category_index(self):
        """Returns the index of the category with the highest score."""
        max_category = max(self.categories, key=self.categories.get)
        return list(self.categories.keys()).index(max_category)


class Player:
    def __init__(self, name, cards: list[Card]):
        self.name = name
        self.cards = cards

    def choose_category(self):
        """Choose the best category based on the current top card."""
        if not self.cards:
            return None  # player is eliminated
        top_card = self.cards[0]
        return top_card.get_best_category_index()

    def play_card(self):
        """Play the top card and remove it from the player's deck."""
        return self.cards.pop(0) if self.cards else None

    def receive_cards(self, cards):
        """Receive cards won in a round."""
        self.cards.extend(cards)


class Game:
    def __init__(self, players):
        self.players = players
        self.round_winner = None

    def start_round(self):
        """Start a round and determine the winner based on chosen categories."""
        active_players = [player for player in self.players if player.cards]

        # Check if we have a game winner
        if len(active_players) == 1:
            print(f"{active_players[0].name} wins the game!")
            return True  # Signal that the game has ended

        if self.round_winner is None or self.round_winner >= len(active_players):
            self.round_winner = random.randint(0, len(active_players) - 1)

        chosen_player = active_players[self.round_winner]
        category_index = chosen_player.choose_category()
        category_key = list(chosen_player.cards[0].categories.keys())[category_index]
        print(f"{chosen_player.name} chooses category {category_key}")

        round_cards = []
        scores = []

        for player in active_players:
            # Ensure each player only plays one unique card per round
            if player.cards:
                card = player.play_card()  # Remove and play card
                round_cards.append(card)
                scores.append(card.categories[category_key])
                print(
                    f"{player.name} plays {card.name} with score {scores[-1]} in category {category_key}"
                )

        max_score = max(scores)
        winners = [
            player
            for player, score in zip(active_players, scores)
            if score == max_score
        ]

        if len(winners) > 1:
            print("Tie detected!")
            self.handle_tie(winners, round_cards, category_key)
        else:
            self.round_winner = self.players.index(winners[0])
            print(f"{self.players[self.round_winner].name} wins the round!")

        # Winner takes all cards
        self.players[self.round_winner].receive_cards(round_cards)
        return False  # Signal that the game has not ended

    def handle_tie(self, tied_players, round_cards, original_category_key):
        """Resolve ties with additional tie-breaking rounds."""
        print("Resolving tie...")
        tie_rounds = 0
        max_tie_rounds = (
            10  # Set a maximum number of tie-break rounds to prevent infinite loops
        )

        while len(tied_players) > 1 and tie_rounds < max_tie_rounds:
            tie_rounds += 1
            scores = []
            tie_break_category = original_category_key

            print(f"Tie-break category chosen by previous winner: {tie_break_category}")

            for player in tied_players:
                if player.cards:
                    # Each player draws a new card for tie-break
                    next_card = player.play_card()  # Remove and play card
                    round_cards.append(next_card)
                    scores.append(next_card.categories[tie_break_category])
                    print(
                        f"{player.name} plays {next_card.name} with score {scores[-1]} in tie-break category {tie_break_category}"
                    )
                else:
                    scores.append(
                        -1
                    )  # Players without cards automatically lose the tie

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

        if tie_rounds >= max_tie_rounds:
            print(
                "Tie-breaking limit reached; declaring the player with the most cards as the winner of this round."
            )
            tied_players.sort(key=lambda player: len(player.cards), reverse=True)
            self.round_winner = self.players.index(tied_players[0])

        if self.round_winner is not None:
            self.players[self.round_winner].receive_cards(round_cards)

    def play_game(self):
        """Play the game until only one player has all the cards."""
        while True:
            active_players = [player for player in self.players if player.cards]

            if len(active_players) == 1:
                self.round_winner = self.players.index(active_players[0])
                print(f"{self.players[self.round_winner].name} wins the game!")
                break

            self.start_round()


def load_cards_from_json(filepath="src/card_data.json"):
    """Load card data from a JSON file."""
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            card_data = json.load(file)
        return [Card(card["name"], card["categories"]) for card in card_data]
    else:
        print(f"File {filepath} not found. Generating random cards instead.")
        return [
            Card(
                f"Card {i+1}",
                {f"Category {j+1}": random.randint(1, 10) for j in range(6)},
            )
            for i in range(28)
        ]


if __name__ == "__main__":
    cards = load_cards_from_json()
    random.shuffle(cards)
    players = [Player(f"Player {i+1}", cards[i::4]) for i in range(4)]
    game = Game(players)
    game.play_game()
