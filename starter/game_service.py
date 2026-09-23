"""Service layer for the Sudoku app's current game lifecycle.

This module contains the minimal orchestration logic that sits between the
Flask route layer and the pure Sudoku domain rules in sudoku_logic.py.
"""

import sudoku_logic


def resolve_difficulty_to_clues(difficulty):
    """Normalize a difficulty name to its clue count."""
    if difficulty is None:
        raise ValueError("Invalid difficulty")

    normalized = str(difficulty).strip().lower()
    if normalized not in sudoku_logic.DIFFICULTY_CLUES:
        raise ValueError("Invalid difficulty")

    return sudoku_logic.DIFFICULTY_CLUES[normalized]


def start_new_game(clues=35, difficulty=None):
    """Create a new puzzle and return its puzzle and solution."""
    if difficulty is not None:
        clues = resolve_difficulty_to_clues(difficulty)
    elif clues is None:
        clues = 35

    return sudoku_logic.generate_puzzle(int(clues))


def validate_board(board, solution):
    """Return coordinates of cells that do not match the solution."""
    incorrect = []

    for row_index in range(sudoku_logic.SIZE):
        for col_index in range(sudoku_logic.SIZE):
            if board[row_index][col_index] != solution[row_index][col_index]:
                incorrect.append([row_index, col_index])

    return incorrect


def get_hint(board, puzzle, solution, hinted_cells=None):
    """Return the next hint as (row, col, value) using the live board state."""
    if hinted_cells is None:
        hinted_cells = set()

    for row_index in range(sudoku_logic.SIZE):
        for col_index in range(sudoku_logic.SIZE):
            if (row_index, col_index) in hinted_cells:
                continue

            if board[row_index][col_index] != sudoku_logic.EMPTY:
                continue

            if puzzle[row_index][col_index] != sudoku_logic.EMPTY:
                continue

            return row_index, col_index, solution[row_index][col_index]

    return None