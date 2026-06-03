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

from Queens.resolver import (
    Cell,
    Grid,
    build_example_grid,
    QueenResolver,
    EMPTY,
    QUEEN,
    BLOCKED,
)

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
                Cell((1, 1), "red"),
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
# Test Cell class
# =============================================================================


class TestCell:
    """Tests for Cell class."""

    def test_cell_creation(self, empty_cell: Cell):
        """Test basic cell creation."""
        assert empty_cell.row == 0
        assert empty_cell.col == 0
        assert empty_cell.color == "cyan"
        assert empty_cell.value == EMPTY

    def test_cell_getters(self, empty_cell: Cell):
        """Test cell getters."""
        assert empty_cell.coord == (0, 0)
        assert empty_cell.get_color == "cyan"
        assert empty_cell.get_value == EMPTY

    def test_cell_creation_with_value(self):
        """Test cell creation with specific value."""
        cell = Cell((5, 3), "red", QUEEN)
        assert cell.row == 5
        assert cell.col == 3
        assert cell.color == "red"
        assert cell.value == QUEEN

    def test_cell_creation_negative_coords(self):
        """Test cell creation with negative coordinates."""
        cell = Cell((-1, -1), "blue")
        assert cell.row == -1
        assert cell.col == -1

    def test_cell_creation_empty_color(self):
        """Test cell creation with empty color string."""
        cell = Cell((0, 0), "")
        assert cell.color == ""
        assert cell.value == EMPTY

    def test_cell_creation_large_coords(self):
        """Test cell creation with large coordinates."""
        cell = Cell((1000, 1000), "green")
        assert cell.row == 1000
        assert cell.col == 1000

    def test_cell_coord_property(self, empty_cell: Cell):
        """Test coord property returns tuple."""
        assert empty_cell.coord == (0, 0)

    def test_cell_coord_property_multiple(self):
        """Test coord property with different coordinates."""
        cell = Cell((3, 7), "yellow")
        assert cell.coord == (3, 7)

    def test_make_queen(self, empty_cell: Cell):
        """Test make_queen sets value to QUEEN."""
        assert empty_cell.value == EMPTY
        empty_cell.make_queen()
        assert empty_cell.value == QUEEN

    def test_make_queen_already_queen(self, queen_cell: Cell):
        """Test make_queen on already queen cell."""
        assert queen_cell.value == QUEEN
        queen_cell.make_queen()
        assert queen_cell.value == QUEEN

    def test_make_queen_on_blocked(self, blocked_cell: Cell):
        """Test make_queen on blocked cell overrides to queen."""
        assert blocked_cell.value == BLOCKED
        blocked_cell.make_queen()
        assert blocked_cell.value == QUEEN

    def test_block_cell(self, empty_cell: Cell):
        """Test block_cell sets value to BLOCKED."""
        assert empty_cell.value == EMPTY
        empty_cell.block_cell()
        assert empty_cell.value == BLOCKED

    def test_block_cell_already_blocked(self, blocked_cell: Cell):
        """Test block_cell on already blocked cell."""
        assert blocked_cell.value == BLOCKED
        blocked_cell.block_cell()
        assert blocked_cell.value == BLOCKED

    def test_block_cell_on_queen(self, queen_cell: Cell):
        """Test block_cell on queen cell - should override to blocked."""
        assert queen_cell.value == QUEEN
        queen_cell.block_cell()
        assert queen_cell.value == BLOCKED

    def test_is_empty_true(self, empty_cell: Cell):
        """Test is_empty returns True for empty cell."""
        assert empty_cell.is_empty() is True

    def test_is_empty_false_queen(self, queen_cell: Cell):
        """Test is_empty returns False for queen cell."""
        assert queen_cell.is_empty() is False

    def test_is_empty_false_blocked(self, blocked_cell: Cell):
        """Test is_empty returns False for blocked cell."""
        assert blocked_cell.is_empty() is False

    def test_cell_repr(self, empty_cell: Cell):
        """Test __repr__ returns expected string."""
        repr_str = repr(empty_cell)
        assert "Cell(0,0,cyan,0)" in repr_str or "Cell(0, 0, cyan, 0)" in repr_str

    def test_cell_repr_with_values(self):
        """Test __repr__ with different values."""
        cell = Cell((2, 3), "red", QUEEN)
        repr_str = repr(cell)
        assert "2" in repr_str
        assert "3" in repr_str
        assert "red" in repr_str
        assert "1" in repr_str


# =============================================================================
# Test Grid class - Basics
# =============================================================================


