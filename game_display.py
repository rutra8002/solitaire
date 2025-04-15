import os


class GameDisplay:
    def __init__(self, game):
        self.game = game

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n=== CONSOLE SOLITAIRE ===\n")

        # Display stock and waste
        stock_display = "[XX]" if self.game.stock else "[ ]"
        waste_display = f"[{self.game.waste[-1].rank}{self.game.waste[-1].suit}]" if self.game.waste else "[ ]"
        print(f"Stock: {stock_display}  Waste: {waste_display}  ", end="")

        # Display foundations
        print("Foundations: ", end="")
        for i, pile in enumerate(self.game.foundations):
            if pile:
                print(f"[{pile[-1].rank}{pile[-1].suit}]", end=" ")
            else:
                print(f"[F{i + 1}]", end=" ")
        print("\n")

        # Display tableau
        print("Tableau:")
        max_height = max(len(pile) for pile in self.game.tableau)
        for i in range(max_height):
            for j in range(7):
                if i < len(self.game.tableau[j]):
                    card = self.game.tableau[j][i]
                    if card.visible:
                        print(f"[{card.rank}{card.suit}]", end=" ")
                    else:
                        print("[XX]", end=" ")
                else:
                    print("    ", end=" ")
            print()
        print("\n")