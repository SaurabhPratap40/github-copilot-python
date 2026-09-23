from flask import Flask, render_template, jsonify, request
import game_service

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hint_count': 0,
    'hinted_cells': set()
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')

    if difficulty is not None:
        if str(difficulty).strip() == '':
            return jsonify({'error': 'Invalid difficulty'}), 400

        try:
            puzzle, solution = game_service.start_new_game(difficulty=difficulty)
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400
    else:
        clues = request.args.get('clues', 35)
        try:
            puzzle, solution = game_service.start_new_game(clues=clues)
        except ValueError:
            return jsonify({'error': 'Invalid clue count'}), 400

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hint_count'] = 0
    CURRENT['hinted_cells'] = set()
    return jsonify({'puzzle': puzzle})

@app.route('/hint', methods=['POST'])
def request_hint():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')

    if solution is None or CURRENT.get('puzzle') is None:
        return jsonify({'error': 'No game in progress'}), 400

    if board is None:
        return jsonify({'error': 'Board is required'}), 400

    hint = game_service.get_hint(
        board,
        CURRENT['puzzle'],
        solution,
        CURRENT.get('hinted_cells', set())
    )

    if hint is None:
        return jsonify({
            'hint_count': CURRENT.get('hint_count', 0),
            'message': 'No editable empty cells remaining.'
        })

    row, col, value = hint
    CURRENT['puzzle'][row][col] = value
    CURRENT['hinted_cells'].add((row, col))
    CURRENT['hint_count'] += 1

    return jsonify({
        'row': row,
        'col': col,
        'value': value,
        'hint_count': CURRENT['hint_count'],
        'message': 'Hint applied.'
    })

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = game_service.validate_board(board, solution)
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)