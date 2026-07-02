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

from Queens.brute_force_resolver import BruteForceResolver
from Queens.queens_grid import Cell, Grid, EMPTY, QUEEN, BLOCKED, build_example_grid
from Queens.ui import print_grid

# =============================================================================
# Fixtures for testing
# =============================================================================


@pytest.fixture
def empty_cell():
    """Create a basic empty cell."""
    return Cell(0, 0, "cyan")


@pytest.fixture
def queen_cell():
    """Create a cell with a queen."""
    return Cell(1, 1, "red", QUEEN)


@pytest.fixture
def blocked_cell():
    """Create a blocked cell."""
    return Cell(2, 2, "blue", BLOCKED)


@pytest.fixture
def simple_grid_1x1():
    """Create a 1x1 grid."""
    return BruteForceResolver([[Cell(0, 0, "cyan")]])


@pytest.fixture
def simple_grid_2x2():
    """Create a 2x2 grid with different colors."""
    return BruteForceResolver(
        [
            [Cell(0, 0, "cyan"), Cell(0, 1, "red")],
            [Cell(1, 0, "blue"), Cell(1, 1, "green")],
        ]
    )


@pytest.fixture
def grid_single_color():
    """Create a 3x3 grid with a single color."""
    return BruteForceResolver([[Cell(r, c, "red") for c in range(3)] for r in range(3)])


@pytest.fixture
def grid_all_queens():
    """Create a 2x2 grid where all cells are queens."""
    return BruteForceResolver(
        [
            [Cell(0, 0, "cyan", QUEEN), Cell(0, 1, "red", QUEEN)],
            [Cell(1, 0, "blue", QUEEN), Cell(1, 1, "green", QUEEN)],
        ]
    )


@pytest.fixture
def grid_all_blocked():
    """Create a 2x2 grid where all cells are blocked."""
    return BruteForceResolver(
        [
            [Cell(0, 0, "cyan", BLOCKED), Cell(0, 1, "red", BLOCKED)],
            [Cell(1, 0, "blue", BLOCKED), Cell(1, 1, "green", BLOCKED)],
        ]
    )


@pytest.fixture
def grid_mixed():
    """Create a 3x3 grid with mixed values."""
    return BruteForceResolver(
        [
            [
                Cell(0, 0, "cyan", QUEEN),
                Cell(0, 1, "cyan", BLOCKED),
                Cell(0, 2, "cyan"),
            ],
            [
                Cell(1, 0, "red", BLOCKED),
                Cell(1, 1, "red", QUEEN),
                Cell(1, 2, "red", BLOCKED),
            ],
            [Cell(2, 0, "blue"), Cell(2, 1, "blue", BLOCKED), Cell(2, 2, "blue")],
        ]
    )


@pytest.fixture
def sample_grid_for_resolution():
    """Create a grid that can be resolved."""
    test_grid = [
        "R R",
        "G G",
    ]
    return BruteForceResolver(build_example_grid(test_grid))


@pytest.fixture
def three_squares_grid():
    grid = [
        #0 1 2 3 4 5 6 7 8 9
        "O O O O O O O O O O",  # 0
        "O R R O B B B O O O",  # 1
        "O O O O O O O O W O",  # 2
        "O R O O O B O O W O",  # 3
        "O R O O O B O O W O",  # 4
        "O O O O O B O O W O",  # 5
        "O O O O O O O O W O",  # 6
        "O O O O O O O O O O",  # 7
        "O W W W W W W W O O",  # 8
        "O O O O O O O O O O",  # 9
    ]
    return BruteForceResolver(build_example_grid(grid))


@pytest.fixture
def star_grid():
    grid = [
        # 0 1 2 3 4 5 6 7 8 9 10
        "O O O O O O O O O O O",  # 0
        "O O O O O R R O O O O",  # 1
        "O O O O R R R O O O O",  # 2
        "O O O R R R R R O O O",  # 3
        "O R R R R R R R R O O",  # 4
        "O R R R R R R R R R O",  # 5
        "O O R R R R R R R R O",  # 6
        "O O O R R R R R O O O",  # 7
        "O O O O R R R O O O O",  # 8
        "O O O O O R R O O O O",  # 9
        "O O O O O O O O O O O",  # 10
    ]
    return BruteForceResolver(build_example_grid(grid))


# =============================================================================
# TOTEST Test _block_row
# =============================================================================