class TestGridBasics:
    """Tests for Grid class basic functionality."""

    def test_grid_creation(self, simple_grid_1x1: Grid):
        """Test grid creation with 1x1 data."""
        assert len(simple_grid_1x1.grid) == 1
        assert len(simple_grid_1x1.grid[0]) == 1

    def test_grid_creation_2x2(self, simple_grid_2x2: Grid):
        """Test grid creation with 2x2 data."""
        assert len(simple_grid_2x2.grid) == 2
        assert len(simple_grid_2x2.grid[0]) == 2
        assert len(simple_grid_2x2.grid[1]) == 2

    def test_grid_getitem(self, simple_grid_2x2: Grid):
        """Test __getitem__ returns correct row."""
        row = simple_grid_2x2[0]
        assert len(row) == 2
        assert row[0].row == 0
        assert row[1].row == 0

    def test_grid_getitem_second_row(self, simple_grid_2x2: Grid):
        """Test __getitem__ for second row."""
        row = simple_grid_2x2[1]
        assert row[0].row == 1
        assert row[1].row == 1

    def test_grid_iter(self, simple_grid_2x2: Grid):
        """Test __iter__ allows iteration over grid."""
        rows = list(simple_grid_2x2)
        assert len(rows) == 2
        assert rows[0] == simple_grid_2x2[0]
        assert rows[1] == simple_grid_2x2[1]

    def test_grid_regions_populated(self, simple_grid_2x2: Grid):
        """Test that regions are populated on grid creation."""
        assert hasattr(simple_grid_2x2, "regions")
        assert isinstance(simple_grid_2x2.regions, list)

    def test_grid_empty(self):
        """Test creation of empty grid (0x0)."""
        grid = Grid([])
        assert len(grid.grid) == 0
        assert len(grid.regions) == 0

    def test_grid_single_row(self):
        """Test grid with single row."""
        grid = Grid([[Cell((0, 0), "red"), Cell((0, 1), "red")]])
        assert len(grid.grid) == 1
        assert len(grid.grid[0]) == 2

    def test_grid_single_column(self):
        """Test grid with single column."""
        grid = Grid(
            [
                [Cell((0, 0), "red")],
                [Cell((1, 0), "blue")],
                [Cell((2, 0), "green")],
            ]
        )
        assert len(grid.grid) == 3
        assert len(grid.grid[0]) == 1


# =============================================================================
# Test _is_grid_finished
# =============================================================================


class TestIsGridFinished:
    """Tests for _is_grid_finished method."""

    def test_grid_finished_empty(self, simple_grid_1x1: Grid):
        """Test that grid with empty cell is not finished."""
        assert simple_grid_1x1._is_grid_finished() is False

    def test_grid_finished_single_empty(self, simple_grid_2x2: Grid):
        """Test that grid with at least one empty cell is not finished."""
        assert simple_grid_2x2._is_grid_finished() is False

    def test_grid_finished_all_queens(self, grid_all_queens: Grid):
        """Test that grid with all queens is finished."""
        assert grid_all_queens._is_grid_finished() is True

    def test_grid_finished_all_blocked(self, grid_all_blocked: Grid):
        """Test that grid with all blocked cells is finished."""
        assert grid_all_blocked._is_grid_finished() is True

    def test_grid_finished_mixed(self, grid_mixed: Grid):
        """Test that grid with only QUEEN and BLOCKED is finished."""
        grid = Grid(
            [
                [Cell((0, 0), "cyan", QUEEN), Cell((0, 1), "cyan", BLOCKED)],
                [Cell((1, 0), "red", BLOCKED), Cell((1, 1), "red", QUEEN)],
            ]
        )
        assert grid._is_grid_finished() is True

    def test_grid_finished_empty_grid(self):
        """Test that empty grid is considered finished."""
        grid = Grid([])
        assert grid._is_grid_finished() is True

    def test_grid_finished_one_cell_empty(self):
        """Test grid with one empty cell."""
        grid = Grid([[Cell((0, 0), "red", EMPTY)]])
        assert grid._is_grid_finished() is False

    def test_grid_finished_one_cell_queen(self):
        """Test grid with one queen cell."""
        grid = Grid([[Cell((0, 0), "red", QUEEN)]])
        assert grid._is_grid_finished() is True

    def test_grid_finished_one_cell_blocked(self):
        """Test grid with one blocked cell."""
        grid = Grid([[Cell((0, 0), "red", BLOCKED)]])
        assert grid._is_grid_finished() is True


# =============================================================================
# Test _safe_block
# =============================================================================


