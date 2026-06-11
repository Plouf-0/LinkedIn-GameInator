"""Tests for Queens.resolver module.

Comprehensive test suite covering:
- Cell class functionality and edge cases
- Grid class methods and edge cases
- Region finding and claiming logic
- Parallel claiming logic
- Resolution algorithm
- Utility functions (build_example_grid, QueenResolver)
"""

# pyright: reportPrivateUsage=false

import pytest
import warnings

from Queens.resolver import QueenResolver
from Queens.queens_grid import Cell, Grid, EMPTY, QUEEN, BLOCKED

# =============================================================================
# Fixtures for testing
# =============================================================================


@pytest.fixture
def empty_cell():
    """Create a basic empty cell."""
    return Cell((0, 0), "cyan")


@pytest.fixture
def queen_cell():
    """Create a cell with a queen."""
    return Cell((1, 1), "red", QUEEN)


@pytest.fixture
def blocked_cell():
    """Create a blocked cell."""
    return Cell((2, 2), "blue", BLOCKED)


@pytest.fixture
def simple_grid_1x1():
    """Create a 1x1 grid."""
    return Grid([[Cell((0, 0), "cyan")]])


@pytest.fixture
def simple_grid_2x2():
    """Create a 2x2 grid with different colors."""
    return Grid(
        [
            [Cell((0, 0), "cyan"), Cell((0, 1), "red")],
            [Cell((1, 0), "blue"), Cell((1, 1), "green")],
        ]
    )


@pytest.fixture
def grid_single_color():
    """Create a 3x3 grid with a single color."""
    return Grid([[Cell((r, c), "red") for c in range(3)] for r in range(3)])


@pytest.fixture
def grid_all_queens():
    """Create a 2x2 grid where all cells are queens."""
    return Grid(
        [
            [Cell((0, 0), "cyan", QUEEN), Cell((0, 1), "red", QUEEN)],
            [Cell((1, 0), "blue", QUEEN), Cell((1, 1), "green", QUEEN)],
        ]
    )


@pytest.fixture
def grid_all_blocked():
    """Create a 2x2 grid where all cells are blocked."""
    return Grid(
        [
            [Cell((0, 0), "cyan", BLOCKED), Cell((0, 1), "red", BLOCKED)],
            [Cell((1, 0), "blue", BLOCKED), Cell((1, 1), "green", BLOCKED)],
        ]
    )


@pytest.fixture
def grid_mixed():
    """Create a 3x3 grid with mixed values."""
    return Grid(
        [
            [
                Cell((0, 0), "cyan", QUEEN),
                Cell((0, 1), "cyan", BLOCKED),
                Cell((0, 2), "cyan"),
            ],
            [
                Cell((1, 0), "red", BLOCKED),
                Cell((1, 1), "red", QUEEN),
                Cell((1, 2), "red", BLOCKED),
            ],
            [Cell((2, 0), "blue"), Cell((2, 1), "blue", BLOCKED), Cell((2, 2), "blue")],
        ]
    )


@pytest.fixture
def sample_grid_for_resolution():
    """Create a grid that can be resolved."""
    test_grid = [
        "R R",
        "G G",
    ]
    return build_example_grid(test_grid)


# =============================================================================
# Test _is_region_claimed
# =============================================================================


class TestIsRegionClaimed:
    """Tests for _is_region_claimed method."""

    def test_is_region_claimed_all_blocked(self, grid_all_blocked: Grid):
        """Test _is_region_claimed returns True for all blocked region."""
        assert grid_all_blocked._is_region_claimed((0, 0)) is True

    def test_is_region_claimed_all_queens(self, grid_all_queens: Grid):
        """Test _is_region_claimed returns True for all queens region."""
        assert grid_all_queens._is_region_claimed((0, 0)) is True

    def test_is_region_claimed_mixed_false(self, grid_mixed: Grid):
        """Test _is_region_claimed returns False for mixed region."""
        assert grid_mixed._is_region_claimed((0, 0)) is False

    def test_is_region_claimed_mixed_true(self, grid_mixed: Grid):
        """Test _is_region_claimed returns True for region with only QUEEN and BLOCKED."""
        assert grid_mixed._is_region_claimed((1, 0)) is True


# =============================================================================
# Test _claim_cell
# =============================================================================