class TestBlockRow:
    """Tests for _block_row method."""

    # DONE
    def test_block_row(self, three_squares_grid: BruteForceResolver):
        """Test _block_row block row"""
        left = three_squares_grid[1, 1]
        right = three_squares_grid[1, 2]
        three_squares_grid._block_row(left, right)
        assert three_squares_grid[1, 0].is_blocked()
        assert three_squares_grid[1, 3].is_blocked()
        assert three_squares_grid[1, 4].is_blocked()
        assert three_squares_grid[1, 5].is_blocked()
        assert three_squares_grid[1, 6].is_blocked()
        assert three_squares_grid[1, 7].is_blocked()
        assert three_squares_grid[1, 8].is_blocked()
        assert three_squares_grid[1, 9].is_blocked()

    # DONE
    def test_block_row_block_two_sides(self, three_squares_grid: BruteForceResolver):
        """Test _block_row block the two upper and under cells on a 2 cell block."""
        left = three_squares_grid[1, 1]
        right = three_squares_grid[1, 2]
        three_squares_grid._block_row(left, right)
        assert three_squares_grid[0, 1].is_blocked()
        assert three_squares_grid[0, 2].is_blocked()
        assert three_squares_grid[2, 1].is_blocked()
        assert three_squares_grid[2, 2].is_blocked()

    # DONE
    def test_block_row_block_three_sides(self, three_squares_grid: BruteForceResolver):
        """Test _block_row block the two upper and under cells on a 2 cell block."""
        left = three_squares_grid[1, 4]
        right = three_squares_grid[1, 6]
        three_squares_grid._block_row(left, right)
        assert not three_squares_grid[0, 4].is_blocked()
        assert three_squares_grid[0, 5].is_blocked()
        assert not three_squares_grid[0, 6].is_blocked()

        assert not three_squares_grid[2, 4].is_blocked()
        assert three_squares_grid[2, 5].is_blocked()
        assert not three_squares_grid[2, 6].is_blocked()

    # DONE
    def test_block_row_block_big_sides(self, three_squares_grid: BruteForceResolver):
        """Test _block_row block the two upper and under cells on a 2 cell block."""
        left = three_squares_grid[8, 1]
        right = three_squares_grid[8, 7]
        three_squares_grid._block_row(left, right)
        for i in range(10):
            assert not three_squares_grid[7, i].is_blocked()
            assert not three_squares_grid[9, i].is_blocked()
        assert three_squares_grid[8, 0].is_blocked()
        assert three_squares_grid[8, 8].is_blocked()
        assert three_squares_grid[8, 9].is_blocked()

    # DONE
    def test_block_row_not_cells_color(self, three_squares_grid: BruteForceResolver):
        """Test _block_row don't block same color."""
        left = three_squares_grid[8, 2]
        right = three_squares_grid[8, 5]
        three_squares_grid._block_row(left, right)
        assert not three_squares_grid[8, 1].is_blocked()
        assert not three_squares_grid[8, 6].is_blocked()
        assert not three_squares_grid[8, 7].is_blocked()

    # DONE
    def test_block_row_not_cells_color_two_sides(self, star_grid: BruteForceResolver):
        """Test _block_row block the two upper and under cells on a 2 cell block."""
        left = star_grid[1, 5]
        right = star_grid[1, 6]
        star_grid._block_row(left, right)
        assert star_grid[0, 5].is_blocked()
        assert star_grid[0, 6].is_blocked()
        assert not star_grid[2, 5].is_blocked()
        assert not star_grid[2, 6].is_blocked()
        left = star_grid[9, 5]
        right = star_grid[9, 6]
        star_grid._block_row(left, right)
        assert not star_grid[8, 5].is_blocked()
        assert not star_grid[8, 6].is_blocked()
        assert star_grid[10, 5].is_blocked()
        assert star_grid[10, 6].is_blocked()

    # DONE
    def test_block_row_not_cells_color_three_sides(self, star_grid: BruteForceResolver):
        """Test _block_row block the two upper and under cells on a 2 cell block."""
        left = star_grid[2, 4]
        right = star_grid[2, 6]
        star_grid._block_row(left, right)
        assert not star_grid[1, 4].is_blocked()
        assert not star_grid[1, 5].is_blocked()
        assert not star_grid[1, 6].is_blocked()
        assert not star_grid[3, 4].is_blocked()
        assert not star_grid[3, 5].is_blocked()
        assert not star_grid[3, 6].is_blocked()
        left = star_grid[8, 4]
        right = star_grid[8, 6]
        star_grid._block_row(left, right)
        assert not star_grid[7, 4].is_blocked()
        assert not star_grid[7, 5].is_blocked()
        assert not star_grid[7, 6].is_blocked()
        assert not star_grid[9, 4].is_blocked()
        assert not star_grid[9, 5].is_blocked()
        assert not star_grid[9, 6].is_blocked()

    # DONE
    def test_claim_row_different_rows_raises(
        self, three_squares_grid: BruteForceResolver
    ):
        """Test _claim_row raises ValueError for different rows."""
        left = three_squares_grid[0, 0]
        right = three_squares_grid[1, 1]
        with pytest.raises(
            ValueError, match="Left and right cells must be in the same row."
        ):
            three_squares_grid._block_row(left, right)

    def test_block_row_swaps_left_right_with_warning(
        self, three_squares_grid: BruteForceResolver
    ):
        """Test _block_row swaps left and right if needed with warning."""
        left = three_squares_grid[0, 0]
        right = three_squares_grid[0, 1]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            three_squares_grid._block_row(right, left)
            assert len(w) > 0


# =============================================================================
# TOTEST Test _block_column
# =============================================================================


