from pathlib import Path

from pyswip import Prolog

PROLOG_FILE = Path(__file__).parent / "sudoku_resolver.pl"


def solve(grid: list[list[int]], rows_per_area: int) -> list[list[int]]:
    """Solve a square Sudoku grid (0 = empty cell) using the Prolog solver.

    rows_per_area is the number of rows in each area/box (e.g. 3 for a 9x9
    grid, 2 for a 6x6 grid); the width of an area is derived from it, since an
    area always holds exactly `size` cells.
    """
    size = len(grid)
    prolog = Prolog()
    prolog.consult(str(PROLOG_FILE))

    flat_grid = [cell for row in grid for cell in row]
    solutions = list(prolog.query(f"resout({flat_grid}, {size}, {rows_per_area}, X)", maxresult=1))
    if not solutions:
        raise ValueError("No solution found for the given sudoku grid")

    flat_solution: list[int] = solutions[0]["X"]
    return [flat_solution[row * size : (row + 1) * size] for row in range(size)]