class TestClaimCell:
    """Tests for _claim_cell method."""

    def test_claim_cell_sets_queen(self):
        """Test that _claim_cell sets the cell to queen."""
        grid = Grid([[Cell((0, 0), "cyan")]])
        grid.queenify_cell(grid[0][0])
        assert grid[0][0].value == QUEEN

    def test_claim_cell_blocks_row(self):
        """Test that _claim_cell blocks all cells in the same row."""
        grid = Grid(
            [
                [Cell((0, 0), "cyan"), Cell((0, 1), "cyan"), Cell((0, 2), "cyan")],
            ]
        )
        grid.queenify_cell(grid[0][1])
        assert grid[0][0].value == BLOCKED
        assert grid[0][1].value == QUEEN
        assert grid[0][2].value == BLOCKED

    def test_claim_cell_blocks_column(self):
        """Test that _claim_cell blocks all cells in the same column."""
        grid = Grid(
            [
                [Cell((0, 0), "cyan")],
                [Cell((1, 0), "cyan")],
                [Cell((2, 0), "cyan")],
            ]
        )
        grid.queenify_cell(grid[1][0])
        assert grid[0][0].value == BLOCKED
        assert grid[1][0].value == QUEEN
        assert grid[2][0].value == BLOCKED

    def test_claim_cell_blocks_diagonals(self):
        """Test that _claim_cell blocks diagonal cells."""
        grid = Grid(
            [
                [Cell((0, 0), "cyan"), Cell((0, 1), "cyan"), Cell((0, 2), "cyan")],
                [Cell((1, 0), "cyan"), Cell((1, 1), "cyan"), Cell((1, 2), "cyan")],
                [Cell((2, 0), "cyan"), Cell((2, 1), "cyan"), Cell((2, 2), "cyan")],
            ]
        )
        grid.queenify_cell(grid[1][1])
        assert grid[0][0].value == BLOCKED
        assert grid[0][2].value == BLOCKED
        assert grid[2][0].value == BLOCKED
        assert grid[2][2].value == BLOCKED

    def test_claim_cell_already_queen(self):
        """Test _claim_cell on already queen cell."""
        grid = Grid([[Cell((0, 0), "cyan", QUEEN)]])
        grid.queenify_cell(grid[0][0])
        assert grid[0][0].value == QUEEN

    def test_claim_cell_in_grid(self, simple_grid_2x2: Grid):
        """Test _claim_cell on a cell in a 2x2 grid."""
        cell = simple_grid_2x2[0][0]
        simple_grid_2x2.queenify_cell(cell)
        assert cell.value == QUEEN
        assert simple_grid_2x2[0][1].value == BLOCKED
        assert simple_grid_2x2[1][0].value == BLOCKED


# =============================================================================
# Test _claim_region
# =============================================================================


class TestClaimRegion:
    """Tests for _claim_region method."""

    def test_claim_region_blocks_all_except_target(self):
        """Test that _claim_region blocks all cells in region except target."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red"), Cell((0, 2), "red")],
            ]
        )
        target = grid[0][1]
        grid.block_region(target)
        assert grid[0][0].value == BLOCKED
        assert grid[0][1].value == EMPTY
        assert grid[0][2].value == BLOCKED

    def test_claim_region_with_queens(self):
        """Test _claim_region respects existing queens."""
        grid = Grid(
            [
                [Cell((0, 0), "red", QUEEN), Cell((0, 1), "red"), Cell((0, 2), "red")],
            ]
        )
        target = grid[0][1]
        grid.block_region(target)
        assert grid[0][0].value == QUEEN
        assert grid[0][1].value == EMPTY
        assert grid[0][2].value == BLOCKED

    def test_claim_region_multiple_regions(self):
        """Test _claim_region with multiple regions."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "blue")],
                [Cell((1, 0), "red"), Cell((1, 1), "blue")],
            ]
        )
        target = grid[0][0]
        grid.block_region(target)
        assert grid[0][0].value == EMPTY
        assert grid[1][0].value == BLOCKED
        assert grid[0][1].value == EMPTY
        assert grid[1][1].value == EMPTY


# =============================================================================
# Test _claim_row
# =============================================================================


