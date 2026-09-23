// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudoku_leaderboard_v1';
const DARK_MODE_KEY = 'sudoku_dark_mode';
let puzzle = [];
let boardWasFull = false;
let timerIntervalId = null;
let elapsedSeconds = 0;
let hasRecordedCompletionForCurrentGame = false;

function getStoredThemePreference() {
  try {
    const rawValue = window.localStorage.getItem(DARK_MODE_KEY);
    if (rawValue === 'true' || rawValue === 'dark') {
      return true;
    }
    if (rawValue === 'false' || rawValue === 'light') {
      return false;
    }
  } catch (error) {
    // Ignore storage access errors and fall back to the default light theme.
  }

  return false;
}

function saveThemePreference(isDarkMode) {
  try {
    window.localStorage.setItem(DARK_MODE_KEY, String(isDarkMode));
  } catch (error) {
    // Ignore storage write errors and keep the app running.
  }
}

function applyTheme(isDarkMode) {
  document.body.classList.toggle('dark-mode', isDarkMode);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
  }
}

function toggleDarkMode() {
  const isDarkMode = !document.body.classList.contains('dark-mode');
  applyTheme(isDarkMode);
  saveThemePreference(isDarkMode);
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timer = document.getElementById('timer');
  if (timer) {
    timer.textContent = formatTime(elapsedSeconds);
  }
}

function resetTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }

  elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  resetTimer();
  timerIntervalId = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function updateHintCount(count) {
  const hintCount = document.getElementById('hint-count');
  if (hintCount) {
    hintCount.textContent = `Hints: ${count}`;
  }
}

function readLeaderboard() {
  try {
    const raw = window.localStorage.getItem(LEADERBOARD_KEY);
    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter(entry => entry && typeof entry === 'object');
  } catch (error) {
    return [];
  }
}

function writeLeaderboard(entries) {
  try {
    window.localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(entries));
  } catch (error) {
    // Ignore storage write failures and keep the app running.
  }
}

function sanitizePlayerName(name) {
  const trimmed = String(name || '').trim();
  if (!trimmed) {
    return 'Anonymous';
  }

  return trimmed.slice(0, 20);
}

function rankDifficulty(difficulty) {
  const order = { easy: 0, medium: 1, hard: 2 };
  return order[difficulty] ?? 3;
}

function sortLeaderboard(entries) {
  return [...entries].sort((a, b) => {
    if (Number(a.time) !== Number(b.time)) {
      return Number(a.time) - Number(b.time);
    }

    if (Number(a.hintsUsed) !== Number(b.hintsUsed)) {
      return Number(a.hintsUsed) - Number(b.hintsUsed);
    }

    const difficultyDiff = rankDifficulty(a.difficulty) - rankDifficulty(b.difficulty);
    if (difficultyDiff !== 0) {
      return difficultyDiff;
    }

    return String(a.player).localeCompare(String(b.player), undefined, { sensitivity: 'base' });
  });
}

function renderLeaderboard() {
  const list = document.getElementById('leaderboard-list');
  if (!list) {
    return;
  }

  const entries = sortLeaderboard(readLeaderboard()).slice(0, 10);
  list.innerHTML = '';

  if (entries.length === 0) {
    const emptyItem = document.createElement('li');
    emptyItem.textContent = 'No entries yet';
    list.appendChild(emptyItem);
    return;
  }

  entries.forEach((entry, index) => {
    const item = document.createElement('li');
    item.textContent = `${index + 1}. ${entry.player} — ${formatTime(entry.time)} — ${entry.difficulty} — hints ${entry.hintsUsed}`;
    list.appendChild(item);
  });
}

