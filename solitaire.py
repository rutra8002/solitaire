from card import Card
from deck import Deck
from game_display import GameDisplay
from move_handler import MoveHandler
import os
import json


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

        # New attributes
        self.difficulty = 'easy'  # Default difficulty
        self.move_count = 0
        self.move_history = []
        self.leaderboard = self.load_leaderboard()

        self.deck = Deck()
        self.display = GameDisplay(self)
        self.move_handler = MoveHandler(self)

    def load_leaderboard(self):
        if os.path.exists('leaderboard.json'):
            try:
                with open('leaderboard.json', 'r') as f:
                    return json.load(f)
            except:
                return {'easy': [], 'hard': []}
        return {'easy': [], 'hard': []}

    def save_leaderboard(self):
        with open('leaderboard.json', 'w') as f:
            json.dump(self.leaderboard, f)

    def select_difficulty(self):
        self.difficulty = self.display.get_difficulty()


    def init_game(self):
        # Create and shuffle deck
        deck = self.deck.create_shuffled_deck()

        # Reset game state
        self.tableau = [[] for _ in range(7)]
        self.foundations = [[] for _ in range(4)]
        self.stock = []
        self.waste = []
        self.move_count = 0
        self.move_history = []

        # Deal cards to tableau
        for i in range(7):
            for j in range(i, 7):
                card = deck.pop()
                # Only the top card in each pile is visible
                visible = (i == j)
                self.tableau[j].append(Card(card.rank, card.suit, visible))

        # Remaining cards go to stock
        self.stock = [Card(card.rank, card.suit, False) for card in deck]

    def record_move(self, move_type, source, destination, cards, revealed_card=None):
        """Record a move for potential undo"""
        if len(self.move_history) >= 3:
            self.move_history.pop(0)
        self.move_history.append({
            'type': move_type,
            'source': source,
            'destination': destination,
            'cards': cards,
            'revealed_card': revealed_card
        })
        self.move_count += 1

    def undo_last_move(self):
        """Undo the last move if available"""
        if not self.move_history:
            return "No moves to undo"

        move = self.move_history.pop()

        # Implement logic to undo the move based on move type
        if move['type'] == 'draw':
            # Handle undoing card draw
            cards_drawn = move['cards']
            for _ in range(len(cards_drawn)):
                if self.waste:
                    card = self.waste.pop()
                    self.stock.insert(0, Card(card.rank, card.suit, False))
            return "Undid card draw"

        elif move['type'] == 'recycle':
            # Restore waste pile from stock when undoing recycle operation
            for _ in range(len(self.stock)):
                card = self.stock.pop()
                self.waste.append(Card(card.rank, card.suit, True))
            return "Undid recycle"

        elif move['type'] == 'move':
            # Handle undoing card movement between piles
            source, source_idx = self.move_handler.get_pile_from_code(move['destination'])
            dest, dest_idx = self.move_handler.get_pile_from_code(move['source'])

            if source and dest:
                cards = move['cards']
                for card_data in cards:
                    if source:
                        source.pop()
                        dest.append(Card(card_data['rank'], card_data['suit'], card_data['visible']))

                # Check if a card was flipped during the original move
                # If source is a tableau pile and has cards, we may need to hide the top card
                if move.get('revealed_card') and dest in self.tableau and len(dest) > 1:
                    # Get the card that was below the moved card and hide it
                    card_idx = len(dest) - len(cards) - 1
                    if card_idx >= 0:
                        revealed_card = move['revealed_card']
                        dest[card_idx] = Card(revealed_card['rank'], revealed_card['suit'], False)

                return "Move undone"

        return "Could not undo move"

    def draw_card(self):
        # Store current state for undo
        drawn_cards = []

        if not self.stock:
            # Recycle waste pile when stock is empty
            drawn_cards = [{'rank': card.rank, 'suit': card.suit, 'visible': card.visible}
                           for card in self.waste]
            self.stock = [Card(card.rank, card.suit, False) for card in reversed(self.waste)]
            self.waste = []
            self.record_move('recycle', 'waste', 'stock', drawn_cards)
            return

        # Draw cards based on difficulty
        if self.difficulty == 'easy':
            if self.stock:
                card = self.stock.pop()
                self.waste.append(Card(card.rank, card.suit, True))
                drawn_cards.append({'rank': card.rank, 'suit': card.suit, 'visible': True})
        else:  # Hard mode
            for _ in range(min(3, len(self.stock))):
                card = self.stock.pop()
                visible = (_ == min(3, len(self.stock)) - 1)  # Only the top card is visible
                self.waste.append(Card(card.rank, card.suit, visible))
                drawn_cards.append({'rank': card.rank, 'suit': card.suit, 'visible': visible})

        self.record_move('draw', 'stock', 'waste', drawn_cards)

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

    def update_leaderboard(self):
        if len(self.leaderboard[self.difficulty]) < 10:
            self.leaderboard[self.difficulty].append(self.move_count)
            self.leaderboard[self.difficulty].sort()
        elif self.move_count < max(self.leaderboard[self.difficulty]):
            self.leaderboard[self.difficulty].pop()
            self.leaderboard[self.difficulty].append(self.move_count)
            self.leaderboard[self.difficulty].sort()
        self.save_leaderboard()

    def play(self):
        self.select_difficulty()
        self.init_game()

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
            elif command == 'u':
                result = self.undo_last_move()
                self.display.display_move_result(result)
                self.display.prompt_continue()
            elif command == 'n':
                if self.display.confirm_new_game():
                    self.init_game()

        if self.check_win():
            self.update_leaderboard()
            self.display.display_win_message(self.move_count, self.leaderboard[self.difficulty])