import random
from src.card import Card


class Deck:
    def __init__(self):
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.suits = ['♥', '♦', '♣', '♠']

    def create_shuffled_deck(self):
        deck = [Card(rank, suit, False) for suit in self.suits for rank in self.ranks]
        random.shuffle(deck)
        return deck