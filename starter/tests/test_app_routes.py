import copy

import pytest

from app import CURRENT, app as flask_app
import sudoku_logic


@pytest.fixture()
def client():
    """Create a Flask test client for each test."""
    flask_app.config["TESTING"] = True

    with flask_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_game_state():
    """Reset the legacy in-memory game state before and after each test."""
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None

    yield

    CURRENT["puzzle"] = None
    CURRENT["solution"] = None


def test_index_route_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")


@pytest.mark.parametrize(
    ("difficulty", "expected_clues"),
    [
        ("easy", 45),
        ("medium", 36),
        ("hard", 27),
        ("Easy", 45),
        ("MEDIUM", 36),
        ("HaRd", 27),
    ],
)
def test_new_game_route_accepts_difficulty_values(client, difficulty, expected_clues):
    response = client.get(f"/new?difficulty={difficulty}")

    assert response.status_code == 200

    payload = response.get_json()
    puzzle = payload["puzzle"]

    filled_cells = sum(
        cell != sudoku_logic.EMPTY
        for row in puzzle
        for cell in row
    )

    assert filled_cells == expected_clues
    assert CURRENT["puzzle"] == puzzle
    assert CURRENT["solution"] is not None


@pytest.mark.parametrize("difficulty", ["invalid", "", "   "])
def test_new_game_route_rejects_invalid_or_empty_difficulty(client, difficulty):
    response = client.get(f"/new?difficulty={difficulty}")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid difficulty"}


def test_new_game_route_returns_puzzle_and_stores_solution(client):
    response = client.get("/new?clues=35")

    assert response.status_code == 200

    payload = response.get_json()

    assert "puzzle" in payload

    puzzle = payload["puzzle"]

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)

    filled_cells = sum(
        cell != sudoku_logic.EMPTY
        for row in puzzle
        for cell in row
    )

    assert filled_cells == 35

    assert CURRENT["puzzle"] == puzzle
    assert CURRENT["solution"] is not None

    assert all(
        cell != sudoku_logic.EMPTY
        for row in CURRENT["solution"]
        for cell in row
    )


def test_check_solution_route_detects_incorrect_cells(client):
    client.get("/new?clues=35")

    solution = copy.deepcopy(CURRENT["solution"])
    wrong_board = copy.deepcopy(solution)

    wrong_board[0][0] = (
        9 if solution[0][0] != 9 else 8
    )

    response = client.post(
        "/check",
        json={"board": wrong_board}
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert [0, 0] in payload["incorrect"]
    assert payload["incorrect"]


def test_check_solution_route_without_active_game_returns_400(client):
    response = client.post(
        "/check",
        json={
            "board": [
                [0] * sudoku_logic.SIZE
                for _ in range(sudoku_logic.SIZE)
            ]
        }
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "No game in progress"
    }


def test_hint_route_requires_active_game(client):
    response = client.post(
        "/hint",
        json={
            "board": [
                [0] * sudoku_logic.SIZE
                for _ in range(sudoku_logic.SIZE)
            ]
        }
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_hint_route_returns_one_valid_hint_and_updates_state(client):
    client.get("/new?clues=35")

    board = copy.deepcopy(CURRENT["puzzle"])
    user_row, user_col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if board[row][col] == sudoku_logic.EMPTY
    )
    board[user_row][user_col] = 9

    response = client.post("/hint", json={"board": board})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["hint_count"] == 1
    assert payload["message"] == "Hint applied."
    assert payload["row"] == payload["row"]
    assert payload["col"] == payload["col"]
    assert (payload["row"], payload["col"]) != (user_row, user_col)
    assert payload["value"] == CURRENT["solution"][payload["row"]][payload["col"]]
    assert CURRENT["puzzle"][payload["row"]][payload["col"]] == payload["value"]
    assert (payload["row"], payload["col"]) in CURRENT["hinted_cells"]


def test_hint_route_no_empty_cells_returns_clear_message_without_increment(client):
    client.get("/new?clues=35")
    CURRENT["puzzle"] = copy.deepcopy(CURRENT["solution"])
    CURRENT["hinted_cells"] = set()

    response = client.post(
        "/hint",
        json={"board": copy.deepcopy(CURRENT["puzzle"])}
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["message"] == "No editable empty cells remaining."
    assert payload["hint_count"] == 0
    assert CURRENT["hint_count"] == 0