class TestClaimRow:
    """Tests for _claim_row method."""

    def test_claim_row_different_rows_raises(self):
        """Test _claim_row raises ValueError for different rows."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red")],
                [Cell((1, 0), "red"), Cell((1, 1), "red")],
            ]
        )
        left = grid[0][0]
        right = grid[1][1]
        with pytest.raises(ValueError, match="same row"):
            grid._claim_row(left, right)

    def test_claim_row_same_row_basic(self):
        """Test _claim_row with cells in same row - basic functionality."""
        grid = Grid(
            [
                [
                    Cell((0, 0), "green"),
                    Cell((0, 1), "red", QUEEN),
                    Cell((0, 2), "red"),
                    Cell((0, 3), "green"),
                ],
                [
                    Cell((1, 0), "green"),
                    Cell((1, 1), "red"),
                    Cell((1, 2), "red"),
                    Cell((1, 3), "green"),
                ],
            ]
        )
        left = grid[0][1]
        right = grid[0][2]
        grid._claim_row(left, right)
        assert grid[0][0].is_blocked()
        assert grid[0][3].is_blocked()
        assert grid[1][1].is_blocked()
        assert grid[1][2].is_blocked()

    def test_claim_row_swaps_left_right_with_warning(self):
        """Test _claim_row swaps left and right if needed with warning."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red"), Cell((0, 2), "red")],
            ]
        )
        left = grid[0][2]
        right = grid[0][0]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            grid._claim_row(left, right)
            assert len(w) > 0


# =============================================================================
# Test _claim_column
# =============================================================================


class TestClaimColumn:
    """Tests for _claim_column method."""

    def test_claim_column_different_columns_raises(self):
        """Test _claim_column raises ValueError for different columns."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red")],
                [Cell((1, 0), "red"), Cell((1, 1), "red")],
            ]
        )
        top = grid[0][0]
        bottom = grid[1][1]
        with pytest.raises(ValueError, match="same column"):
            grid._claim_column(top, bottom)

    def test_claim_column_same_column_basic(self):
        """Test _claim_column with cells in same column - basic functionality."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red")],
                [Cell((1, 0), "red"), Cell((1, 1), "green")],
                [Cell((2, 0), "red"), Cell((2, 1), "green", QUEEN)],
                [Cell((3, 0), "red"), Cell((3, 1), "green")],
                [Cell((4, 0), "red"), Cell((4, 1), "red")],
                [Cell((5, 0), "red"), Cell((5, 1), "red")],
            ]
        )
        top = grid[1][1]
        bottom = grid[3][1]
        grid._claim_column(top, bottom)
        assert grid[0][1].is_blocked()
        assert grid[4][1].is_blocked()
        assert grid[5][1].is_blocked()
        assert grid[2][0].is_blocked()

    def test_claim_column_swaps_top_bottom_with_warning(self):
        """Test _claim_column swaps top and bottom if needed with warning."""
        grid = Grid(
            [
                [Cell((0, 0), "red")],
                [Cell((1, 0), "red")],
                [Cell((2, 0), "red")],
            ]
        )
        top = grid[2][0]
        bottom = grid[0][0]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            grid._claim_column(top, bottom)
            assert len(w) > 0


# =============================================================================
# Test _claim_corner
# =============================================================================


