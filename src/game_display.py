from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED, SIMPLE, DOUBLE
from rich.layout import Layout
from rich.align import Align
from rich.padding import Padding
from src.card import Card
import os


class GameDisplay:
    def __init__(self, game):
        self.game = game
        self.console = Console()
        self.card_styles = {
            "♥": "red on default",
            "♦": "red on default",
            "♣": "blue on default",
            "♠": "blue on default",
            "back": "white on black",
            "empty": "green on default"
        }

    def _format_card(self, card, empty_label="  "):
        """Format card with proper styling"""
        if not card:
            return f"[{self.card_styles['empty']}]{empty_label}[/{self.card_styles['empty']}]"

        if not card.visible:
            return f"[{self.card_styles['back']}]XX[/{self.card_styles['back']}]"

        style = self.card_styles[card.suit]
        return f"[{style}]{card.rank}{card.suit}[/{style}]"

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Create layout
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="game"),
            Layout(name="status", size=3),
            Layout(name="controls", size=4)
        )

        # Header with title and difficulty
        difficulty_text = "EASY MODE" if self.game.difficulty == 'easy' else "HARD MODE"
        difficulty_style = "bold white on dark_green" if self.game.difficulty == 'easy' else "bold white on dark_red"
        header = Text("♣ ♦ ♠ ♥  CONSOLE SOLITAIRE  ♥ ♠ ♦ ♣", justify="center", style="bold white")
        header_panel = Panel(
            Align.center(header, vertical="middle"),
            subtitle=Text(difficulty_text, style=difficulty_style),
            box=DOUBLE
        )
        layout["header"].update(header_panel)

        # Game area layout
        game_layout = Layout()
        game_layout.split(
            Layout(name="top_row", size=6),
            Layout(name="tableau")
        )

        # Top row with stock, waste, and foundations
        top_row = Layout()
        top_row.split_row(
            Layout(name="stock_waste", ratio=2),
            Layout(name="foundations", ratio=3)
        )

        # Stock and waste display
        stock_waste_table = Table(box=SIMPLE, show_header=True, header_style="bold cyan")
        stock_waste_table.add_column("Stock", justify="center")
        stock_waste_table.add_column("Waste", justify="center")

        # Stock display
        stock_count = len(self.game.stock)
        stock_display = self._format_card(None, "S") if stock_count == 0 else self._format_card(Card("", "", False))
        stock_label = f"({stock_count})"

        # Waste display
        waste_count = len(self.game.waste)

        # Show up to 3 top cards in the waste pile
        if waste_count > 0:
            # Get up to the 3 most recent cards from waste
            visible_waste = self.game.waste[-min(3, waste_count):]

            # Format each card with proper spacing
            waste_display = ""
            for card in visible_waste:
                waste_display += f"{self._format_card(card)} "

            # Remove trailing space
            waste_display = waste_display.strip()
        else:
            waste_display = self._format_card(None, "W")

        waste_label = f"({waste_count})"

        stock_waste_table.add_row(f"{stock_display}\n{stock_label}", f"{waste_display}\n{waste_label}")
        top_row["stock_waste"].update(Panel(stock_waste_table, title="[bold]Draw Pile[/bold]", box=ROUNDED))

        # Foundations display
        foundations_table = Table(box=SIMPLE, show_header=True, header_style="bold cyan")
        for i in range(4):
            foundations_table.add_column(f"F{i + 1}", justify="center")

        foundation_displays = []
        for i, pile in enumerate(self.game.foundations):
            pile_count = len(pile)
            if pile_count > 0:
                foundation_displays.append(f"{self._format_card(pile[-1])}\n({pile_count})")
            else:
                # Use empty space instead of suit symbol for empty foundations
                foundation_displays.append(f"{self._format_card(None)}\n(0)")

        foundations_table.add_row(*foundation_displays)
        top_row["foundations"].update(Panel(foundations_table, title="[bold]Foundations[/bold]", box=ROUNDED))
        game_layout["top_row"].update(top_row)

        # Tableau display
        tableau_table = Table(box=SIMPLE, show_header=True, header_style="bold cyan")
        for i in range(7):
            pile_count = len(self.game.tableau[i])
            tableau_table.add_column(f"T{i + 1}", justify="center", style="white")

        # Calculate visible rows needed
        max_height = max(len(pile) for pile in self.game.tableau)

        # Add tableau cards
        for i in range(max_height):
            row = []
            for j in range(7):
                if i < len(self.game.tableau[j]):
                    card = self.game.tableau[j][i]
                    row.append(self._format_card(card))
                else:
                    row.append("")
            tableau_table.add_row(*row)

        # Add tableau counts as a separate row at the bottom
        counts = [f"({len(pile)})" for pile in self.game.tableau]
        tableau_table.add_row(*counts)

        game_layout["tableau"].update(Panel(tableau_table, title="[bold]Tableau[/bold]", box=ROUNDED))
        layout["game"].update(game_layout)

        # Status bar with move count and undo info
        moves_text = Text(f"Moves: {self.game.move_count}", style="bold white")
        undo_count = len(self.game.move_history)
        undo_text = Text(f"Undo available: {min(undo_count, 3)}/3", style="bold white")
        status_table = Table.grid(padding=(0, 2))
        status_table.add_column()
        status_table.add_column()
        status_table.add_row(moves_text, undo_text)
        layout["status"].update(Panel(status_table, box=ROUNDED, style="cyan"))

        # Controls
        controls = [
            ("d", "Draw card"),
            ("m", "Move card"),
            ("u", "Undo move"),
            ("n", "New game"),
            ("q", "Quit")
        ]
        controls_text = Text()
        for i, (key, desc) in enumerate(controls):
            controls_text.append(f"({key}) {desc}", style="bold yellow")
            if i < len(controls) - 1:
                controls_text.append("   |   ", style="white")  # Separator between commands

        layout["controls"].update(Panel(
            Align.center(controls_text),
            title="[bold]Controls[/bold]",
            box=ROUNDED,
            style="cyan"
        ))

        # Render the complete layout
        self.console.print(layout)

    def get_command(self):
        return self.console.input("[bold cyan]Enter command[/bold cyan]: ").lower()

    def get_move_source(self):
        return self.console.input("[bold cyan]From (w-waste, t1-t7, f1-f4)[/bold cyan]: ").lower()

    def get_move_destination(self):
        return self.console.input("[bold cyan]To (t1-t7, f1-f4)[/bold cyan]: ").lower()

    def display_move_result(self, result):
        self.console.print(Panel(result, style="bold", box=ROUNDED))

    def prompt_continue(self):
        self.console.input("[dim]Press Enter to continue...[/dim]")

    def confirm_new_game(self):
        choice = self.console.input(
            "[bold yellow]Are you sure you want to start a new game? (y/n)[/bold yellow]: ").lower()
        return choice == 'y'

    def display_win_message(self, score, leaderboard):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Create victory banner
        win_text = Text("\n🎉 CONGRATULATIONS! YOU WIN! 🎉\n", justify="center")
        win_text.stylize("bold white on green")
        score_text = Text(f"\nYour score: {score} moves\n", justify="center")
        score_text.stylize("bold yellow")

        self.console.print(Panel(win_text + score_text, box=DOUBLE))

        # Display leaderboard
        if leaderboard:
            leaderboard_table = Table(title="LEADERBOARD", title_style="bold yellow", box=ROUNDED)
            leaderboard_table.add_column("Rank", style="cyan", justify="right")
            leaderboard_table.add_column("Score", style="green")

            for i, s in enumerate(leaderboard[:10], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else " "
                leaderboard_table.add_row(f"{i}{medal}", f"{s} moves")

            self.console.print(Padding(leaderboard_table, (1, 0)))

        self.console.input("\n[dim]Press Enter to exit...[/dim]")

    def get_difficulty(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Create title
        title = Text("♣ ♦ CONSOLE SOLITAIRE ♠ ♥", justify="center")
        title.stylize("bold white")

        self.console.print(Panel(title, box=DOUBLE))

        # Create difficulty options panel
        difficulty_table = Table.grid(padding=1)
        difficulty_table.add_column(style="bold cyan")
        difficulty_table.add_column()
        difficulty_table.add_row("1.", "[bold green]Easy[/bold green] - Draw one card at a time")
        difficulty_table.add_row("2.", "[bold red]Hard[/bold red] - Draw three cards at a time")

        self.console.print(Panel(
            difficulty_table,
            title="[bold]Select Difficulty[/bold]",
            box=ROUNDED
        ))

        while True:
            choice = self.console.input("\n[bold cyan]Select difficulty (1-Easy, 2-Hard)[/bold cyan]: ")
            if choice in ['1', '2']:
                return 'easy' if choice == '1' else 'hard'
            self.console.print("[bold red]Invalid choice, please enter 1 or 2.[/bold red]")

