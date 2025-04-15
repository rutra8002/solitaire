from textual.app import App
from textual.widgets import Static
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
import os


class GameDisplay:
    def __init__(self, game):
        self.game = game
        self.console = Console()

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Create layout
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="game"),
            Layout(name="controls", size=3)
        )

        # Header
        layout["header"].update(Panel("=== CONSOLE SOLITAIRE ===", style="bold white on blue"))

        # Game area with stock, waste, foundations and tableau
        game_layout = Layout()
        game_layout.split(
            Layout(name="top_row", size=3),
            Layout(name="tableau")
        )

        # Stock, Waste and Foundations row
        top_table = Table(show_header=False, box=None)
        top_table.add_column("Stock")
        top_table.add_column("Waste")
        top_table.add_column("Foundations")

        # Stock display
        stock_display = "[XX]" if self.game.stock else "[ ]"

        # Waste display with colored suits
        waste_display = "[ ]"
        if self.game.waste:
            card = self.game.waste[-1]
            suit_color = "red" if card.suit in ["♥", "♦"] else "white"
            waste_display = f"[{card.rank}{Text(card.suit, style=suit_color)}]"

        # Foundations display with colored suits
        foundations_display = ""
        for i, pile in enumerate(self.game.foundations):
            if pile:
                card = pile[-1]
                suit_color = "red" if card.suit in ["♥", "♦"] else "white"
                foundations_display += f"[{card.rank}{Text(card.suit, style=suit_color)}] "
            else:
                foundations_display += f"[F{i + 1}] "

        top_table.add_row(
            f"Stock: {stock_display}",
            f"Waste: {waste_display}",
            f"Foundations: {foundations_display}"
        )
        game_layout["top_row"].update(top_table)

        # Tableau display
        tableau_table = Table(show_header=False, box=None)
        for i in range(7):
            tableau_table.add_column(f"T{i + 1}")

        max_height = max(len(pile) for pile in self.game.tableau)
        for i in range(max_height):
            row = []
            for j in range(7):
                if i < len(self.game.tableau[j]):
                    card = self.game.tableau[j][i]
                    if card.visible:
                        suit_color = "red" if card.suit in ["♥", "♦"] else "white"
                        row.append(f"[{card.rank}{Text(card.suit, style=suit_color)}]")
                    else:
                        row.append("[XX]")
                else:
                    row.append("    ")
            tableau_table.add_row(*row)

        game_layout["tableau"].update(Panel(tableau_table, title="Tableau"))
        layout["game"].update(game_layout)

        # Controls
        layout["controls"].update(
            Panel("Commands: (d)raw, (m)ove, (q)uit", style="bold white on blue")
        )

        # Render the complete layout
        self.console.print(layout)

    def get_command(self):
        return input("Enter command (d-draw, m-move, q-quit): ").lower()

    def get_move_source(self):
        return input("From (w-waste, t1-t7, f1-f4): ").lower()

    def get_move_destination(self):
        return input("To (t1-t7, f1-f4): ").lower()

    def display_move_result(self, result):
        self.console.print(Panel(result, style="bold"))

    def prompt_continue(self):
        input("Press Enter to continue...")

    def display_win_message(self):
        self.console.print(Panel("🎉 Congratulations! You win! 🎉", style="bold green"))