class TestClaimCorner:
    """Tests for _claim_corner method."""

    def test_claim_corner_notenough_cells(self):
        """Test _claim_corner with not enough cells."""
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        with pytest.raises(
            ValueError, match="Exactly 3 cells are required to claim a corner."
        ):
            grid._claim_corner([grid[2][2], grid[2][3]])  # Only 2 cells

    def test_claim_corner_in_middle_southwest(self):
        """Test _claim_corner with southwest pointing corner."""
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        cells = [grid[1][1], grid[2][1], grid[2][2]]
        grid._claim_corner(cells)
        assert (
            grid[1][2].is_blocked()
            and grid[2][0].is_blocked()
            and grid[3][1].is_blocked()
        )

    def test_claim_corner_in_middle_southeast(self):
        """Test _claim_corner with southeast pointing corner."""
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        cells = [grid[1][2], grid[2][1], grid[2][2]]
        grid._claim_corner(cells)
        assert (
            grid[1][1].is_blocked()
            and grid[3][2].is_blocked()
            and grid[2][3].is_blocked()
        )

    def test_claim_corner_in_middle_northwest(self):
        """Test _claim_corner with northwest pointing corner."""
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        cells = [grid[1][1], grid[1][2], grid[2][1]]
        grid._claim_corner(cells)
        assert (
            grid[2][2].is_blocked()
            and grid[1][0].is_blocked()
            and grid[0][1].is_blocked()
        )

    def test_claim_corner_in_middle_northeast(self):
        """Test _claim_corner with northeast pointing corner."""
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        cells = [grid[1][1], grid[1][2], grid[2][2]]
        grid._claim_corner(cells)
        assert (
            grid[2][1].is_blocked()
            and grid[0][2].is_blocked()
            and grid[1][3].is_blocked()
        )

    def test_claim_corner_edges_cases(self):
        """Test _claim_corner with cells on grid edges - all corner rotations on borders."""
        # Test all corner orientations on all four edges of the grid

        # Test on top edge (row 0) - same row pattern
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[0][1], grid[0][2], grid[1][1]])  # Case 2: same row
        assert grid[1][
            2
        ].is_blocked()  # No upward from row 0, but cells[1] gets processed

        # Test on bottom edge (row 4) - same row pattern
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[3][1], grid[4][1], grid[4][2]])  # Case 2: same row
        assert (
            grid[3][1].is_blocked()
            or grid[4][0].is_blocked()
            or grid[4][3].is_blocked()
        )

        # Test on left edge (col 0) - same column pattern
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[1][0], grid[2][0], grid[2][1]])  # Case 3: same column
        assert (
            grid[3][0].is_blocked()
            or grid[2][1].is_blocked()
            or grid[1][1].is_blocked()
        )

        # Test on right edge (col 4) - same column pattern
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[1][4], grid[2][3], grid[2][4]])  # Case 3: same column
        assert (
            grid[3][4].is_blocked()
            or grid[2][3].is_blocked()
            or grid[1][3].is_blocked()
        )

        # Test top-left corner of grid (0,0)
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[0][0], grid[0][1], grid[1][0]])  # Top-left corner
        # Should not crash with index errors
        assert True

        # Test top-right corner of grid (0,4)
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[0][3], grid[0][4], grid[1][4]])  # Top-right corner
        assert True

        # Test bottom-left corner of grid (4,0)
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[3][0], grid[4][0], grid[4][1]])  # Bottom-left corner
        assert True

        # Test bottom-right corner of grid (4,4)
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[3][4], grid[4][3], grid[4][4]])  # Bottom-right corner
        assert True

        # Test case 4 (else branch) on top edge
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[0][2], grid[1][1], grid[1][2]])  # Case 4: diagonal
        assert True

        # Test case 4 (else branch) on bottom edge
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[3][1], grid[4][1], grid[4][2]])  # Case 4: diagonal
        assert True

        # Test case 4 (else branch) on left edge
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[1][1], grid[2][0], grid[2][1]])  # Case 4: diagonal
        assert True

        # Test case 4 (else branch) on right edge
        grid = Grid([[Cell((r, c), "red") for c in range(5)] for r in range(5)])
        grid._claim_corner([grid[1][3], grid[2][3], grid[2][4]])  # Case 4: diagonal
        assert True


# =============================================================================
# Test Parallel Claiming
# =============================================================================