function addCompletedGameToLeaderboard() {
  if (hasRecordedCompletionForCurrentGame) {
    return;
  }

  const difficulty = document.getElementById('difficulty')?.value || 'medium';
  const playerName = sanitizePlayerName(window.prompt('Enter your name for the leaderboard:', 'Anonymous'));
  const entry = {
    player: playerName,
    time: elapsedSeconds,
    difficulty: difficulty,
    hintsUsed: Number(document.getElementById('hint-count')?.textContent?.replace(/\D/g, '') || 0)
  };

  const entries = sortLeaderboard(readLeaderboard());
  entries.push(entry);
  const trimmedEntries = sortLeaderboard(entries).slice(0, 10);
  writeLeaderboard(trimmedEntries);
  renderLeaderboard();
  hasRecordedCompletionForCurrentGame = true;
}

function isBoardFull() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  for (let idx = 0; idx < inputs.length; idx++) {
    const input = inputs[idx];
    if (input.disabled) continue;
    if (input.value === '') {
      return false;
    }
  }

  return true;
}

function isValidPlacement(board, row, col, value) {
  if (value === '' || value === null || value === undefined) {
    return true;
  }

  for (let i = 0; i < SIZE; i++) {
    if (i !== col && board[row][i] === value) {
      return false;
    }
    if (i !== row && board[i][col] === value) {
      return false;
    }
  }

  const startRow = Math.floor(row / 3) * 3;
  const startCol = Math.floor(col / 3) * 3;
  for (let r = startRow; r < startRow + 3; r++) {
    for (let c = startCol; c < startCol + 3; c++) {
      if ((r !== row || c !== col) && board[r][c] === value) {
        return false;
      }
    }
  }

  return true;
}

function getBoardState() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  return { board, inputs };
}

function validateCurrentCell(input) {
  if (input.disabled) {
    input.classList.remove('invalid-move');
    return;
  }

  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const value = input.value === '' ? 0 : Number(input.value);
  const { board } = getBoardState();

  if (input.value === '') {
    input.classList.remove('invalid-move');
    return;
  }

  if (isValidPlacement(board, row, col, value)) {
    input.classList.remove('invalid-move');
  } else {
    input.classList.add('invalid-move');
  }
}

function maybeCheckCompletedBoard() {
  const isFull = isBoardFull();

  if (isFull && !boardWasFull) {
    boardWasFull = true;
    checkSolution();
    return;
  }

  if (!isFull) {
    boardWasFull = false;
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        validateCurrentCell(e.target);
        maybeCheckCompletedBoard();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  boardWasFull = false;
  hasRecordedCompletionForCurrentGame = false;
  updateHintCount(0);
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function applyHint(data) {
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const cell = document.querySelector(`input[data-row="${data.row}"][data-col="${data.col}"]`);
  if (!cell) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.message || 'Unable to apply hint.';
    return;
  }

  cell.value = data.value;
  cell.disabled = true;
  cell.classList.add('prefilled');
  cell.classList.remove('invalid-move');
  updateHintCount(data.hint_count);

  msg.style.color = '#388e3c';
  msg.innerText = data.message;
  maybeCheckCompletedBoard();
}

async function requestHint() {
  const { board } = getBoardState();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();

  if (!res.ok) {
    const msg = document.getElementById('message');
    msg.style.color = '#d32f2f';
    msg.innerText = data.error || 'Unable to request a hint.';
    return;
  }

  applyHint(data);
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);

  const data = await res.json();
  if (!res.ok) {
    document.getElementById('message').innerText = data.error || 'Unable to start a new game.';
    return;
  }

  stopTimer();
  boardWasFull = false;
  hasRecordedCompletionForCurrentGame = false;
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  resetTimer();
  startTimer();
}

function applyCheckResult(data) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const msg = document.getElementById('message');

  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }

  if (incorrect.size === 0) {
    stopTimer();
    if (!hasRecordedCompletionForCurrentGame) {
      addCompletedGameToLeaderboard();
    }
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function checkSolution() {
  const { board } = getBoardState();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  applyCheckResult(data);
}

// Wire buttons
window.addEventListener('load', () => {
  const savedTheme = getStoredThemePreference();
  applyTheme(savedTheme);
  renderLeaderboard();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleDarkMode);
  // initialize
  newGame();
});