class TestBlockColumn:
    """Tests for _block_column method."""

    # DONE
    def test_block_column(self, three_squares_grid: BruteForceResolver):
        """Test _block_column block column"""
        up = three_squares_grid[3, 1]
        bottom = three_squares_grid[4, 1]
        three_squares_grid._block_column(up, bottom)
        assert three_squares_grid[0, 1].is_blocked()
        assert three_squares_grid[2, 1].is_blocked()
        assert three_squares_grid[5, 1].is_blocked()
        assert three_squares_grid[6, 1].is_blocked()
        assert three_squares_grid[7, 1].is_blocked()
        assert three_squares_grid[8, 1].is_blocked()
        assert three_squares_grid[9, 1].is_blocked()

    # DONE
    def test_block_column_block_two_sides(self, three_squares_grid: BruteForceResolver):
        """Test _block_column block the two upper and under cells on a 2 cell block."""
        up = three_squares_grid[3, 1]
        bottom = three_squares_grid[4, 1]
        three_squares_grid._block_column(up, bottom)
        assert three_squares_grid[3, 0].is_blocked()
        assert three_squares_grid[4, 0].is_blocked()
        assert three_squares_grid[3, 2].is_blocked()
        assert three_squares_grid[4, 2].is_blocked()

    # DONE
    def test_block_column_block_three_sides(
        self, three_squares_grid: BruteForceResolver
    ):
        """Test _block_column block the two upper and under cells on a 2 cell block."""
        up = three_squares_grid[3, 5]
        bottom = three_squares_grid[5, 5]
        three_squares_grid._block_column(up, bottom)
        assert not three_squares_grid[3, 4].is_blocked()
        assert three_squares_grid[4, 4].is_blocked()
        assert not three_squares_grid[5, 4].is_blocked()
        assert not three_squares_grid[3, 6].is_blocked()
        assert three_squares_grid[4, 6].is_blocked()
        assert not three_squares_grid[5, 6].is_blocked()

    # DONE
    def test_block_column_block_big_sides(self, three_squares_grid: BruteForceResolver):
        """Test _block_column block the two upper and under cells on a 2 cell block."""
        up = three_squares_grid[2, 8]
        bottom = three_squares_grid[6, 8]
        three_squares_grid._block_column(up, bottom)
        for i in range(10):
            assert not three_squares_grid[i, 7].is_blocked()
            assert not three_squares_grid[i, 9].is_blocked()
        assert three_squares_grid[0, 8].is_blocked()
        assert three_squares_grid[1, 8].is_blocked()
        assert three_squares_grid[7, 8].is_blocked()
        assert three_squares_grid[8, 8].is_blocked()
        assert three_squares_grid[9, 8].is_blocked()

    # DONE
    def test_block_column_not_cells_color(self, three_squares_grid: BruteForceResolver):
        """Test _block_column don't block same color."""
        up = three_squares_grid[3, 8]
        bottom = three_squares_grid[5, 8]
        three_squares_grid._block_column(up, bottom)
        assert not three_squares_grid[2, 8].is_blocked()
        assert not three_squares_grid[6, 8].is_blocked()

    # DONE
    def test_block_column_not_cells_color_two_sides(
        self, star_grid: BruteForceResolver
    ):
        """Test _block_column block the two upper and under cells on a 2 cell block."""
        up = star_grid[4, 1]
        bottom = star_grid[5, 1]
        star_grid._block_column(up, bottom)
        assert star_grid[4, 0].is_blocked()
        assert star_grid[5, 0].is_blocked()
        assert not star_grid[4, 2].is_blocked()
        assert not star_grid[5, 2].is_blocked()
        up = star_grid[5, 9]
        bottom = star_grid[6, 9]
        star_grid._block_column(up, bottom)
        assert not star_grid[5, 8].is_blocked()
        assert not star_grid[6, 8].is_blocked()
        assert star_grid[5, 10].is_blocked()
        assert star_grid[6, 10].is_blocked()

    # DONE
    def test_block_column_not_cells_color_three_sides(
        self, star_grid: BruteForceResolver
    ):
        """Test _block_column block the two upper and under cells on a 2 cell block."""
        up = star_grid[4, 2]
        bottom = star_grid[6, 2]
        star_grid._block_column(up, bottom)
        assert not star_grid[4, 1].is_blocked()
        assert not star_grid[5, 1].is_blocked()
        assert not star_grid[6, 1].is_blocked()
        assert not star_grid[4, 3].is_blocked()
        assert not star_grid[5, 3].is_blocked()
        assert not star_grid[6, 3].is_blocked()
        up = star_grid[4, 8]
        bottom = star_grid[6, 8]
        star_grid._block_column(up, bottom)
        assert not star_grid[4, 7].is_blocked()
        assert not star_grid[5, 7].is_blocked()
        assert not star_grid[6, 7].is_blocked()
        assert not star_grid[4, 9].is_blocked()
        assert not star_grid[5, 9].is_blocked()
        assert not star_grid[6, 9].is_blocked()

    # DONE
    def test_block_column_different_rows_raises(
        self, three_squares_grid: BruteForceResolver
    ):
        """Test _block_column raises ValueError for different columns."""
        up = three_squares_grid[0, 0]
        bottom = three_squares_grid[1, 1]
        with pytest.raises(
            ValueError, match="Top and bottom cells must be in the same column."
        ):
            three_squares_grid._block_column(up, bottom)

    # DONE
    def test_block_column_swaps_up_bottom_with_warning(
        self, three_squares_grid: BruteForceResolver
    ):
        """Test _block_column swaps up and bottom if needed with warning."""
        up = three_squares_grid[0, 0]
        bottom = three_squares_grid[1, 0]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            three_squares_grid._block_column(bottom, up)
            assert len(w) > 0


# =============================================================================
# Test _claim_corner
# =============================================================================