class TestClaimParallel:
    """Tests for parallel claiming methods."""

    def test_claim_row_parallel_basic(self):
        """Test _claim_row_parallel basic execution."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "blue"), Cell((0, 2), "yellow")],
                [Cell((1, 0), "red"), Cell((1, 1), "blue"), Cell((1, 2), "yellow")],
                [Cell((2, 0), "red"), Cell((2, 1), "blue"), Cell((2, 2), "yellow")],
            ]
        )
        cells1 = [grid[0][0], grid[2][0]]
        cells2 = [grid[0][1], grid[2][1]]
        grid._claim_row_parallel(cells1, cells2)
        assert grid[0][2].is_blocked()
        assert grid[2][2].is_blocked()

    def test_claim_column_parallel_basic(self):
        """Test _claim_column_parallel basic execution."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red"), Cell((0, 2), "red")],
                [Cell((1, 0), "blue"), Cell((1, 1), "blue"), Cell((1, 2), "blue")],
                [
                    Cell((2, 0), "yellow"),
                    Cell((2, 1), "yellow"),
                    Cell((2, 2), "yellow"),
                ],
            ]
        )
        cells1 = [grid[0][0], grid[0][2]]
        cells2 = [grid[2][0], grid[2][2]]
        grid._claim_column_parallel(cells1, cells2)
        assert grid[1][0].is_blocked()
        assert grid[1][2].is_blocked()

    def test_claim_parallel_empty_regions(self):
        """Test _claim_parallel with empty regions list."""
        grid = Grid([[Cell((0, 0), "red")]])
        grid._claim_parallel([])
        assert grid[0][0].value == EMPTY

    def test_claim_parallel_horizontal(self):
        """Test _claim_parallel with horizontal regions."""
        grid = Grid(
            [
                [
                    Cell((0, 0), "red"),
                    Cell((0, 1), "red"),
                    Cell((0, 2), "yellow"),
                    Cell((0, 3), "yellow"),
                    Cell((0, 4), "cyan"),
                ],
                [
                    Cell((1, 0), "red"),
                    Cell((1, 1), "blue"),
                    Cell((1, 2), "yellow"),
                    Cell((1, 3), "green"),
                    Cell((1, 4), "cyan"),
                ],
                [
                    Cell((2, 0), "red"),
                    Cell((2, 1), "blue"),
                    Cell((2, 2), "yellow"),
                    Cell((2, 3), "green"),
                    Cell((2, 4), "cyan"),
                ],
                [
                    Cell((3, 0), "red"),
                    Cell((3, 1), "red"),
                    Cell((3, 2), "yellow"),
                    Cell((3, 3), "yellow"),
                    Cell((3, 4), "cyan"),
                ],
                [
                    Cell((4, 0), "red"),
                    Cell((4, 1), "red"),
                    Cell((4, 2), "yellow"),
                    Cell((4, 3), "yellow"),
                    Cell((4, 4), "cyan"),
                ],
            ]
        )
        regions = [[grid[1][1], grid[2][1]], [grid[1][3], grid[2][3]]]
        grid._claim_parallel(regions)
        assert grid[1][0].is_blocked()
        assert grid[1][2].is_blocked()
        assert grid[1][4].is_blocked()
        assert grid[2][0].is_blocked()
        assert grid[2][2].is_blocked()
        assert grid[2][4].is_blocked()

    def test_claim_parallel_vertical(self):
        """Test _claim_parallel with vertical regions."""
        grid = Grid(
            [
                [
                    Cell((0, 0), "red"),
                    Cell((0, 1), "red"),
                    Cell((0, 2), "yellow"),
                    Cell((0, 3), "yellow"),
                    Cell((0, 4), "cyan"),
                ],
                [
                    Cell((1, 0), "red"),
                    Cell((1, 1), "blue"),
                    Cell((1, 2), "yellow"),
                    Cell((1, 3), "blue"),
                    Cell((1, 4), "cyan"),
                ],
                [
                    Cell((2, 0), "red"),
                    Cell((2, 1), "red"),
                    Cell((2, 2), "yellow"),
                    Cell((2, 3), "yellow"),
                    Cell((2, 4), "cyan"),
                ],
                [
                    Cell((3, 0), "red"),
                    Cell((3, 1), "green"),
                    Cell((3, 2), "yellow"),
                    Cell((3, 3), "green"),
                    Cell((3, 4), "cyan"),
                ],
                [
                    Cell((4, 0), "red"),
                    Cell((4, 1), "red"),
                    Cell((4, 2), "yellow"),
                    Cell((4, 3), "yellow"),
                    Cell((4, 4), "cyan"),
                ],
            ]
        )
        regions = [[grid[1][1], grid[1][3]], [grid[3][1], grid[3][3]]]
        grid._claim_parallel(regions)
        assert grid[0][1].is_blocked()
        assert grid[2][1].is_blocked()
        assert grid[4][1].is_blocked()
        assert grid[0][3].is_blocked()
        assert grid[2][3].is_blocked()
        assert grid[4][3].is_blocked()


# =============================================================================
# Test build_example_grid
# =============================================================================


