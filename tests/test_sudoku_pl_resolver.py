import pytest

from Sudoku.sudoku_pl_resolver import solve


def _is_valid_solution(grid: list[list[int]], rows_per_area: int) -> bool:
    size = len(grid)
    cols_per_area = 3

    rows_ok = all(sorted(row) == list(range(1, size + 1)) for row in grid)
    cols_ok = all(sorted(col) == list(range(1, size + 1)) for col in zip(*grid, strict=True))
    boxes_ok = all(
        sorted(
            grid[box_row + r][box_col + c]
            for r in range(rows_per_area)
            for c in range(cols_per_area)
        )
        == list(range(1, size + 1))
        for box_row in range(0, size, rows_per_area)
        for box_col in range(0, size, cols_per_area)
    )
    return rows_ok and cols_ok and boxes_ok


def test_solve_returns_a_valid_solution_9x9():
    grid = [
        [0, 0, 0, 7, 0, 9, 6, 0, 0],
        [0, 0, 0, 0, 0, 2, 8, 7, 0],
        [0, 0, 2, 0, 0, 0, 0, 4, 5],
        [6, 0, 0, 9, 0, 7, 0, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [5, 7, 0, 6, 0, 1, 0, 0, 4],
        [3, 5, 0, 0, 0, 0, 1, 0, 0],
        [0, 6, 4, 2, 0, 0, 0, 0, 0],
        [0, 0, 9, 1, 0, 5, 0, 0, 0],
    ]

    solution = solve(grid, rows_per_area=3)

    assert _is_valid_solution(solution, rows_per_area=3)


def test_solve_keeps_the_given_clues_9x9():
    grid = [
        [0, 0, 0, 7, 0, 9, 6, 0, 0],
        [0, 0, 0, 0, 0, 2, 8, 7, 0],
        [0, 0, 2, 0, 0, 0, 0, 4, 5],
        [6, 0, 0, 9, 0, 7, 0, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [5, 7, 0, 6, 0, 1, 0, 0, 4],
        [3, 5, 0, 0, 0, 0, 1, 0, 0],
        [0, 6, 4, 2, 0, 0, 0, 0, 0],
        [0, 0, 9, 1, 0, 5, 0, 0, 0],
    ]

    solution = solve(grid, rows_per_area=3)

    for row_idx, row in enumerate(grid):
        for col_idx, cell_value in enumerate(row):
            if cell_value != 0:
                assert solution[row_idx][col_idx] == cell_value


def test_solve_returns_a_valid_solution_6x6():
    # 6x6 grid: areas are 2 rows by 3 columns.
    grid = [
        [1, 0, 0, 4, 0, 6],
        [0, 5, 6, 0, 2, 0],
        [2, 0, 1, 0, 6, 4],
        [0, 6, 0, 2, 0, 1],
        [3, 0, 2, 6, 0, 5],
        [0, 4, 5, 0, 1, 0],
    ]

    solution = solve(grid, rows_per_area=2)

    assert _is_valid_solution(solution, rows_per_area=2)


def test_solve_keeps_the_given_clues_6x6():
    grid = [
        [1, 0, 0, 4, 0, 6],
        [0, 5, 6, 0, 2, 0],
        [2, 0, 1, 0, 6, 4],
        [0, 6, 0, 2, 0, 1],
        [3, 0, 2, 6, 0, 5],
        [0, 4, 5, 0, 1, 0],
    ]

    solution = solve(grid, rows_per_area=2)

    for row_idx, row in enumerate(grid):
        for col_idx, cell_value in enumerate(row):
            if cell_value != 0:
                assert solution[row_idx][col_idx] == cell_value


def test_solve_returns_a_valid_solution_6x6_from_screenshot():
    # 6x6 grid from the screenshot: areas are 2 rows by 3 columns.
    grid = [
        [0, 1, 2, 0, 0, 0],
        [3, 0, 4, 0, 0, 0],
        [5, 6, 1, 0, 0, 0],
        [0, 0, 0, 1, 5, 6],
        [0, 0, 0, 2, 0, 1],
        [0, 0, 0, 3, 4, 0],
    ]

    solution = solve(grid, rows_per_area=2)

    assert _is_valid_solution(solution, rows_per_area=2)
    for row_idx, row in enumerate(grid):
        for col_idx, cell_value in enumerate(row):
            if cell_value != 0:
                assert solution[row_idx][col_idx] == cell_value


def test_solve_raises_on_unsolvable_grid():
    grid = [[0] * 9 for _ in range(9)]
    grid[0][0] = 1
    grid[0][1] = 1  # Two identical values in the same row: unsolvable.

    with pytest.raises(ValueError, match="No solution found"):
        solve(grid, rows_per_area=3)
