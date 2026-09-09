![CI](https://github.com/Plouf-0/LinkedIn-GameInator/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/Plouf-0/LinkedIn-GameInator)
![License](https://img.shields.io/github/license/Plouf-0/LinkedIn-GameInator)
[![cov](https://Plouf-0.github.io/LinkedIn-GameInator/badges/coverage.svg)](https://github.com/Plouf-0/LinkedIn-GameInator/actions)

# LinkedIn-GameInator

Many different ways to resolve the LinkedIn games.

The app drives a real Firefox window: you log into LinkedIn yourself, open a
game, and the matching resolver reads the board, solves it, and plays the
solution back into the page.

## Supported games

| Game        | Resolver                                        |
| ----------- | ----------------------------------------------- |
| Queens      | ✅ constraint propagation (`Queens`)             |
| Mini Sudoku | ✅ CLP(FD) in SWI-Prolog (`Sudoku`)              |
| Tango       | ❌ not implemented                               |
| Zip         | ❌ not implemented                               |
| Patches     | ❌ not implemented                               |
| Crossclimb  | ❌ not implemented                               |
| Pinpoint    | ❌ not implemented                               |
| Wend        | ❌ not implemented                               |

The Queens resolver only propagates constraints, it never guesses. A grid that
requires a guess is left unfinished, and nothing is clicked into the page.

## Requirements

- **Python 3.11+**
- **Firefox** — Selenium drives it, so it must be installed and on the `PATH`.
- **SWI-Prolog** — required by `pyswip` for the Sudoku resolver.
  - Linux: `sudo apt-get install swi-prolog`
  - macOS: `brew install swi-prolog`
  - Windows: `choco install swi-prolog`

## Install & run

```bash
uv sync
uv run linkedin-gameinator
```

Then, in the Firefox window that opens:

1. log into your LinkedIn account (you have 10 minutes),
2. open a game from the games page,
3. watch the resolver fill it in.

The app loops back to step 2 after each game; press `Ctrl+C` to stop, and the
browser is closed for you.

Nothing is stored about your account: you type your credentials into LinkedIn's
own page, and the app never reads them.

### Archives

Each Queens grid is archived once per day under the OS's per-user data
directory, in `LinkedIn-Gameinator/Queens/<date>_Queens.txt`:

| OS      | Location                                          |
| ------- | ------------------------------------------------- |
| Windows | `%LOCALAPPDATA%\LinkedIn-Gameinator`              |
| macOS   | `~/Library/Application Support/LinkedIn-Gameinator`|
| Linux   | `$XDG_DATA_HOME/LinkedIn-Gameinator`              |

### Language

LinkedIn's board labels are read in both French and English.

## Development

```bash
uv sync --all-extras --dev
uv run pre-commit install
```

Run the same checks as CI before pushing:

```bash
./check.sh      # Linux / macOS
./check.ps1     # Windows
```

That runs `ruff check`, `ruff format --check`, `mypy`, the pre-commit hooks and
`pytest --cov`.

### Layout

| Path                | Contents                                              |
| ------------------- | ----------------------------------------------------- |
| `src/WebScrapper`   | Selenium flow and per-game page adapters              |
| `src/Queens`        | Queens grid model, resolver, archiver and terminal UI |
| `src/Sudoku`        | Sudoku resolver (Python wrapper + CLP(FD) program)    |
| `src/Archiver`      | Shared archiving base class                           |
| `tests`             | Pytest suite                                          |
