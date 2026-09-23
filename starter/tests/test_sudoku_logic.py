from sudoku_logic import (
    SIZE,
    EMPTY,
    EASY,
    MEDIUM,
    HARD,
    DIFFICULTY_CLUES,
    count_solutions,
    create_empty_board,
    deep_copy,
    fill_board,
    generate_puzzle,
    is_safe,
    remove_cells,
)


def board_is_valid_sudoku(board):
    """Verify that a completed Sudoku board has no duplicate values."""
    for row in board:
        values = [value for value in row if value != EMPTY]
        assert len(values) == len(set(values))

    for col in range(SIZE):
        values = [
            board[row][col]
            for row in range(SIZE)
            if board[row][col] != EMPTY
        ]
        assert len(values) == len(set(values))

    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            values = []

            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    value = board[row][col]

                    if value != EMPTY:
                        values.append(value)

            assert len(values) == len(set(values))


def test_create_empty_board_has_9_by_9_zero_grid():
    board = create_empty_board()

    assert len(board) == SIZE
    assert all(len(row) == SIZE for row in board)
    assert all(cell == EMPTY for row in board for cell in row)


def test_deep_copy_creates_independent_copy():
    original = [[1, 2, 3], [4, 5, 6]]
    copied = deep_copy(original)

    copied[0][0] = 99

    assert original[0][0] == 1
    assert copied[0][0] == 99


def test_is_safe_rejects_duplicate_in_row():
    board = create_empty_board()

    board[0][0] = 5
    board[0][1] = 5

    assert is_safe(board, 0, 2, 5) is False


def test_is_safe_rejects_duplicate_in_box():
    board = create_empty_board()

    board[0][0] = 4
    board[1][1] = 4

    assert is_safe(board, 2, 2, 4) is False


def test_fill_board_produces_valid_completed_board():
    board = create_empty_board()

    fill_board(board)

    assert all(cell != EMPTY for row in board for cell in row)

    board_is_valid_sudoku(board)


def test_difficulty_mapping_has_expected_clue_counts():
    assert EASY == 45
    assert MEDIUM == 36
    assert HARD == 27
    assert DIFFICULTY_CLUES == {
        "easy": EASY,
        "medium": MEDIUM,
        "hard": HARD,
    }


def test_count_solutions_returns_one_for_solved_board():
    board = create_empty_board()
    fill_board(board)

    assert count_solutions(board, limit=2) == 1


def test_count_solutions_with_limit_two_on_empty_board_returns_two():
    board = create_empty_board()

    assert count_solutions(board, limit=2) == 2


def test_generate_puzzle_has_exactly_one_valid_solution():
    puzzle, solution = generate_puzzle(clues=35)

    assert count_solutions(puzzle, limit=2) == 1
    assert count_solutions(solution, limit=2) == 1


def test_generate_puzzle_respects_easy_medium_hard_clue_counts():
    for clues in (EASY, MEDIUM, HARD):
        puzzle, _ = generate_puzzle(clues=clues)

        filled_cells = sum(
            cell != EMPTY
            for row in puzzle
            for cell in row
        )

        assert filled_cells == clues


def test_remove_cells_reduces_clue_count_to_requested_amount():
    board = create_empty_board()
    fill_board(board)

    remove_cells(board, clues=35)

    filled_cells = sum(
        cell != EMPTY
        for row in board
        for cell in row
    )

    assert filled_cells == 35


def test_generate_puzzle_returns_solution_and_puzzle_shapes():
    puzzle, solution = generate_puzzle(clues=35)

    assert len(puzzle) == SIZE
    assert all(len(row) == SIZE for row in puzzle)

    assert len(solution) == SIZE
    assert all(len(row) == SIZE for row in solution)

    assert any(
        cell == EMPTY
        for row in puzzle
        for cell in row
    )

    assert all(
        cell != EMPTY
        for row in solution
        for cell in row
    )

    board_is_valid_sudoku(solution)