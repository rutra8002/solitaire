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
            Layout(name="status", size=2),
            Layout(name="controls", size=3)
        )

        # Header with difficulty
        difficulty_text = "EASY MODE" if self.game.difficulty == 'easy' else "HARD MODE"
        layout["header"].update(
            Panel(f"=== CONSOLE SOLITAIRE - {difficulty_text} ===",
                  style="bold white on rgb(0,139,0)" if self.game.difficulty == 'easy' else "bold white on rgb(139,0,0)")
        )

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

        # Stock display with count
        stock_count = len(self.game.stock)
        stock_display = f"[XX] ({stock_count})" if self.game.stock else "[ ] (0)"

        # Waste display with count and colored suits
        waste_count = len(self.game.waste)
        waste_display = "[ ] (0)"
        if self.game.waste:
            card = self.game.waste[-1]
            if card.visible:
                suit_color = "red" if card.suit in ["♥", "♦"] else "white"
                waste_display = f"[{suit_color}][{card.rank}{card.suit}][/{suit_color}] ({waste_count})"
            else:
                waste_display = f"[XX] ({waste_count})"

        # Foundations display with count and colored suits
        foundations_display = ""
        for i, pile in enumerate(self.game.foundations):
            pile_count = len(pile)
            if pile:
                card = pile[-1]
                suit_color = "red" if card.suit in ["♥", "♦"] else "white"
                foundations_display += f"[{suit_color}][{card.rank}{card.suit}][/{suit_color}] ({pile_count}) "
            else:
                foundations_display += f"[F{i + 1}] (0) "

        top_table.add_row(
            f"Stock: {stock_display}",
            f"Waste: {waste_display}",
            f"Foundations: {foundations_display}"
        )
        game_layout["top_row"].update(top_table)

        # Tableau display with card counts in headers
        tableau_table = Table(show_header=True, box=None)
        for i in range(7):
            pile_count = len(self.game.tableau[i])
            tableau_table.add_column(f"T{i + 1} ({pile_count})")

        max_height = max(len(pile) for pile in self.game.tableau)
        for i in range(max_height):
            row = []
            for j in range(7):
                if i < len(self.game.tableau[j]):
                    card = self.game.tableau[j][i]
                    if card.visible:
                        suit_color = "red" if card.suit in ["♥", "♦"] else "white"
                        row.append(f"[{suit_color}][{card.rank}{card.suit}][/{suit_color}]")
                    else:
                        row.append("[XX]")
                else:
                    row.append("    ")
            tableau_table.add_row(*row)

        game_layout["tableau"].update(Panel(tableau_table, title="Tableau"))
        layout["game"].update(game_layout)

        # Status bar with move count and undo info
        undo_info = f"Undo available: {min(len(self.game.move_history), 3)}/3"
        status_text = f"Moves: {self.game.move_count} | {undo_info}"
        layout["status"].update(Panel(status_text, style="bold white on blue"))

        # Controls
        layout["controls"].update(
            Panel("Commands: (d)raw, (m)ove, (u)ndo, (n)ew game, (q)uit", style="bold white on blue")
        )

        # Render the complete layout
        self.console.print(layout)

    def get_command(self):
        return input("Enter command (d-draw, m-move, u-undo, n-new game, q-quit): ").lower()

    def get_move_source(self):
        return input("From (w-waste, t1-t7, f1-f4): ").lower()

    def get_move_destination(self):
        return input("To (t1-t7, f1-f4): ").lower()

    def display_move_result(self, result):
        self.console.print(Panel(result, style="bold"))

    def prompt_continue(self):
        input("Press Enter to continue...")

    def confirm_new_game(self):
        choice = input("Are you sure you want to start a new game? (y/n): ").lower()
        return choice == 'y'

    def display_win_message(self, score, leaderboard):
        self.console.print(Panel(f"🎉 Congratulations! You win! 🎉\nYour score: {score} moves", style="bold green"))

        # Display leaderboard
        if leaderboard:
            self.console.print(Panel("Leaderboard (Top 10)", style="bold yellow"))
            for i, s in enumerate(leaderboard[:10], 1):
                self.console.print(f"{i}. {s} moves")

        input("Press Enter to exit...")

    def get_difficulty(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("=== CONSOLE SOLITAIRE ===", style="bold white on blue"))
        self.console.print(Panel("Select difficulty:", style="bold"))
        self.console.print("1. Easy - Draw one card at a time")
        self.console.print("2. Hard - Draw three cards at a time")

        while True:
            choice = input("\nSelect difficulty (1-Easy, 2-Hard): ")
            if choice in ['1', '2']:
                return 'easy' if choice == '1' else 'hard'
            self.console.print("[red]Invalid choice, please enter 1 or 2.[/red]")