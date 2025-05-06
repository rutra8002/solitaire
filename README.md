# Console Solitaire

A text-based implementation of the classic Solitaire card game, built with Python and the Rich library.

## How to Run the Project

1. Make sure you have Python 3.6+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Gameplay Instructions

### Game Setup
- When starting, select a difficulty level:
  - **Easy**: Draw one card at a time
  - **Hard**: Draw three cards at a time

### Controls
- **d**: Draw card(s) from the stock pile
- **m**: Move card(s) between piles
  - You'll be asked to specify the source and destination
- **u**: Undo the last move (up to 3 moves)
- **n**: Start a new game
- **q**: Quit the game

### Moving Cards
When moving cards, use these codes:
- **w**: Waste pile
- **t1-t7**: Tableau piles 1-7
- **f1-f4**: Foundation piles 1-4

### Rules
- Build tableau piles in descending order with alternating colors
- Build foundation piles in ascending order by suit (starting with Ace)
- Only Kings can be placed on empty tableau spaces
- Win by moving all cards to the foundation piles

## Class and Module Descriptions

### `Solitaire` (solitaire.py)
The main game controller that manages game state and logic.
- Initializes game components
- Handles game flow and win conditions
- Manages the leaderboard and difficulty settings

### `Card` (card.py)
Simple class representing a playing card with:
- `rank`: Card rank (A, 2-10, J, Q, K)
- `suit`: Card suit (♥, ♦, ♣, ♠)
- `visible`: Boolean indicating if card is face-up

### `Deck` (deck.py)
Creates and handles the standard 52-card deck.
- `create_shuffled_deck()`: Returns a new shuffled deck of cards

### `MoveHandler` (move_handler.py)
Handles all card movement logic:
- `move_card()`: Moves cards between piles
- `_move_to_foundation()`: Logic for moving to foundation piles
- `_move_to_tableau()`: Logic for moving to tableau piles
- `get_pile_from_code()`: Converts pile codes to actual piles

### `GameDisplay` (game_display.py)
Manages the UI/UX of the game:
- `display()`: Renders the current game state
- `get_command()`: Gets player input
- `display_win_message()`: Shows congratulations and score

The game follows a Model-View-Controller pattern with:
- Model: `Card`, `Deck`, and game state attributes in `Solitaire`
- View: `GameDisplay` for rendering
- Controller: `Solitaire` and `MoveHandler` for game logic