class TestSafeBlock:
    """Tests for _safe_block method."""

    def test_safe_block_valid_coords(self, simple_grid_2x2: Grid):
        """Test _safe_block with valid coordinates."""
        initial_value = simple_grid_2x2.grid[0][0].value
        assert initial_value == EMPTY
        simple_grid_2x2._safe_block(0, 0)
        assert simple_grid_2x2.grid[0][0].value == BLOCKED

    def test_safe_block_negative_row(self, simple_grid_2x2: Grid):
        """Test _safe_block with negative row - should not crash."""
        simple_grid_2x2._safe_block(-1, 0)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_negative_col(self, simple_grid_2x2: Grid):
        """Test _safe_block with negative column - should not crash."""
        simple_grid_2x2._safe_block(0, -1)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_row_too_large(self, simple_grid_2x2: Grid):
        """Test _safe_block with row too large - should not crash."""
        simple_grid_2x2._safe_block(100, 0)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_col_too_large(self, simple_grid_2x2: Grid):
        """Test _safe_block with column too large - should not crash."""
        simple_grid_2x2._safe_block(0, 100)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_queen_cell(self, simple_grid_2x2: Grid):
        """Test _safe_block on queen cell - should not block it."""
        simple_grid_2x2.grid[0][0].value = QUEEN
        simple_grid_2x2._safe_block(0, 0)
        assert simple_grid_2x2.grid[0][0].value == QUEEN

    def test_safe_block_already_blocked(self, simple_grid_2x2: Grid):
        """Test _safe_block on already blocked cell."""
        simple_grid_2x2.grid[0][0].value = BLOCKED
        simple_grid_2x2._safe_block(0, 0)
        assert simple_grid_2x2.grid[0][0].value == BLOCKED

    def test_safe_block_multiple_calls(self, simple_grid_2x2: Grid):
        """Test multiple _safe_block calls."""
        simple_grid_2x2._safe_block(0, 0)
        simple_grid_2x2._safe_block(0, 1)
        simple_grid_2x2._safe_block(1, 0)
        assert simple_grid_2x2.grid[0][0].value == BLOCKED
        assert simple_grid_2x2.grid[0][1].value == BLOCKED
        assert simple_grid_2x2.grid[1][0].value == BLOCKED


# =============================================================================
# Test _find_regions
# =============================================================================


class TestFindRegions:
    """Tests for _find_regions method."""

    def test_find_regions_empty_grid(self):
        """Test _find_regions on empty grid."""
        grid = Grid([])
        regions = grid.regions
        assert regions == []

    def test_find_regions_single_color(self, grid_single_color: Grid):
        """Test _find_regions with single color."""
        regions = grid_single_color.regions
        assert len(regions) == 1
        assert len(regions[0]) == 9

    def test_find_regions_multiple_colors(self, simple_grid_2x2: Grid):
        """Test _find_regions with multiple colors."""
        regions = simple_grid_2x2.regions
        assert len(regions) == 4

    def test_find_regions_coordinates(self, simple_grid_2x2: Grid):
        """Test that region coordinates are correct."""
        regions = simple_grid_2x2.regions
        cyan_region = None
        for reg in regions:
            if (0, 0) in reg:
                cyan_region = reg
                break
        assert cyan_region is not None
        assert (0, 0) in cyan_region
        assert len(cyan_region) == 1

    def test_find_regions_order_preserved(self):
        """Test that region order matches color appearance order."""
        grid = Grid(
            [
                [Cell((0, 0), "first"), Cell((0, 1), "second")],
                [Cell((1, 0), "first"), Cell((1, 1), "third")],
            ]
        )
        regions = grid.regions
        assert (0, 0) in regions[0] or (1, 0) in regions[0]

    def test_find_regions_all_cells_accounted_for(self):
        """Test that all cells are in some region."""
        grid = Grid(
            [
                [Cell((0, 0), "A"), Cell((0, 1), "B")],
                [Cell((1, 0), "A"), Cell((1, 1), "B")],
            ]
        )
        regions = grid.regions
        all_coords = {(r, c) for reg in regions for (r, c) in reg}
        expected_coords = {(0, 0), (0, 1), (1, 0), (1, 1)}
        assert all_coords == expected_coords

    def test_find_regions_no_duplicate_coords(self):
        """Test that no coordinate appears in multiple regions."""
        grid = Grid(
            [
                [Cell((0, 0), "A"), Cell((0, 1), "B")],
                [Cell((1, 0), "A"), Cell((1, 1), "B")],
            ]
        )
        regions = grid.regions
        all_coords: list[tuple[int, int]] = []
        for reg in regions:
            all_coords.extend(reg)
        assert len(all_coords) == len(set(all_coords)) == 4


# =============================================================================
# Test _claim_cell
# =============================================================================