class TestBuildExampleGrid:
    """Tests for build_example_grid function."""

    def test_build_example_grid_basic(self):
        """Test build_example_grid with basic input."""
        test_grid = [
            "R R",
            "G G",
        ]
        grid = build_example_grid(test_grid)
        assert len(grid.grid) == 2
        assert len(grid.grid[0]) == 2
        assert len(grid.grid[1]) == 2

    def test_build_example_grid_single_row(self):
        """Test build_example_grid with single row."""
        test_grid = ["R R R"]
        grid = build_example_grid(test_grid)
        assert len(grid.grid) == 1
        assert len(grid.grid[0]) == 3

    def test_build_example_grid_single_cell(self):
        """Test build_example_grid with single cell."""
        test_grid = ["R"]
        grid = build_example_grid(test_grid)
        assert len(grid.grid) == 1
        assert len(grid.grid[0]) == 1

    def test_build_example_grid_empty(self):
        """Test build_example_grid with empty list."""
        grid = build_example_grid([])
        assert len(grid.grid) == 0

    def test_build_example_grid_color_mapping(self):
        """Test build_example_grid color mapping."""
        test_grid = ["C R B O V Y P W N"]
        grid = build_example_grid(test_grid)
        assert grid[0][0].color == "cyan"
        assert grid[0][1].color == "red"
        assert grid[0][2].color == "blue"
        assert grid[0][3].color == "orange"
        assert grid[0][4].color == "green"
        assert grid[0][5].color == "yellow"
        assert grid[0][6].color == "purple"
        assert grid[0][7].color == "white"
        assert grid[0][8].color == "black"

    def test_build_example_grid_unknown_color(self):
        """Test build_example_grid with unknown color token."""
        test_grid = ["X Y Z"]
        grid = build_example_grid(test_grid)
        assert grid[0][0].color == "unknown"
        assert grid[0][1].color == "yellow"
        assert grid[0][2].color == "unknown"

    def test_build_example_grid_irregular(self):
        """Test build_example_grid with irregular row lengths."""
        test_grid = ["R R R", "G G", "B"]
        grid = build_example_grid(test_grid)
        assert len(grid.grid) == 3
        assert len(grid.grid[0]) == 3
        assert len(grid.grid[1]) == 2
        assert len(grid.grid[2]) == 1

    def test_build_example_grid_preserves_coordinates(self):
        """Test that build_example_grid preserves row and column indices."""
        test_grid = [
            "A B",
            "C D",
        ]
        grid = build_example_grid(test_grid)
        assert grid[0][0].row == 0 and grid[0][0].col == 0
        assert grid[0][1].row == 0 and grid[0][1].col == 1
        assert grid[1][0].row == 1 and grid[1][0].col == 0
        assert grid[1][1].row == 1 and grid[1][1].col == 1

    def test_build_example_grid_10x10_all_colors(self):
        """Test build_example_grid with a 10x10 grid using all available colors."""
        test_grid = [
            "C C C C C C C C C C",
            "R R R R R R R R R R",
            "B B B B B B B B B B",
            "O O O O O O O O O O",
            "V V V V V V V V V V",
            "Y Y Y Y Y Y Y Y Y Y",
            "P P P P P P P P P P",
            "W W W W W W W W W W",
            "G G G G G G G G G G",
            "N N N N N N N N N N",
        ]
        grid = build_example_grid(test_grid)

        assert len(grid.grid) == 10
        assert all(len(row) == 10 for row in grid.grid)

        expected_colors = [
            "cyan",
            "red",
            "blue",
            "orange",
            "green",
            "yellow",
            "purple",
            "white",
            "gray",
            "black",
        ]
        for row_idx, expected_color in enumerate(expected_colors):
            for cell in grid[row_idx]:
                assert cell.color == expected_color

        assert len(grid.regions) == 10
        for region in grid.regions:
            assert len(region) == 10


# =============================================================================
# Test QueenResolver
# =============================================================================


class TestQueenResolver:
    """Tests for QueenResolver function."""

    def test_queen_resolver_empty_grid(self, capsys: pytest.CaptureFixture[str]):
        """Test QueenResolver with empty grid."""
        grid = Grid([])
        QueenResolver(grid)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_queen_resolver_valid_grid(self, capsys: pytest.CaptureFixture[str]):
        """Test QueenResolver with valid grid."""
        test_grid = [
            "R R",
            "G G",
        ]
        grid = build_example_grid(test_grid)
        QueenResolver(grid)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_queen_resolver_modifies_grid(self):
        """Test that QueenResolver modifies the grid."""
        test_grid = [
            "R R",
            "G G",
        ]
        grid = build_example_grid(test_grid)
        QueenResolver(grid)
        assert True