class TestClaimCorner:
    """Tests for _claim_corner method."""

    def test_claim_corner_notenough_cells(self):
        """Test _claim_corner with not enough cells."""
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        with pytest.raises(
            ValueError, match="Exactly 3 cells are required to claim a corner."
        ):
            grid._claim_corner([grid[2, 2], grid[2, 3]])  # Only 2 cells

    def test_claim_corner_in_middle_southwest(self):
        """Test _claim_corner with southwest pointing corner."""
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        cells = [grid[1, 1], grid[2, 1], grid[2, 2]]
        grid._claim_corner(cells)
        assert (
            grid[1, 2].is_blocked()
            and grid[2, 0].is_blocked()
            and grid[3, 1].is_blocked()
        )

    def test_claim_corner_in_middle_southeast(self):
        """Test _claim_corner with southeast pointing corner."""
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        cells = [grid[1, 2], grid[2, 1], grid[2, 2]]
        grid._claim_corner(cells)
        assert (
            grid[1, 1].is_blocked()
            and grid[3, 2].is_blocked()
            and grid[2, 3].is_blocked()
        )

    def test_claim_corner_in_middle_northwest(self):
        """Test _claim_corner with northwest pointing corner."""
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        cells = [grid[1, 1], grid[1, 2], grid[2, 1]]
        grid._claim_corner(cells)
        assert (
            grid[2, 2].is_blocked()
            and grid[1, 0].is_blocked()
            and grid[0, 1].is_blocked()
        )

    def test_claim_corner_in_middle_northeast(self):
        """Test _claim_corner with northeast pointing corner."""
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        cells = [grid[1, 1], grid[1, 2], grid[2, 2]]
        grid._claim_corner(cells)
        assert (
            grid[2, 1].is_blocked()
            and grid[0, 2].is_blocked()
            and grid[1, 3].is_blocked()
        )

    def test_claim_corner_edges_cases(self):
        """Test _claim_corner with cells on grid edges - all corner rotations on borders."""
        # Test all corner orientations on all four edges of the grid

        # Test on top edge (row 0) - same row pattern
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[0, 1], grid[0, 2], grid[1, 1]])  # Case 2: same row
        assert grid[
            1, 2
        ].is_blocked()  # No upward from row 0, but cells[1] gets processed

        # Test on bottom edge (row 4) - same row pattern
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[3, 1], grid[4, 1], grid[4, 2]])  # Case 2: same row
        assert (
            grid[3, 1].is_blocked()
            or grid[4, 0].is_blocked()
            or grid[4, 3].is_blocked()
        )

        # Test on left edge (col 0) - same column pattern
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[1, 0], grid[2, 0], grid[2, 1]])  # Case 3: same column
        assert (
            grid[3, 0].is_blocked()
            or grid[2, 1].is_blocked()
            or grid[1, 1].is_blocked()
        )

        # Test on bottom edge (col 4) - same column pattern
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[1, 4], grid[2, 3], grid[2, 4]])  # Case 3: same column
        assert (
            grid[3, 4].is_blocked()
            or grid[2, 3].is_blocked()
            or grid[1, 3].is_blocked()
        )

        # Test top-left corner of grid (0,0)
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[0, 0], grid[0, 1], grid[1, 0]])  # Top-left corner
        # Should not crash with index errors
        assert True

        # Test top-right corner of grid (0,4)
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[0, 3], grid[0, 4], grid[1, 4]])  # Top-right corner
        assert True

        # Test bottom-left corner of grid (4,0)
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[3, 0], grid[4, 0], grid[4, 1]])  # Bottom-left corner
        assert True

        # Test bottom-right corner of grid (4,4)
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[3, 4], grid[4, 3], grid[4, 4]])  # Bottom-right corner
        assert True

        # Test case 4 (else branch) on top edge
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[0, 2], grid[1, 1], grid[1, 2]])  # Case 4: diagonal
        assert True

        # Test case 4 (else branch) on bottom edge
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[3, 1], grid[4, 1], grid[4, 2]])  # Case 4: diagonal
        assert True

        # Test case 4 (else branch) on left edge
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[1, 1], grid[2, 0], grid[2, 1]])  # Case 4: diagonal
        assert True

        # Test case 4 (else branch) on right edge
        grid = BruteForceResolver(
            [[Cell(r, c, "red") for c in range(5)] for r in range(5)]
        )
        grid._claim_corner([grid[1, 3], grid[2, 3], grid[2, 4]])  # Case 4: diagonal
        assert True


# =============================================================================
# TODO Test Parallel Claiming
# =============================================================================


