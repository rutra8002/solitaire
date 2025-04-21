class MoveHandler:
    def __init__(self, game):
        self.game = game

    def get_pile_from_code(self, code):
        """
        Converts a pile code (e.g., 't1', 'f2', 'w') into the actual pile and its index
        Returns a tuple: (pile, index) or (None, None) if invalid
        """
        if not code:
            return None, None

        # Strip whitespace and ensure lowercase
        code = code.strip().lower()

        if len(code) < 1:
            return None, None

        if code[0] == 't' and len(code) > 1:
            try:
                idx = int(code[1:]) - 1
                if 0 <= idx < 7:
                    return self.game.tableau[idx], idx
            except ValueError:
                pass

        elif code[0] == 'f' and len(code) > 1:
            try:
                idx = int(code[1:]) - 1
                if 0 <= idx < 4:
                    return self.game.foundations[idx], idx
            except ValueError:
                pass

        elif code[0] == 'w':
            return self.game.waste, None

        return None, None

    def move_card(self, source_code, dest_code):
        """
        Move card(s) from source to destination
        Returns a message indicating success or failure
        """
        source_pile, source_idx = self.get_pile_from_code(source_code)
        dest_pile, dest_idx = self.get_pile_from_code(dest_code)

        # Validate source and destination
        if source_pile is None:  # Check if None, not if empty
            return f"Invalid source: {source_code}"
        if dest_pile is None:  # Check if None, not if empty
            return f"Invalid destination: {dest_code}"
        if len(source_pile) == 0:
            return "No cards to move"

        # Handle moves based on destination type
        if dest_code.startswith('f'):
            return self._move_to_foundation(source_pile, source_idx, dest_pile, dest_idx, source_code, dest_code)
        elif dest_code.startswith('t'):
            return self._move_to_tableau(source_pile, source_idx, dest_pile, dest_idx, source_code, dest_code)
        else:
            return f"Cannot move to {dest_code}"

    def _move_to_foundation(self, source_pile, source_idx, dest_pile, dest_idx, source_code, dest_code):
        """Handle moves to foundation piles"""
        # Can only move one card at a time to foundation
        if not source_pile or len(source_pile) == 0:
            return "No cards to move"

        # Can only move the top card
        if source_code.startswith('t'):
            if not source_pile or len(source_pile) == 0:
                return "No cards in tableau pile"
            if not source_pile[-1].visible:
                return "Cannot move a face-down card"
            card = source_pile[-1]
        elif source_code.startswith('w'):
            if not source_pile or len(source_pile) == 0:
                return "No cards in waste pile"
            card = source_pile[-1]
        else:
            return "Invalid source for foundation move"

        # Check if the card can be placed on the foundation
        if not self.game.can_place_on_foundation(card, dest_pile):
            return "Invalid move: Card cannot be placed on foundation"

        # Move the card
        card_data = {'rank': card.rank, 'suit': card.suit, 'visible': card.visible}
        source_pile.pop()
        dest_pile.append(card)

        # Reveal the top card in tableau if needed
        revealed_card = None
        if source_code.startswith('t') and source_pile and not source_pile[-1].visible:
            source_pile[-1].visible = True
            revealed_card = {'rank': source_pile[-1].rank, 'suit': source_pile[-1].suit, 'visible': False}

        # Record the move
        self.game.record_move('move', source_code, dest_code, [card_data], revealed_card)
        return "Card moved to foundation"

    def _move_to_tableau(self, source_pile, source_idx, dest_pile, dest_idx, source_code, dest_code):
        """Handle moves to tableau piles"""
        if source_code.startswith('t'):
            # Find first visible card in source pile
            visible_index = -1
            for i, card in enumerate(source_pile):
                if card.visible:
                    visible_index = i
                    break

            if visible_index == -1:
                return "No visible cards to move"

            # Try moving subsets of cards, starting from all visible cards
            # and progressively reducing to just one card if needed
            cards_range = range(visible_index, len(source_pile))
            for start_idx in cards_range:
                cards_to_move = source_pile[start_idx:]

                # Check if this subset of cards can be placed
                if not dest_pile:  # Empty tableau pile
                    if cards_to_move[0].rank != 'K':
                        continue  # Try a smaller subset
                else:  # Non-empty tableau pile
                    if not self.game.can_place_on_tableau(cards_to_move[0], dest_pile[-1]):
                        continue  # Try a smaller subset

                # Found a valid subset to move
                card_data_list = [{'rank': c.rank, 'suit': c.suit, 'visible': c.visible} for c in cards_to_move]

                # Remove cards from source
                revealed_card = None
                new_len = start_idx
                if new_len > 0 and not source_pile[new_len - 1].visible:
                    source_pile[new_len - 1].visible = True
                    revealed_card = {'rank': source_pile[new_len - 1].rank,
                                     'suit': source_pile[new_len - 1].suit,
                                     'visible': False}
                source_pile[:] = source_pile[:new_len]

                # Add cards to destination
                for card in cards_to_move:
                    dest_pile.append(card)

                # Record the move
                self.game.record_move('move', source_code, dest_code, card_data_list, revealed_card)
                return f"{len(cards_to_move)} card(s) moved"

            return "Cannot move any cards to that destination"

        elif source_code.startswith('w') or source_code.startswith('f'):
            # Handle waste or foundation moves (same as before)
            if not source_pile:
                return "No cards to move"
            cards_to_move = [source_pile[-1]]

            # Check if the move is valid
            if not dest_pile:  # Empty tableau pile
                if cards_to_move[0].rank != 'K':
                    return "Only Kings can be placed on empty tableau piles"
            else:  # Non-empty tableau pile
                if not self.game.can_place_on_tableau(cards_to_move[0], dest_pile[-1]):
                    return "Invalid move: Cards must be placed in alternating colors and descending order"

            # Move the cards
            card_data_list = [{'rank': c.rank, 'suit': c.suit, 'visible': c.visible} for c in cards_to_move]

            # Remove cards from source
            source_pile.pop()

            # Add cards to destination
            for card in cards_to_move:
                dest_pile.append(card)

            # Record the move
            self.game.record_move('move', source_code, dest_code, card_data_list, None)
            return f"{len(cards_to_move)} card(s) moved"

        return "No cards to move"