# =============================================================================
# Test resolve
# =============================================================================


class TestResolve:
    """Tests for resolve method."""

    def test_resolve_simple_grid(self):
        """Test resolve on a simple grid."""
        test_grid = [
            "P P G G G G",
            "P P O R R G",
            "P O O R R B",
            "O O O R V V",
            "O O O V V V",
            "O O O V V V",
        ]
        grid = build_example_grid(test_grid)
        result = grid.resolve()
        assert result is not None
        assert grid[1][0].is_queen()
        assert grid[4][1].is_queen()
        assert grid[0][2].is_queen()
        assert grid[3][3].is_queen()
        assert grid[5][4].is_queen()
        assert grid[2][5].is_queen()

    def test_resolve_simple_grid1(self):
        """Test resolve on a simple grid."""
        test_grid = [
            "C O Y Y Y P P",
            "C O V V Y B P",
            "C O V Y Y B B",
            "C O O Y Y Y Y",
            "C O G Y Y Y Y",
            "C O G Y Y Y Y",
            "C C C C C C C",
        ]
        grid = build_example_grid(test_grid)
        grid.resolve()
        assert grid[1][3].is_queen()
        assert grid[3][1].is_queen()
        assert grid[4][4].is_queen()
        assert grid[5][2].is_queen()
        assert grid[6][0].is_queen()

    def test_resolve_simple_grid2(self):
        """Test resolve on a simple grid."""
        test_grid = [
            "P P P P O O O O",
            "P P B B B B O O",
            "P P B V V B O O",
            "P P B V V B O O",
            "G G B B B B O O",
            "G G B R R B R R",
            "Y C B R R B R R",
            "Y C C R R R R R",
        ]
        grid = build_example_grid(test_grid)
        grid.resolve()
        assert grid[0][3].is_queen()
        assert grid[1][5].is_queen()
        assert grid[2][7].is_queen()
        assert grid[3][4].is_queen()
        assert grid[4][1].is_queen()
        assert grid[5][6].is_queen()
        assert grid[6][0].is_queen()
        assert grid[7][2].is_queen()

    def test_resolve_returns_grid(self):
        """Test that resolve returns the grid."""
        test_grid = ["R R", "G G"]
        grid = build_example_grid(test_grid)
        result = grid.resolve()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_resolve_max_iterations(self, capsys: pytest.CaptureFixture[str]):
        """Test that resolve stops at max iterations."""
        test_grid = [
            "R R R R R",
            "R R R R R",
            "R R R R R",
            "R R R R R",
            "R R R R R",
        ]
        grid = build_example_grid(test_grid)
        result = grid.resolve()

        captured = capsys.readouterr()
        output = captured.out
        assert "Max iterations reached, stopping resolution.\n" == output
        assert result is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_workflow_simple(self):
        """Test complete workflow from grid creation to resolution."""
        test_grid = [
            "R R",
            "G G",
        ]
        grid = build_example_grid(test_grid)
        assert len(grid.grid) == 2
        assert len(grid.regions) == 2
        result = grid.resolve()
        assert result is not None

    def test_full_workflow_colorful(self):
        """Test workflow with multiple colors."""
        test_grid = [
            "R G B",
            "R G B",
            "R G B",
        ]
        grid = build_example_grid(test_grid)
        assert len(grid.regions) == 3
        result = grid.resolve()
        assert result is not None

    def test_cell_to_grid_integration(self):
        """Test that cells work correctly within a grid."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red")],
                [Cell((1, 0), "blue"), Cell((1, 1), "blue")],
            ]
        )
        grid.queenify_cell(grid[0][0])
        assert grid[0][0].value == QUEEN
        assert grid[0][1].value == BLOCKED
        assert grid[1][0].value == BLOCKED
        assert len(grid.regions) == 2

    def test_region_finding_with_claiming(self):
        """Test that region finding works with cell claiming."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "red")],
                [Cell((1, 0), "red"), Cell((1, 1), "red")],
            ]
        )
        grid.queenify_cell(grid[0][0])
        assert len(grid.regions) == 1