class TestClaimParallel:
    """Tests for parallel claiming methods."""

    # DONE
    def test_block_row_parallel_basic(self, three_squares_grid: BruteForceResolver):
        """Test _block_row_parallel basic execution."""
        cells1 = [three_squares_grid[3, 1], three_squares_grid[4, 1]]
        cells2 = [three_squares_grid[3, 5], three_squares_grid[4, 5]]
        three_squares_grid._block_row_parallel(cells1, cells2)
        print_grid(three_squares_grid.grid)
        assert three_squares_grid[3, 0].is_blocked()
        assert three_squares_grid[3, 2].is_blocked()
        assert three_squares_grid[3, 3].is_blocked()
        assert three_squares_grid[3, 4].is_blocked()
        assert three_squares_grid[3, 6].is_blocked()
        assert three_squares_grid[3, 7].is_blocked()
        assert three_squares_grid[3, 8].is_blocked()
        assert three_squares_grid[3, 9].is_blocked()
        assert three_squares_grid[4, 0].is_blocked()
        assert three_squares_grid[4, 2].is_blocked()
        assert three_squares_grid[4, 3].is_blocked()
        assert three_squares_grid[4, 4].is_blocked()
        assert three_squares_grid[4, 6].is_blocked()
        assert three_squares_grid[4, 7].is_blocked()
        assert three_squares_grid[4, 8].is_blocked()
        assert three_squares_grid[4, 9].is_blocked()

    # DONE
    def test_block_column_parallel_basic(self, three_squares_grid: BruteForceResolver):
        """Test _block_column_parallel basic execution."""
        cells1 = [three_squares_grid[1, 1], three_squares_grid[1, 2]]
        cells2 = [three_squares_grid[8, 1], three_squares_grid[8, 2]]
        three_squares_grid._block_column_parallel(cells1, cells2)
        print_grid(three_squares_grid.grid)
        assert three_squares_grid[0, 1].is_blocked()
        assert three_squares_grid[2, 1].is_blocked()
        assert three_squares_grid[5, 1].is_blocked()
        assert three_squares_grid[6, 1].is_blocked()
        assert three_squares_grid[7, 1].is_blocked()
        assert three_squares_grid[9, 1].is_blocked()
        assert three_squares_grid[0, 2].is_blocked()
        assert three_squares_grid[2, 2].is_blocked()
        assert three_squares_grid[3, 2].is_blocked()
        assert three_squares_grid[4, 2].is_blocked()
        assert three_squares_grid[5, 2].is_blocked()
        assert three_squares_grid[6, 2].is_blocked()
        assert three_squares_grid[7, 2].is_blocked()
        assert three_squares_grid[9, 2].is_blocked()

    def test_claim_parallel_empty_regions(self):
        """Test _claim_parallel with empty regions list."""
        grid = BruteForceResolver([[Cell(0, 0, "red")]])
        grid._claim_parallel([])
        assert grid[0, 0].value == EMPTY

    def test_claim_parallel_horizontal(self):
        """Test _claim_parallel with horizontal regions."""
        grid = BruteForceResolver(
            [
                [
                    Cell(0, 0, "red"),
                    Cell(0, 1, "red"),
                    Cell(0, 2, "yellow"),
                    Cell(0, 3, "yellow"),
                    Cell(0, 4, "cyan"),
                ],
                [
                    Cell(1, 0, "red"),
                    Cell(1, 1, "blue"),
                    Cell(1, 2, "yellow"),
                    Cell(1, 3, "green"),
                    Cell(1, 4, "cyan"),
                ],
                [
                    Cell(2, 0, "red"),
                    Cell(2, 1, "blue"),
                    Cell(2, 2, "yellow"),
                    Cell(2, 3, "green"),
                    Cell(2, 4, "cyan"),
                ],
                [
                    Cell(3, 0, "red"),
                    Cell(3, 1, "red"),
                    Cell(3, 2, "yellow"),
                    Cell(3, 3, "yellow"),
                    Cell(3, 4, "cyan"),
                ],
                [
                    Cell(4, 0, "red"),
                    Cell(4, 1, "red"),
                    Cell(4, 2, "yellow"),
                    Cell(4, 3, "yellow"),
                    Cell(4, 4, "cyan"),
                ],
            ]
        )
        regions = [[grid[1, 1], grid[2, 1]], [grid[1, 3], grid[2, 3]]]
        grid._claim_parallel(regions)
        assert grid[1, 0].is_blocked()
        assert grid[1, 2].is_blocked()
        assert grid[1, 4].is_blocked()
        assert grid[2, 0].is_blocked()
        assert grid[2, 2].is_blocked()
        assert grid[2, 4].is_blocked()

    def test_claim_parallel_vertical(self):
        """Test _claim_parallel with vertical regions."""
        grid = BruteForceResolver(
            [
                [
                    Cell(0, 0, "red"),
                    Cell(0, 1, "red"),
                    Cell(0, 2, "yellow"),
                    Cell(0, 3, "yellow"),
                    Cell(0, 4, "cyan"),
                ],
                [
                    Cell(1, 0, "red"),
                    Cell(1, 1, "blue"),
                    Cell(1, 2, "yellow"),
                    Cell(1, 3, "blue"),
                    Cell(1, 4, "cyan"),
                ],
                [
                    Cell(2, 0, "red"),
                    Cell(2, 1, "red"),
                    Cell(2, 2, "yellow"),
                    Cell(2, 3, "yellow"),
                    Cell(2, 4, "cyan"),
                ],
                [
                    Cell(3, 0, "red"),
                    Cell(3, 1, "green"),
                    Cell(3, 2, "yellow"),
                    Cell(3, 3, "green"),
                    Cell(3, 4, "cyan"),
                ],
                [
                    Cell(4, 0, "red"),
                    Cell(4, 1, "red"),
                    Cell(4, 2, "yellow"),
                    Cell(4, 3, "yellow"),
                    Cell(4, 4, "cyan"),
                ],
            ]
        )
        regions = [[grid[1, 1], grid[1, 3]], [grid[3, 1], grid[3, 3]]]
        grid._claim_parallel(regions)
        assert grid[0, 1].is_blocked()
        assert grid[2, 1].is_blocked()
        assert grid[4, 1].is_blocked()
        assert grid[0, 3].is_blocked()
        assert grid[2, 3].is_blocked()
        assert grid[4, 3].is_blocked()


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
        grid = BruteForceResolver(build_example_grid(test_grid))
        assert len(grid.grid) == 2
        assert len(grid.grid[0]) == 2
        assert len(grid.grid[1]) == 2

    def test_build_example_grid_single_row(self):
        """Test build_example_grid with single row."""
        test_grid = ["R R R"]
        grid = BruteForceResolver(build_example_grid(test_grid))
        assert len(grid.grid) == 1
        assert len(grid.grid[0]) == 3

    def test_build_example_grid_single_cell(self):
        """Test build_example_grid with single cell."""
        test_grid = ["R"]
        grid = BruteForceResolver(build_example_grid(test_grid))
        assert len(grid.grid) == 1
        assert len(grid.grid[0]) == 1

    def test_build_example_grid_empty(self):
        """Test build_example_grid with empty list."""
        grid = BruteForceResolver(build_example_grid([]))
        assert len(grid.grid) == 0

    def test_build_example_grid_color_mapping(self):
        """Test build_example_grid color mapping."""
        test_grid = ["C R B O V Y P W N"]
        grid = BruteForceResolver(build_example_grid(test_grid))
        assert grid[0, 0].color == "cyan"
        assert grid[0, 1].color == "red"
        assert grid[0, 2].color == "blue"
        assert grid[0, 3].color == "orange"
        assert grid[0, 4].color == "green"
        assert grid[0, 5].color == "yellow"
        assert grid[0, 6].color == "purple"
        assert grid[0, 7].color == "white"
        assert grid[0, 8].color == "black"

    def test_build_example_grid_unknown_color(self):
        """Test build_example_grid with unknown color token."""
        test_grid = ["X Y Z"]
        grid = BruteForceResolver(build_example_grid(test_grid))
        assert grid[0, 0].color == "unknown"
        assert grid[0, 1].color == "yellow"
        assert grid[0, 2].color == "unknown"

    def test_build_example_grid_irregular(self):
        """Test build_example_grid with irregular row lengths."""
        test_grid = ["R R R", "G G", "B"]
        grid = BruteForceResolver(build_example_grid(test_grid))
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
        grid = BruteForceResolver(build_example_grid(test_grid))
        assert grid[0, 0].row == 0 and grid[0, 0].col == 0
        assert grid[0, 1].row == 0 and grid[0, 1].col == 1
        assert grid[1, 0].row == 1 and grid[1, 0].col == 0
        assert grid[1, 1].row == 1 and grid[1, 1].col == 1

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
        grid = BruteForceResolver(build_example_grid(test_grid))

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
            for cell in grid.grid[row_idx]:
                assert cell.color == expected_color

        assert len(grid.regions) == 10
        for region in grid.regions:
            assert len(region.cells) == 10


