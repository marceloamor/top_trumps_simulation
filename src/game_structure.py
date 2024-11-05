import random


class Card:
    def __init__(self, name, categories):
        self.name = name
        self.categories = categories  # Expecting a list of category scores

    def get_best_category_index(self):
        """returns the index of the category with the highest score
        Add logic here to handle ties if desired
        Upgrade: Add strategies based on knolwedge of the game,
        cards in hand, cards played, etc.
        """
        return self.categories.index(max(self.categories))


class Player:
    def __init__(self, name, cards: list[Card]):
        self.name = name
        self.cards = cards

    def choose_category(self):
        """Choose the best category based on the current top card
        Current implementation assumes the player is aware of the best category
        and always chooses it.
        Upgrade:
        Add logic here to choose the best category based on the player's individual strategy
        """
        if not self.cards:
            return None  # player is eliminated
        top_card = self.cards[0]
        return top_card.get_best_category_index()

    def play_card(self):
        """play the top card and remove it from the player's deck."""
        return self.cards.pop(0) if self.cards else None

    def receive_cards(self, cards):
        """receive cards won in a round."""
        self.cards.extend(cards)


class Game:
    def __init__(self, players):
        self.players = players
        self.round_winner = None

    def start_round(self):
        """Start a round and determine the winner based on chosen categories."""
        # Choose a random player to start the round if it's the first round
        if self.round_winner is None:
            self.round_winner = random.randint(0, len(self.players) - 1)

        category_index = self.players[self.round_winner].choose_category()
        print(
            f"{self.players[self.round_winner].name} chooses category {category_index}"
        )

        # Compare cards based on the chosen category
        round_cards = []
        scores = []

        for player in self.players:
            if player.cards:  # Ensure the player has cards to play
                card = player.play_card()
                round_cards.append(card)
                scores.append(card.categories[category_index])
                print(
                    f"{player.name} plays {card.name} with score {scores[-1]} in category {category_index}"
                )

        # Determine the round winner
        max_score = max(scores)
        winners = [
            player for player, score in zip(self.players, scores) if score == max_score
        ]

        if len(winners) > 1:
            # Handle ties
            print("Tie detected!")
            self.handle_tie(winners, round_cards, category_index)
        else:
            self.round_winner = winners[0]
            print(f"{self.round_winner.name} wins the round!")

        # Award cards to the winner
        self.round_winner.receive_cards(round_cards)

    def handle_tie(self, tied_players, round_cards, original_category_index):
        """Resolve ties by letting the previous winner choose the tie-break category and comparing the next cards."""
        print("Resolving tie...")

        while len(tied_players) > 1:
            # The player who chose the original category (round winner) picks the tie-break category
            tie_break_category = original_category_index

            print(f"Tie-break category chosen by previous winner: {tie_break_category}")

            scores = []
            for player in tied_players:
                if player.cards:
                    next_card = player.play_card()
                    round_cards.append(
                        next_card
                    )  # Add to cards that the winner will collect
                    scores.append(next_card.categories[tie_break_category])
                    print(
                        f"{player.name} plays {next_card.name} with score {scores[-1]} in tie-break category {tie_break_category}"
                    )
                else:
                    # If a player has no cards left, they can't continue in the tie-breaking process
                    scores.append(-1)  # Assign a very low score for elimination

            max_score = max(scores)
            new_tied_players = [
                player
                for player, score in zip(tied_players, scores)
                if score == max_score
            ]

            if len(new_tied_players) == 1:
                self.round_winner = new_tied_players[0]
                print(f"{self.round_winner.name} wins the tie!")
                break
            else:
                tied_players = new_tied_players  # Narrow down the tied players

        # Award all collected round cards to the winner of the tie
        if self.round_winner:
            self.round_winner.receive_cards(round_cards)

    def play_game(self):
        """Play the game until one player has all the cards."""
        while all(player.cards for player in self.players):
            self.start_round()

        print(f"{self.round_winner.name} wins the game!")


# Example usage (This part can be in another file or a test function):
if __name__ == "__main__":
    # Create example cards
    cards = [
        Card(f"Card {i+1}", [random.randint(1, 10) for _ in range(6)])
        for i in range(28)
    ]

    # Create players with shuffled cards
    random.shuffle(cards)
    players = [Player(f"Player {i+1}", cards[i::4]) for i in range(4)]  # 4 players

    # Start the game
    game = Game(players)
    game.play_game()
