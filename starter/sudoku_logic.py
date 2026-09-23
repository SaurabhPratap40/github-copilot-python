"""Core Sudoku generation and validation logic.

This module contains the pure domain rules for building and validating
Sudoku boards. It intentionally has no Flask or UI dependencies.
"""

import copy
import random


SIZE = 9
EMPTY = 0

EASY = 45
MEDIUM = 36
HARD = 27

DIFFICULTY_CLUES = {
    "easy": EASY,
    "medium": MEDIUM,
    "hard": HARD,
}


def deep_copy(board):
    """Return a deep copy of a Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board():
    """Return a 9x9 board filled with empty cells."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    """Return True if placing num at row, col is valid for the board."""
    for index in range(SIZE):
        if board[row][index] == num or board[index][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3

    for row_offset in range(3):
        for col_offset in range(3):
            if board[start_row + row_offset][start_col + col_offset] == num:
                return False

    return True


def fill_board(board):
    """Fill every empty cell with a valid value using backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible_values = list(range(1, SIZE + 1))
                random.shuffle(possible_values)

                for candidate in possible_values:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate

                        if fill_board(board):
                            return True

                        board[row][col] = EMPTY

                return False

    return True


def remove_cells(board, clues):
    """Remove cells until the board has the requested number of clues."""
    attempts = SIZE * SIZE - clues

    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)

        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def _find_next_empty(board):
    """Return the next empty cell coordinate or None when the board is full."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def count_solutions(board, limit=2):
    """Count valid Sudoku completions up to the supplied limit."""
    working_board = deep_copy(board)
    solution_count = 0

    def backtrack():
        nonlocal solution_count

        if solution_count >= limit:
            return

        empty_cell = _find_next_empty(working_board)
        if empty_cell is None:
            solution_count += 1
            return

        row, col = empty_cell

        for candidate in range(1, SIZE + 1):
            if is_safe(working_board, row, col, candidate):
                working_board[row][col] = candidate
                backtrack()
                working_board[row][col] = EMPTY

                if solution_count >= limit:
                    return

    backtrack()
    return solution_count


def generate_puzzle(clues=35):
    """Generate a puzzle and the solved board that produced it."""
    max_attempts = 100

    for _ in range(max_attempts):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        puzzle = deep_copy(board)

        filled_cells = SIZE * SIZE
        candidate_positions = [
            (row, col)
            for row in range(SIZE)
            for col in range(SIZE)
        ]
        random.shuffle(candidate_positions)

        for row, col in candidate_positions:
            if filled_cells <= clues:
                break

            original_value = puzzle[row][col]
            puzzle[row][col] = EMPTY

            if count_solutions(puzzle, limit=2) == 1:
                filled_cells -= 1
                continue

            puzzle[row][col] = original_value

        if filled_cells == clues and count_solutions(puzzle, limit=2) == 1:
            return puzzle, solution

    raise RuntimeError(
        f"Could not generate a unique Sudoku puzzle with {clues} clues "
        f"after {max_attempts} attempts."
    )