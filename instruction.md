# GitHub Copilot Instructions — Sudoku Refactoring Project

## Project Goal

Refactor the legacy Python Flask Sudoku application into a clean, modular,
maintainable application while adding the required game functionality.

The application should support:

- Easy, Medium, and Hard difficulty levels
- Sudoku puzzles with exactly one unique solution
- Locked prefilled cells
- Immediate feedback for invalid entries
- Puzzle completion detection
- Hint functionality
- Check Puzzle functionality
- Game timer
- Top 10 leaderboard
- Persistent leaderboard data using browser localStorage
- Dark mode
- Responsive desktop and mobile layouts

## Code Quality

- Use clear and descriptive names for variables, functions, and classes.
- Keep functions focused on one responsibility.
- Prefer small, reusable functions over large functions.
- Use consistent 4-space indentation.
- Follow modern Python practices.
- Add useful comments for non-obvious logic.
- Avoid unnecessary duplication.
- Handle errors gracefully.
- Keep game logic separate from Flask routes and presentation logic.
- Do not introduce unnecessary dependencies.

## Sudoku Logic

- Keep Sudoku generation, validation, solving, and puzzle logic modular.
- Generated puzzles must have exactly one valid solution.
- Difficulty levels should control the number of prefilled cells.
- Prefilled cells must not be editable by the player.
- Player moves must be validated against Sudoku rules.
- Avoid changing working functionality unless necessary.

## Flask Application

- Keep Flask routes organized and easy to understand.
- Separate application logic from HTML templates where practical.
- Use clear request and response handling.
- Validate user input before processing it.
- Avoid exposing unnecessary internal implementation details.

## Frontend

- Use semantic HTML where practical.
- Keep CSS organized and readable.
- The interface must work in both light and dark modes.
- The layout must work on desktop and mobile screens.
- Sudoku 3x3 blocks should have alternating visual styles.
- Buttons and text should remain readable in all themes.
- Avoid unnecessary animations or visual effects that reduce usability.

## Testing

- Preserve existing functionality when refactoring.
- Run the test suite after significant changes.
- New functionality should be testable independently.
- Do not remove tests just to make the test suite pass.
- When a test fails, investigate the underlying cause before changing the test.

## GitHub Copilot Usage

When suggesting code:

1. Explain the purpose of significant changes when useful.
2. Prefer incremental changes instead of rewriting unrelated code.
3. Preserve existing working functionality.
4. Point out assumptions or potential edge cases.
5. If there are multiple reasonable approaches, explain the trade-offs.
6. Do not add unnecessary libraries or architectural complexity.

## Responsible AI Development

Treat Copilot suggestions as proposals rather than automatically correct solutions.

Before accepting generated code:

- Review what the code does.
- Check that it fits the existing project structure.
- Check for unnecessary complexity.
- Test the implementation.
- Reject or modify suggestions that do not meet the project requirements.

## Project Documentation

Keep the README updated with:

- Project description
- Setup instructions
- How to run the Flask application
- How to run the tests
- Main application features

Document important development decisions where appropriate.