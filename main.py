import random
import os
from collections import namedtuple

# Card representation
Card = namedtuple('Card', ['rank', 'suit', 'visible'])


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
        self.init_game()

    def init_game(self):
        # Create and shuffle deck
        deck = [Card(rank, suit, False) for suit in self.suits for rank in self.ranks]
        random.shuffle(deck)

        # Deal cards to tableau
        for i in range(7):
            for j in range(i, 7):
                card = deck.pop()
                # Only the top card in each pile is visible
                visible = (i == j)
                self.tableau[j].append(Card(card.rank, card.suit, visible))

        # Remaining cards go to stock
        self.stock = [Card(card.rank, card.suit, False) for card in deck]

    def display_game(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n=== CONSOLE SOLITAIRE ===\n")

        # Display stock and waste
        stock_display = "[XX]" if self.stock else "[ ]"
        waste_display = f"[{self.waste[-1].rank}{self.waste[-1].suit}]" if self.waste else "[ ]"
        print(f"Stock: {stock_display}  Waste: {waste_display}  ", end="")

        # Display foundations
        print("Foundations: ", end="")
        for i, pile in enumerate(self.foundations):
            if pile:
                print(f"[{pile[-1].rank}{pile[-1].suit}]", end=" ")
            else:
                print(f"[F{i + 1}]", end=" ")
        print("\n")

        # Display tableau
        print("Tableau:")
        max_height = max(len(pile) for pile in self.tableau)
        for i in range(max_height):
            for j in range(7):
                if i < len(self.tableau[j]):
                    card = self.tableau[j][i]
                    if card.visible:
                        print(f"[{card.rank}{card.suit}]", end=" ")
                    else:
                        print("[XX]", end=" ")
                else:
                    print("    ", end=" ")
            print()
        print("\n")

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

    def get_pile_from_code(self, code):
        """Get the actual pile from a code like w, t1, f2, etc."""
        if code == 'w':
            return self.waste, None
        elif code.startswith('t') and len(code) == 2:
            try:
                idx = int(code[1]) - 1
                if 0 <= idx < 7:
                    return self.tableau[idx], idx
            except ValueError:
                pass
        elif code.startswith('f') and len(code) == 2:
            try:
                idx = int(code[1]) - 1
                if 0 <= idx < 4:
                    # Print debug info to see what's happening
                    print(f"Foundation index: {idx}")
                    print(f"Foundation pile: {self.foundations[idx]}")
                    return self.foundations[idx], idx
            except ValueError:
                pass
        return None, None

    def move_card(self, source_code, dest_code):
        """Handle card movement between different piles"""
        source_pile, source_idx = self.get_pile_from_code(source_code)
        dest_pile, dest_idx = self.get_pile_from_code(dest_code)

        if source_pile is None or dest_pile is None:
            return "Invalid source or destination"

        # Handle waste to tableau/foundation
        if source_pile is self.waste:
            if not self.waste:
                return "No card in waste pile"
            card = self.waste[-1]

            # Moving to tableau
            if dest_pile in self.tableau:
                if not dest_pile:  # Empty tableau pile - only Kings allowed
                    if card.rank == 'K':
                        self.waste.pop()
                        dest_pile.append(card)
                        return "Moved successfully"
                    return "Only Kings can be placed on empty tableau piles"
                # Non-empty tableau pile
                if self.can_place_on_tableau(card, dest_pile[-1]):
                    self.waste.pop()
                    dest_pile.append(card)
                    return "Moved successfully"
                return "Invalid move: card must be opposite color and one rank lower"

            # Moving to foundation
            elif dest_pile in self.foundations:
                # Only move the last card from tableau to foundation
                card = source_pile[-1]

                if self.can_place_on_foundation(card, dest_pile):
                    dest_pile.append(source_pile.pop())
                    # Flip the new top card if needed
                    if source_pile and not source_pile[-1].visible:
                        source_pile[-1] = Card(source_pile[-1].rank, source_pile[-1].suit, True)
                    return "Moved successfully"
                return "Invalid foundation move: must start with Ace and build up by suit"
        # Handle tableau to tableau/foundation
        elif source_pile in self.tableau:
            if not source_pile:
                return "No cards in this tableau pile"

            # Find first visible card to move (and all cards after it)
            for i, c in enumerate(source_pile):
                if c.visible:
                    first_visible_idx = i
                    break
            else:
                return "No visible cards in this pile"

            cards_to_move = source_pile[first_visible_idx:]
            if not cards_to_move:
                return "No cards to move"

            # Moving to tableau
            if dest_pile in self.tableau:
                if not dest_pile:  # Empty tableau pile - only Kings allowed
                    if cards_to_move[0].rank == 'K':
                        for _ in range(len(cards_to_move)):
                            dest_pile.append(source_pile.pop(first_visible_idx))
                        if source_pile and not source_pile[-1].visible:
                            source_pile[-1] = Card(source_pile[-1].rank, source_pile[-1].suit, True)
                        return "Moved successfully"
                    return "Only Kings can be placed on empty tableau piles"
                # Non-empty tableau pile
                if self.can_place_on_tableau(cards_to_move[0], dest_pile[-1]):
                    for _ in range(len(cards_to_move)):
                        dest_pile.append(source_pile.pop(first_visible_idx))
                    if source_pile and not source_pile[-1].visible:
                        source_pile[-1] = Card(source_pile[-1].rank, source_pile[-1].suit, True)
                    return "Moved successfully"
                return "Invalid move: card must be opposite color and one rank lower"

            # Moving to foundation (only one card at a time)
            elif dest_pile in self.foundations:
                if len(cards_to_move) > 1:
                    return "Can only move one card at a time to foundation"
                card = source_pile[-1]
                if self.can_place_on_foundation(card, dest_pile):
                    dest_pile.append(source_pile.pop())
                    if source_pile and not source_pile[-1].visible:
                        source_pile[-1] = Card(source_pile[-1].rank, source_pile[-1].suit, True)
                    return "Moved successfully"
                return "Invalid foundation move: must start with Ace and build up by suit"

        return "Invalid move"

    def play(self):
        while not self.check_win():
            self.display_game()
            command = input("Enter command (d-draw, m-move, q-quit): ").lower()

            if command == 'q':
                break
            elif command == 'd':
                self.draw_card()
            elif command == 'm':
                source = input("From (w-waste, t1-t7, f1-f4): ").lower()
                dest = input("To (t1-t7, f1-f4): ").lower()
                result = self.move_card(source, dest)
                print(result)
                input("Press Enter to continue...")


if __name__ == "__main__":
    game = Solitaire()
    game.play()