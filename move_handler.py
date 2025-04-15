from card import Card


class MoveHandler:
    def __init__(self, game):
        self.game = game

    def get_pile_from_code(self, code):
        """Get the actual pile from a code like w, t1, f2, etc."""
        if code == 'w':
            return self.game.waste, None
        elif code.startswith('t') and len(code) == 2:
            try:
                idx = int(code[1]) - 1
                if 0 <= idx < 7:
                    return self.game.tableau[idx], idx
            except ValueError:
                pass
        elif code.startswith('f') and len(code) == 2:
            try:
                idx = int(code[1]) - 1
                if 0 <= idx < 4:
                    return self.game.foundations[idx], idx
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
        if source_pile is self.game.waste:
            if not self.game.waste:
                return "No card in waste pile"
            card = self.game.waste[-1]

            # Moving to tableau
            if dest_pile in self.game.tableau:
                if not dest_pile:  # Empty tableau pile - only Kings allowed
                    if card.rank == 'K':
                        self.game.waste.pop()
                        dest_pile.append(card)
                        return "Moved successfully"
                    return "Only Kings can be placed on empty tableau piles"
                # Non-empty tableau pile
                if self.game.can_place_on_tableau(card, dest_pile[-1]):
                    self.game.waste.pop()
                    dest_pile.append(card)
                    return "Moved successfully"
                return "Invalid move: card must be opposite color and one rank lower"

            # Moving to foundation
            elif dest_pile in self.game.foundations:
                if self.game.can_place_on_foundation(card, dest_pile):
                    dest_pile.append(self.game.waste.pop())
                    return "Moved successfully"
                if not dest_pile:
                    return "Foundation piles must start with Ace"
                return "Invalid foundation move: must build up by suit"

        # Handle tableau to tableau/foundation movement
        elif source_pile in self.game.tableau:
            if not source_pile:
                return "No cards in this tableau pile"

            # Moving to foundation
            if dest_pile in self.game.foundations:
                # For foundation, can only move the last card in tableau pile
                if not source_pile[-1].visible:
                    return "Can't move face-down cards"

                card = source_pile[-1]
                if self.game.can_place_on_foundation(card, dest_pile):
                    dest_pile.append(source_pile.pop())
                    if source_pile and not source_pile[-1].visible:
                        source_pile[-1] = Card(source_pile[-1].rank, source_pile[-1].suit, True)
                    return "Moved successfully"

                if not dest_pile:
                    return "Foundation piles must start with Ace"
                return "Invalid foundation move: must build up by suit"

            # Find first visible card to move (for tableau to tableau)
            first_visible_idx = None
            for i, c in enumerate(source_pile):
                if c.visible:
                    first_visible_idx = i
                    break

            if first_visible_idx is None:
                return "No visible cards in this pile"

            cards_to_move = source_pile[first_visible_idx:]
            if not cards_to_move:
                return "No cards to move"

            # Moving to tableau
            if dest_pile in self.game.tableau:
                if not dest_pile:  # Empty tableau pile - only Kings allowed
                    if cards_to_move[0].rank == 'K':
                        for _ in range(len(cards_to_move)):
                            dest_pile.append(source_pile.pop(first_visible_idx))
                        if source_pile and not source_pile[-1].visible:
                            source_pile[-1] = Card(source_pile[-1].rank, source_pile[-1].suit, True)
                        return "Moved successfully"
                    return "Only Kings can be placed on empty tableau piles"

                # Non-empty tableau pile
                if self.game.can_place_on_tableau(cards_to_move[0], dest_pile[-1]):
                    for _ in range(len(cards_to_move)):
                        dest_pile.append(source_pile.pop(first_visible_idx))
                    if source_pile and not source_pile[-1].visible:
                        source_pile[-1] = Card(source_pile[-1].rank, source_pile[-1].suit, True)
                    return "Moved successfully"
                return "Invalid move: card must be opposite color and one rank lower"

        # Handle foundation to tableau movement
        elif source_pile in self.game.foundations:
            if not source_pile:
                return "No cards in this foundation pile"

            card = source_pile[-1]
            # Moving to tableau
            if dest_pile in self.game.tableau:
                if not dest_pile:  # Empty tableau - only Kings allowed
                    if card.rank == 'K':
                        dest_pile.append(source_pile.pop())
                        return "Moved successfully"
                    return "Only Kings can be placed on empty tableau piles"
                # Non-empty tableau pile
                if self.game.can_place_on_tableau(card, dest_pile[-1]):
                    dest_pile.append(source_pile.pop())
                    return "Moved successfully"
                return "Invalid move: card must be opposite color and one rank lower"

        return "Invalid move"