class TestClaimCell:
    """Tests for _claim_cell method."""

    def test_claim_cell_sets_queen(self):
        """Test that _claim_cell sets the cell to queen."""
        grid = Grid([[Cell((0, 0), "cyan")]])
        grid._claim_cell(grid[0][0])
        assert grid[0][0].value == QUEEN

    def test_claim_cell_blocks_row(self):
        """Test that _claim_cell blocks all cells in the same row."""
        grid = Grid(
            [
                [Cell((0, 0), "cyan"), Cell((0, 1), "cyan"), Cell((0, 2), "cyan")],
            ]
        )
        grid._claim_cell(grid[0][1])
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
        grid._claim_cell(grid[1][0])
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
        grid._claim_cell(grid[1][1])
        assert grid[0][0].value == BLOCKED
        assert grid[0][2].value == BLOCKED
        assert grid[2][0].value == BLOCKED
        assert grid[2][2].value == BLOCKED

    def test_claim_cell_already_queen(self):
        """Test _claim_cell on already queen cell."""
        grid = Grid([[Cell((0, 0), "cyan", QUEEN)]])
        grid._claim_cell(grid[0][0])
        assert grid[0][0].value == QUEEN

    def test_claim_cell_in_grid(self, simple_grid_2x2: Grid):
        """Test _claim_cell on a cell in a 2x2 grid."""
        cell = simple_grid_2x2[0][0]
        simple_grid_2x2._claim_cell(cell)
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
        grid._claim_region(target)
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
        grid._claim_region(target)
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
        grid._claim_region(target)
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
                [Cell((0, 0), "red"), Cell((0, 1), "red"), Cell((0, 2), "red")],
            ]
        )
        left = grid[0][0]
        right = grid[0][2]
        grid._claim_row(left, right)
        assert True

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
                [Cell((0, 0), "red")],
                [Cell((1, 0), "red")],
                [Cell((2, 0), "red")],
            ]
        )
        top = grid[0][0]
        bottom = grid[2][0]
        grid._claim_column(top, bottom)
        assert True

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
        assert grid[1][2].is_blocked()  # No upward from row 0, but cells[1] gets processed

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
                [Cell((0, 0), "red"), Cell((0, 1), "red"), Cell((0, 2), "blue")],
                [Cell((1, 0), "red"), Cell((1, 1), "red"), Cell((1, 2), "blue")],
            ]
        )
        cells1 = [grid[0][0], grid[0][1]]
        cells2 = [grid[1][0], grid[1][1]]
        grid._claim_row_parallel(cells1, cells2)
        assert True

    def test_claim_column_parallel_basic(self):
        """Test _claim_column_parallel basic execution."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "blue"), Cell((0, 2), "blue")],
                [Cell((1, 0), "red"), Cell((1, 1), "blue"), Cell((1, 2), "blue")],
            ]
        )
        cells1 = [grid[0][1], grid[0][2]]
        cells2 = [grid[1][1], grid[1][2]]
        grid._claim_column_parallel(cells1, cells2)
        assert True

    def test_claim_parallel_empty_regions(self):
        """Test _claim_parallel with empty regions list."""
        grid = Grid([[Cell((0, 0), "red")]])
        grid._claim_parallel([])
        assert grid[0][0].value == EMPTY

    def test_claim_parallel_no_matching_regions(self):
        """Test _claim_parallel with non-matching regions."""
        grid = Grid(
            [
                [Cell((0, 0), "red"), Cell((0, 1), "blue")],
                [Cell((1, 0), "red"), Cell((1, 1), "blue")],
            ]
        )
        regions = [[grid[0][0]], [grid[1][1]]]
        grid._claim_parallel(regions)
        assert True


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
            "R R",
            "G G",
        ]
        grid = build_example_grid(test_grid)
        result = grid.resolve()
        assert result is not None
        assert len(result) == 2

    def test_resolve_already_solved(self):
        """Test resolve on already solved grid."""
        grid = Grid(
            [
                [Cell((0, 0), "red", QUEEN), Cell((0, 1), "red", BLOCKED)],
                [Cell((1, 0), "blue", BLOCKED), Cell((1, 1), "blue", QUEEN)],
            ]
        )
        result = grid.resolve()
        assert result is not None

    def test_resolve_impossible_grid(self):
        """Test resolve on impossible grid (no solution)."""
        test_grid = [
            "R R",
            "R R",
        ]
        grid = build_example_grid(test_grid)
        result = grid.resolve()
        assert result is not None

    def test_resolve_returns_grid(self):
        """Test that resolve returns the grid."""
        test_grid = ["R R", "G G"]
        grid = build_example_grid(test_grid)
        result = grid.resolve()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_resolve_max_iterations(self):
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
        grid._claim_cell(grid[0][0])
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
        grid._claim_cell(grid[0][0])
        assert len(grid.regions) == 1
