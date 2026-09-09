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
| Queens      | ✅ constraint propagation + backtracking (`Queens`) |
| Mini Sudoku | ✅ CLP(FD) in SWI-Prolog (`Sudoku`)              |
| Tango       | ❌ not implemented                               |
| Zip         | ❌ not implemented                               |
| Patches     | ❌ not implemented                               |
| Crossclimb  | ❌ not implemented                               |
| Pinpoint    | ❌ not implemented                               |
| Wend        | ❌ not implemented                               |

The Queens resolver first applies the usual deductions, then guesses in the
most constrained region and backtracks where those stall. If it still finds no
valid solution, nothing is clicked into the page.

## Requirements

**Firefox** is always required — Selenium drives it, so it must be installed
and on the `PATH`.

The rest depends on how you run the app:

| | Python | SWI-Prolog |
| --- | --- | --- |
| Released executable | not needed | **bundled**, nothing to install |
| From source | 3.11+ | must be installed |

SWI-Prolog powers the Sudoku resolver through `pyswip`. To run from source:

- Linux: `sudo apt-get install swi-prolog`
- macOS: `brew install swi-prolog`
- Windows: `choco install swi-prolog`

Without it, the app still starts and Queens still works; opening a Sudoku grid
prints an install hint instead of solving it.

## Install & run

Download the executable for your OS from the
[releases](https://github.com/Plouf-0/LinkedIn-GameInator/releases) and run it,
or from source:

```bash
uv sync
uv run linkedin-gameinator
```

Check that everything works before opening a browser:

```bash
linkedin-gameinator --self-test
```

It solves one Queens board and one Sudoku grid offline, and reports which
SWI-Prolog answered. `--verbose` logs the resolvers' reasoning step by step.

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

### Building the executable

```bash
uv run pyinstaller --noconfirm --clean linkedin-gameinator.spec
dist/linkedin-gameinator --self-test
```

The spec collects the SWI-Prolog found on the build machine (via
`swipl --dump-runtime-variables`) and copies its home into the bundle, minus
the documentation, demos and xpce; a runtime hook then points `SWI_HOME_DIR`
and `LIBSWIPL_PATH` at it before `pyswip` is imported. The bundled copy takes
priority over any installation on the machine running the executable; set
`USE_SYSTEM_SWIPL=1` to debug against a local one instead.

Building without SWI-Prolog installed still produces a working executable, just
one that cannot solve Sudoku. Set `REQUIRE_BUNDLED_SWIPL=1` to turn that into a
build failure, which is what CI does so a release cannot ship unbundled.

SWI-Prolog is redistributed under its own licence, a copy of which travels in
the bundle.

### Layout

| Path                | Contents                                              |
| ------------------- | ----------------------------------------------------- |
| `src/WebScrapper`   | Selenium flow and per-game page adapters              |
| `src/Queens`        | Queens grid model, resolver, archiver and terminal UI |
| `src/Sudoku`        | Sudoku resolver (Python wrapper + CLP(FD) program)    |
| `src/Archiver`      | Shared archiving base class                           |
| `packaging`         | PyInstaller helpers (SWI-Prolog collection, runtime hook) |
| `tests`             | Pytest suite                                          |