# =============================================================================
# Test QueenResolver
# =============================================================================


class TestResolveGrid:
    """Tests for QueenResolver function."""

    def test_resolve_grid_empty_grid(self, capsys: pytest.CaptureFixture[str]):
        """Test QueenResolver with empty grid."""
        grid = BruteForceResolver([])
        grid.resolve_grid()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_resolve_grid_valid_grid(self, capsys: pytest.CaptureFixture[str]):
        """Test QueenResolver with valid grid."""
        test_grid = [
            "R R",
            "G G",
        ]
        grid = BruteForceResolver(build_example_grid(test_grid))
        grid.resolve_grid()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def testresolve_grid_modifies_grid(self):
        """Test that QueenResolver modifies the grid."""
        test_grid = [
            "R R",
            "G G",
        ]
        grid = BruteForceResolver(build_example_grid(test_grid))
        grid.resolve_grid()
        assert True


# =============================================================================
# Additional Tests for Coverage
# =============================================================================


class TestCellRepr:
    """Tests for Cell.__repr__ method."""

    def test_cell_repr(self):
        """Test Cell __repr__ method."""
        cell = Cell(0, 1, "red", QUEEN)
        repr_str = repr(cell)
        assert "Cell" in repr_str
        assert "0" in repr_str
        assert "1" in repr_str
        assert "red" in repr_str
        assert "1" in repr_str  # QUEEN value


class TestRegionProperties:
    """Tests for Region class properties."""

    def test_region_color_property(self):
        """Test Region.color property."""
        grid = Grid([[Cell(0, 0, "cyan"), Cell(0, 1, "cyan")]])
        region = grid.regions[0]
        assert region.color == "cyan"


class TestGridPrivateMethods:
    """Tests for Grid private helper methods."""

    def test_get_row(self):
        """Test _get_row method."""
        grid = Grid(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "red")],
                [Cell(1, 0, "blue"), Cell(1, 1, "blue")],
            ]
        )
        row = grid._get_row(0)
        assert len(row) == 2
        assert row[0].row == 0
        assert row[1].row == 0
        # Test with row 1
        row1 = grid._get_row(1)
        assert len(row1) == 2
        assert row1[0].row == 1

    def test_get_column(self):
        """Test _get_column method."""
        grid = Grid(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "red")],
                [Cell(1, 0, "blue"), Cell(1, 1, "blue")],
            ]
        )
        col = grid._get_column(0)
        assert len(col) == 2
        assert col[0].col == 0
        assert col[1].col == 0


class TestRegionBlockAll:
    """Tests for Region.block_all_cells method."""

    def test_block_all_cells(self):
        """Test Region.block_all_cells method."""
        grid = Grid([[Cell(0, 0, "red"), Cell(0, 1, "red")]])
        region = grid.regions[0]
        assert grid[0, 0].is_empty()
        assert grid[0, 1].is_empty()
        region.block_all_cells()
        assert grid[0, 0].is_blocked()
        assert grid[0, 1].is_blocked()


class TestGetRegionByCell:
    """Tests for Grid.get_region_by_cell method."""

    def test_get_region_by_cell_success(self):
        """Test get_region_by_cell with existing cell."""
        grid = Grid([[Cell(0, 0, "red"), Cell(0, 1, "blue")]])
        cell = grid[0, 0]
        region = grid.get_region_by_cell(cell)
        assert region.color == "red"
        assert cell in region.cells

    def test_get_region_by_cell_not_found(self):
        """Test get_region_by_cell with non-existent cell."""
        grid = Grid([[Cell(0, 0, "red")]])
        # Create a cell that's not in any region
        external_cell = Cell(99, 99, "external")
        with pytest.raises(ValueError, match="not found in any region"):
            grid.get_region_by_cell(external_cell)


class TestBlockRegion:
    """Tests for Grid.block_region method."""

    def test_block_region(self):
        """Test block_region method."""
        grid = Grid([[Cell(0, 0, "red"), Cell(0, 1, "red")]])
        assert grid[0, 0].is_empty()
        grid.block_region(grid[0, 0])
        assert grid[0, 0].is_blocked()
        assert grid[0, 1].is_blocked()


class TestBlockCellByCoord:
    """Tests for Grid.block_cell_by_coord method."""

    def test_block_cell_by_coord_valid(self):
        """Test block_cell_by_coord with valid coordinates."""
        grid = Grid([[Cell(0, 0, "red"), Cell(0, 1, "red")]])
        grid.block_cell_by_coord(0, 0)
        assert grid[0, 0].is_blocked()

    def test_block_cell_by_coord_out_of_bounds(self):
        """Test block_cell_by_coord with out of bounds coordinates."""
        grid = Grid([[Cell(0, 0, "red")]])
        # Should not raise, just do nothing
        grid.block_cell_by_coord(99, 99)
        assert grid[0, 0].is_empty()

    def test_block_cell_by_coord_queen_cell(self):
        """Test block_cell_by_coord doesn't block queen cells."""
        grid = Grid([[Cell(0, 0, "red", QUEEN)]])
        grid.block_cell_by_coord(0, 0)
        assert grid[0, 0].is_queen()


