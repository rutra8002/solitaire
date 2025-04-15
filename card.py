class Card:
    def __init__(self, rank, suit, visible=False):
        self.rank = rank
        self.suit = suit
        self.visible = visible

    def __repr__(self):
        return f"Card({self.rank}, {self.suit}, {self.visible})"