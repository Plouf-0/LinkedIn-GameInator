import sys
from pathlib import Path
from typing import Any

PROLOG_FILE_NAME = "sudoku_resolver.pl"

INSTALL_HINT = {
    "win32": "choco install swi-prolog  (or https://www.swi-prolog.org/download/stable)",
    "darwin": "brew install swi-prolog",
}.get(sys.platform, "sudo apt-get install swi-prolog")


class PrologUnavailableError(RuntimeError):
    """Raised when SWI-Prolog cannot be reached, with a way to fix it."""


def prolog_file() -> Path:
    """Return the path of the Prolog program, frozen bundle included.

    PyInstaller unpacks data files next to the module inside `sys._MEIPASS`, so
    resolving relative to `__file__` works in both cases as long as the file is
    declared in the spec's `datas`.
    """
    return Path(__file__).parent / PROLOG_FILE_NAME


def _load_prolog() -> Any:
    """Import pyswip on demand and return its `Prolog` class.

    The import is deliberately not at module level: pyswip locates and loads
    libswipl at import time, so a top-level import would stop the whole
    application from starting on a machine without SWI-Prolog -- including the
    games that do not need it.
    """
    try:
        from pyswip import Prolog
    except Exception as e:
        raise PrologUnavailableError(
            f"SWI-Prolog is required to solve Sudoku grids but could not be loaded "
            f"({e}). Install it with: {INSTALL_HINT}"
        ) from e
    return Prolog


def solve(grid: list[list[int]], rows_per_area: int) -> list[list[int]]:
    """Solve a square Sudoku grid (0 = empty cell) using the Prolog solver.

    rows_per_area is the number of rows in each area/box (e.g. 3 for a 9x9
    grid, 2 for a 6x6 grid); the width of an area is derived from it, since an
    area always holds exactly `size` cells.
    """
    prolog_class = _load_prolog()

    path = prolog_file()
    if not path.exists():
        raise PrologUnavailableError(f"The Prolog program is missing from the build: {path}")

    size = len(grid)
    prolog = prolog_class()
    prolog.consult(str(path))

    flat_grid = [cell for row in grid for cell in row]
    solutions = list(prolog.query(f"resout({flat_grid}, {size}, {rows_per_area}, X)", maxresult=1))
    if not solutions:
        raise ValueError("No solution found for the given sudoku grid")

    flat_solution: list[int] = solutions[0]["X"]
    return [flat_solution[row * size : (row + 1) * size] for row in range(size)]