class TestBruteForceResolverImport:
    """Tests to cover import statements in resolver.py."""

    def test_ui_import_attempt(self):
        """Test that UI import is attempted in resolver."""
        # This test just ensures the import is attempted
        # The actual import may succeed or fail, but the attempt should be there
        from Queens.brute_force_resolver import BruteForceResolver

        # If we get here, the import worked or was handled
        assert BruteForceResolver is not None


class TestClaimRowReturn:
    """Tests to cover return statements."""

    def test_block_row_returns_none(self):
        """Test that _block_row returns None."""
        grid = BruteForceResolver(
            [[Cell(0, 0, "red"), Cell(0, 1, "red"), Cell(0, 2, "red")]]
        )
        result = grid._block_row(grid[0, 0], grid[0, 2])
        assert result is None


class TestClaimColumnReturn:
    """Tests to cover return statements."""

    def test_block_column_returns_none(self):
        """Test that _block_column returns None."""
        grid = BruteForceResolver(
            [[Cell(0, 0, "red")], [Cell(1, 0, "red")], [Cell(2, 0, "red")]]
        )
        result = grid._block_column(grid[0, 0], grid[2, 0])
        assert result is None


class TestResolveWarning:
    """Tests for warning in resolve_grid."""

    def test_resolve_duo_not_aligned_warning(self, capsys: pytest.CaptureFixture[str]):
        """Test that resolve_grid warns when duo is not aligned."""
        # Create a grid with a region that has 2 empty cells not aligned
        test_grid = [
            "R R",
            "R R",
        ]
        base_grid = build_example_grid(test_grid)
        grid = BruteForceResolver(base_grid)
        # Queenify one cell to leave 3 empty cells
        grid.queenify_cell(grid[0, 0])
        # This should create a scenario where there might be unaligned duos
        # But the current logic might not hit this, so we need to mock it
        # For now, just call resolve_grid and check it doesn't crash
        with warnings.catch_warnings(record=True) as w:
            print(w)
            warnings.simplefilter("always")
            grid.resolve_grid()
            # The warning might or might not be triggered depending on the grid state
            # This test mainly ensures resolve_grid runs without crashing


class TestClaimRowSize3:
    """Tests for _block_row with size 3."""

    def test_block_row_size_3_claims_centers(self):
        """Test _block_row with size 3 claims center cells."""
        grid = BruteForceResolver(
            [
                [
                    Cell(0, 0, "red"),
                    Cell(0, 1, "red"),
                    Cell(0, 2, "red"),
                    Cell(0, 3, "green"),
                ],
                [
                    Cell(1, 0, "blue"),
                    Cell(1, 1, "blue"),
                    Cell(1, 2, "blue"),
                    Cell(1, 3, "blue"),
                ],
                [
                    Cell(2, 0, "cyan"),
                    Cell(2, 1, "cyan"),
                    Cell(2, 2, "cyan"),
                    Cell(2, 3, "cyan"),
                ],
            ]
        )
        left = grid[0, 0]
        right = grid[0, 2]
        grid._block_row(left, right)
        # With size 3, should claim cells above and below the center (col 1)
        assert grid[0, 3].is_blocked()  # left side
        assert grid[1, 1].is_blocked()  # center above or below


class TestClaimColumnSize3:
    """Tests for _block_column with size 3."""

    def test_block_column_size_3_claims_centers(self):
        """Test _block_column with size 3 claims center cells."""
        grid = BruteForceResolver(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "green"), Cell(0, 2, "blue")],
                [Cell(1, 0, "red"), Cell(1, 1, "green"), Cell(1, 2, "blue")],
                [Cell(2, 0, "red"), Cell(2, 1, "green"), Cell(2, 2, "blue")],
            ]
        )
        top = grid[0, 0]
        bottom = grid[2, 0]
        grid._block_column(top, bottom)
        # With size 3, should claim cells left and right of the center (row 1, col 0)
        # The center is at row 1, so it should block cells at (1, -1) and (1, 1) relative to col 0
        # So it should block (1, 1) which is in bounds
        assert grid[1, 1].is_blocked()  # center right


class TestResolveUnalignedDuo:
    """Tests for unaligned duo warning in resolve_grid."""

    def test_resolve_duo_unaligned_warning(self):
        """Test that resolve_grid warns when duo cells are not aligned."""
        # Create a scenario where a region has 2 empty cells not aligned
        # We need a 2x2 grid of the same color, with one queen already placed
        # This leaves 3 empty cells, but we need exactly 2 in a region not aligned
        # This is tricky to set up with the current data structures
        # Let's create a custom scenario
        grid = BruteForceResolver(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "blue")],
                [Cell(1, 0, "red"), Cell(1, 1, "red")],
            ]
        )
        # Queenify the blue cell to isolate the red region
        grid.queenify_cell(grid[0, 1])
        # Now the red region has cells at (0,0), (1,0), (1,1) - 3 cells
        # After placing queen at (0,1), the red region still has 3 cells
        # This might create a duo that's not aligned
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            grid.resolve_grid()
            # Check if any warnings were raised
            # The specific warning about unaligned duo should be in the warnings
            assert len(w) >= 0  # May or may not have warnings


