from card import Card
from deck import Deck
from game_display import GameDisplay
from move_handler import MoveHandler


class Solitaire:
    def __init__(self):
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.suits = ['♥', '♦', '♣', '♠']
        self.red_suits = ['♥', '♦']
        self.black_suits = ['♣', '♠']
        self.tableau = [[] for _ in range(7)]
        self.foundations = [[] for _ in range(4)]
        self.stock = []
        self.waste = []

        self.deck = Deck()
        self.display = GameDisplay(self)
        self.move_handler = MoveHandler(self)

        self.init_game()

    def init_game(self):
        # Create and shuffle deck
        deck = self.deck.create_shuffled_deck()

        # Deal cards to tableau
        for i in range(7):
            for j in range(i, 7):
                card = deck.pop()
                # Only the top card in each pile is visible
                visible = (i == j)
                self.tableau[j].append(Card(card.rank, card.suit, visible))

        # Remaining cards go to stock
        self.stock = [Card(card.rank, card.suit, False) for card in deck]

    def draw_card(self):
        if not self.stock:
            # Recycle waste pile when stock is empty
            self.stock = [Card(card.rank, card.suit, False) for card in reversed(self.waste)]
            self.waste = []
            return

        card = self.stock.pop()
        self.waste.append(Card(card.rank, card.suit, True))

    def get_card_value(self, rank):
        return self.ranks.index(rank)

    def can_place_on_tableau(self, card, target_card):
        # Different color and one rank lower
        card_is_red = card.suit in self.red_suits
        target_is_red = target_card.suit in self.red_suits

        return (card_is_red != target_is_red and
                self.get_card_value(card.rank) == self.get_card_value(target_card.rank) - 1)

    def can_place_on_foundation(self, card, foundation):
        if not foundation:  # Empty foundation
            return card.rank == 'A'

        top_card = foundation[-1]
        return (card.suit == top_card.suit and
                self.get_card_value(card.rank) == self.get_card_value(top_card.rank) + 1)

    def check_win(self):
        # Check if all foundations have King as top card
        return all(pile and pile[-1].rank == 'K' for pile in self.foundations)

    def play(self):
        while not self.check_win():
            self.display.display()
            command = self.display.get_command()

            if command == 'q':
                break
            elif command == 'd':
                self.draw_card()
            elif command == 'm':
                source = self.display.get_move_source()
                dest = self.display.get_move_destination()
                result = self.move_handler.move_card(source, dest)
                self.display.display_move_result(result)
                self.display.prompt_continue()

        if self.check_win():
            self.display.display_win_message()