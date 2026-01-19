import pytest
from Queens.resolver import build_example_grid, EMPTY, QUEEN, BLOCKED


def coords_set(n_rows, n_cols):
    return {(r, c) for r in range(n_rows) for c in range(n_cols)}


def get_coords(grid):
    return {(cell.row, cell.col): cell for row in grid for cell in row}


def test_find_regions_single_color():
    testGrid = [
        "R R",
        "R R",
    ]
    g = build_example_grid(testGrid)
    regions = g.find_regions()
    assert len(regions) == 1
    assert set(regions[0]) == {(0, 0), (0, 1), (1, 0), (1, 1)}


def test_claim_cell_center_blocks_row_col_and_diagonals():
    testGrid = [
        "Y Y Y",
        "Y Y Y",
        "Y Y Y",
    ]
    g = build_example_grid(testGrid)
    center = g[1][1]
    g.claim_cell(center)

    # center must be queen
    assert center.value == QUEEN

    # all row/column/diagonals of center blocked (except the queen)
    expected_blocked = {
        (1, 0),
        (1, 2),  # same row
        (0, 1),
        (2, 1),  # same column
        (0, 0),
        (0, 2),
        (2, 0),
        (2, 2),  # diagonals
    }
    for (r, c), cell in get_coords(g).items():
        if (r, c) in expected_blocked:
            assert cell.value == BLOCKED
        elif (r, c) == (1, 1):
            assert cell.value == QUEEN
        else:
            # no other cells in 3x3
            pass


def test_claim_region_blocks_given_coords():
    testGrid = [
        "R R",
        "G G",
    ]
    g = build_example_grid(testGrid)
    region = [(0, 0), (0, 1)]
    g.claim_region(region)
    assert g[0][0].value == BLOCKED
    assert g[0][1].value == BLOCKED
    # other cells remain empty
    assert g[1][0].value == EMPTY
    assert g[1][1].value == EMPTY