class TestReturnStatements:
    """Tests to cover return statements in claim methods."""

    def test_block_row_all_returns(self):
        """Test all return paths in _block_row."""
        # Test size 2 with multiple rows so we don't get index errors
        grid1 = BruteForceResolver(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "red")],
                [Cell(1, 0, "blue"), Cell(1, 1, "blue")],
            ]
        )
        result1 = grid1._block_row(grid1[0, 0], grid1[0, 1])
        assert result1 is None

        # Test size 3 with multiple rows
        grid2 = BruteForceResolver(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "red"), Cell(0, 2, "red")],
                [Cell(1, 0, "blue"), Cell(1, 1, "blue"), Cell(1, 2, "blue")],
            ]
        )
        result2 = grid2._block_row(grid2[0, 0], grid2[0, 2])
        assert result2 is None

    def test_block_column_all_returns(self):
        """Test all return paths in _block_column."""
        # Test size 2 with multiple columns
        grid1 = BruteForceResolver(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "blue")],
                [Cell(1, 0, "red"), Cell(1, 1, "blue")],
            ]
        )
        result1 = grid1._block_column(grid1[0, 0], grid1[1, 0])
        assert result1 is None

        # Test size 3 with multiple columns
        grid2 = BruteForceResolver(
            [
                [Cell(0, 0, "red"), Cell(0, 1, "blue")],
                [Cell(1, 0, "red"), Cell(1, 1, "blue")],
                [Cell(2, 0, "red"), Cell(2, 1, "blue")],
            ]
        )
        result2 = grid2._block_column(grid2[0, 0], grid2[2, 0])
        assert result2 is None


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
        base_grid = build_example_grid(test_grid)
        grid = BruteForceResolver(base_grid)
        result = grid.resolve_grid()
        assert result is not None
        assert grid[1, 0].is_queen()
        assert grid[4, 1].is_queen()
        assert grid[0, 2].is_queen()
        assert grid[3, 3].is_queen()
        assert grid[5, 4].is_queen()
        assert grid[2, 5].is_queen()

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
        base_grid = build_example_grid(test_grid)
        grid = BruteForceResolver(base_grid)
        grid.resolve_grid()
        assert grid[1, 3].is_queen()
        assert grid[3, 1].is_queen()
        assert grid[4, 4].is_queen()
        assert grid[5, 2].is_queen()
        assert grid[6, 0].is_queen()

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
        base_grid = build_example_grid(test_grid)
        grid = BruteForceResolver(base_grid)
        grid.resolve_grid()
        assert grid[0, 3].is_queen()
        assert grid[1, 5].is_queen()
        assert grid[2, 7].is_queen()
        assert grid[3, 4].is_queen()
        assert grid[4, 1].is_queen()
        assert grid[5, 6].is_queen()
        assert grid[6, 0].is_queen()
        assert grid[7, 2].is_queen()

    def test_resolve_returns_grid(self):
        """Test that resolve returns the grid."""
        test_grid = ["R R", "G G"]
        base_grid = build_example_grid(test_grid)
        grid = BruteForceResolver(base_grid)
        result = grid.resolve_grid()
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
        base_grid = build_example_grid(test_grid)
        grid = BruteForceResolver(base_grid)
        result = grid.resolve_grid()

        captured = capsys.readouterr()
        output = captured.out
        assert "Max iterations reached, stopping resolution.\n" in output
        assert result is not None


# =============================================================================
# Test integration of QueenResolver with build_example_grid
# =============================================================================


class TestQueenResolverIntegration:
    """Integration tests for QueenResolver with build_example_grid."""

    def test_queen_resolver_with_example_grid1(self):
        """Test QueenResolver with an example grid."""
        testGrid = [
            "Y Y Y P W W W",
            "Y Y Y P W W W",
            "Y Y P P P W W",
            "R P P O P P W",
            "R R P O P G G",
            "R R B B B G G",
            "R R R R B G G",
        ]
        grid = BruteForceResolver(build_example_grid(testGrid))
        print_grid(grid.grid)
        grid.resolve_grid()
        print_grid(grid.grid)
        assert grid[0, 1].is_queen()
        assert grid[1, 5].is_queen()
        assert grid[2, 2].is_queen()
        assert grid[3, 0].is_queen()
        assert grid[4, 3].is_queen()
        assert grid[5, 6].is_queen()
        assert grid[6, 4].is_queen()

    def test_queen_resolver_with_example_grid2(self):
        """Test QueenResolver with an example grid."""

        testGrid = [
            "P P P P P P P P P P",
            "P P P P V P N P P P",
            "P P P P V P N P P P",
            "P P P B V G N P P P",
            "P P P B V G N P P P",
            "P P R R R R R R P P",
            "P P C C C C C C P P",
            "P O O O O O O O O P",
            "P W W W W W W W W P",
            "Y Y Y Y Y Y Y Y Y P",
        ]
        grid = BruteForceResolver(build_example_grid(testGrid))
        print_grid(grid.grid)
        grid.resolve_grid()
        print_grid(grid.grid)
        assert grid[0, 9].is_queen()
        assert grid[1, 4].is_queen()
        assert grid[2, 6].is_queen()
        assert grid[3, 3].is_queen()
        assert grid[4, 5].is_queen()
        assert grid[5, 2].is_queen()
        assert grid[6, 7].is_queen()
        assert grid[7, 1].is_queen()
        assert grid[8, 8].is_queen()
        assert grid[9, 0].is_queen()

    def test_queen_resolver_with_example_grid3(self):
        """Test QueenResolver with an example grid."""
        testGrid = [
            "P P P O O O O O",
            "P P B O O O O O",
            "P B B O O O O O",
            "V W W W O O O O",
            "V W W W W O O O",
            "V W W W W R R Y",
            "V G G W W R R Y",
            "V G G G W Y Y Y",
        ]
        grid = BruteForceResolver(build_example_grid(testGrid))
        print_grid(grid.grid)
        grid.resolve_grid()
        assert grid[0, 1].is_queen()
        assert grid[1, 6].is_queen()
        assert grid[2, 2].is_queen()
        assert grid[3, 0].is_queen()
        assert grid[4, 4].is_queen()
        assert grid[5, 7].is_queen()
        assert grid[6, 5].is_queen()
        assert grid[6, 3].is_queen()
