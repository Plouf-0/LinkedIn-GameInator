"""Tests for Queens.grid module.

Comprehensive test suite covering:
- Cell class functionality and edge cases
- Grid class methods and edge cases
- Region finding and claiming logic
"""

# pyright: reportPrivateUsage=false

import sys
import pytest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from Queens.queens_grid import (
    Cell,
    Grid,
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
    return Grid([[Cell(0, 0, "cyan")]])


@pytest.fixture
def simple_grid_2x2():
    """Create a 2x2 grid with different colors."""
    return Grid(
        [
            [Cell(0, 0, "cyan"), Cell(0, 1, "red")],
            [Cell(1, 0, "blue"), Cell(1, 1, "green")],
        ]
    )


@pytest.fixture
def grid_single_color():
    """Create a 3x3 grid with a single color."""
    return Grid([[Cell(r, c, "red") for c in range(3)] for r in range(3)])


@pytest.fixture
def grid_all_queens():
    """Create a 2x2 grid where all cells are queens."""
    return Grid(
        [
            [Cell(0, 0, "cyan", QUEEN), Cell(0, 1, "red", QUEEN)],
            [Cell(1, 0, "blue", QUEEN), Cell(1, 1, "green", QUEEN)],
        ]
    )


@pytest.fixture
def grid_all_blocked():
    """Create a 2x2 grid where all cells are blocked."""
    return Grid(
        [
            [Cell(0, 0, "cyan", BLOCKED), Cell(0, 1, "red", BLOCKED)],
            [Cell(1, 0, "blue", BLOCKED), Cell(1, 1, "green", BLOCKED)],
        ]
    )


@pytest.fixture
def grid_mixed():
    """Create a 3x3 grid with mixed values."""
    return Grid(
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

    def test_cell_creation_with_value(self):
        """Test cell creation with specific value."""
        cell = Cell(5, 3, "red", QUEEN)
        assert cell.row == 5
        assert cell.col == 3
        assert cell.color == "red"
        assert cell.value == QUEEN

    def test_cell_creation_negative_coords(self):
        """Test cell creation with negative coordinates."""
        cell = Cell(-1, -1, "blue")
        assert cell.row == -1
        assert cell.col == -1

    def test_cell_creation_empty_color(self):
        """Test cell creation with empty color string."""
        cell = Cell(0, 0, "")
        assert cell.color == ""
        assert cell.value == EMPTY

    def test_cell_creation_large_coords(self):
        """Test cell creation with large coordinates."""
        cell = Cell(1000, 1000, "green")
        assert cell.row == 1000
        assert cell.col == 1000

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
        cell = Cell(2, 3, "red", QUEEN)
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
        row = simple_grid_2x2._get_row(0)
        assert len(row) == 2
        assert row[0].row == 0
        assert row[1].row == 0

    def test_grid_getitem_second_row(self, simple_grid_2x2: Grid):
        """Test __getitem__ for second row."""
        row = simple_grid_2x2._get_row(1)
        assert row[0].row == 1
        assert row[1].row == 1

    def test_grid_iter(self, simple_grid_2x2: Grid):
        """Test __iter__ allows iteration over grid."""
        rows = list(simple_grid_2x2)
        assert len(rows) == 2
        assert rows[0] == simple_grid_2x2._get_row(0)
        assert rows[1] == simple_grid_2x2._get_row(1)

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
        grid = Grid([[Cell(0, 0, "red"), Cell(0, 1, "red")]])
        assert len(grid.grid) == 1
        assert len(grid._get_row(0)) == 2

    def test_grid_single_column(self):
        """Test grid with single column."""
        grid = Grid(
            [
                [Cell(0, 0, "red")],
                [Cell(1, 0, "blue")],
                [Cell(2, 0, "green")],
            ]
        )
        assert len(grid.grid) == 3
        assert len(grid._get_row(0)) == 1


# =============================================================================
# Test _is_grid_finished
# =============================================================================


class TestIsGridFinished:
    """Tests for _is_grid_finished method."""

    def test_grid_finished_empty(self, simple_grid_1x1: Grid):
        """Test that grid with empty cell is not finished."""
        assert simple_grid_1x1.is_grid_finished() is False

    def test_grid_finished_single_empty(self, simple_grid_2x2: Grid):
        """Test that grid with at least one empty cell is not finished."""
        assert simple_grid_2x2.is_grid_finished() is False

    def test_grid_finished_all_queens(self, grid_all_queens: Grid):
        """Test that grid with all queens is finished."""
        assert grid_all_queens.is_grid_finished() is True

    def test_grid_finished_all_blocked(self, grid_all_blocked: Grid):
        """Test that grid with all blocked cells is finished."""
        assert grid_all_blocked.is_grid_finished() is True

    def test_grid_finished_mixed(self):
        """Test that grid with only QUEEN and BLOCKED is finished."""
        grid = Grid(
            [
                [Cell(0, 0, "cyan", QUEEN), Cell(0, 1, "cyan", BLOCKED)],
                [Cell(1, 0, "red", BLOCKED), Cell(1, 1, "red", QUEEN)],
            ]
        )
        assert grid.is_grid_finished() is True

    def test_grid_finished_empty_grid(self):
        """Test that empty grid is considered finished."""
        grid = Grid([])
        assert grid.is_grid_finished() is True

    def test_grid_finished_one_cell_empty(self):
        """Test grid with one empty cell."""
        grid = Grid([[Cell(0, 0, "red", EMPTY)]])
        assert grid.is_grid_finished() is False

    def test_grid_finished_one_cell_queen(self):
        """Test grid with one queen cell."""
        grid = Grid([[Cell(0, 0, "red", QUEEN)]])
        assert grid.is_grid_finished() is True

    def test_grid_finished_one_cell_blocked(self):
        """Test grid with one blocked cell."""
        grid = Grid([[Cell(0, 0, "red", BLOCKED)]])
        assert grid.is_grid_finished() is True


# =============================================================================
# Test _safe_block
# =============================================================================


class TestSafeBlock:
    """Tests for _safe_block method."""

    def test_safe_block_valid_coords(self, simple_grid_2x2: Grid):
        """Test _safe_block with valid coordinates."""
        initial_value = simple_grid_2x2.grid[0][0].value
        assert initial_value == EMPTY
        simple_grid_2x2.block_cell_by_coord(0, 0)
        assert simple_grid_2x2.grid[0][0].value == BLOCKED

    def test_safe_block_negative_row(self, simple_grid_2x2: Grid):
        """Test _safe_block with negative row - should not crash."""
        simple_grid_2x2.block_cell_by_coord(-1, 0)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_negative_col(self, simple_grid_2x2: Grid):
        """Test _safe_block with negative column - should not crash."""
        simple_grid_2x2.block_cell_by_coord(0, -1)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_row_too_large(self, simple_grid_2x2: Grid):
        """Test _safe_block with row too large - should not crash."""
        simple_grid_2x2.block_cell_by_coord(100, 0)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_col_too_large(self, simple_grid_2x2: Grid):
        """Test _safe_block with column too large - should not crash."""
        simple_grid_2x2.block_cell_by_coord(0, 100)
        assert simple_grid_2x2.grid[0][0].value == EMPTY

    def test_safe_block_queen_cell(self, simple_grid_2x2: Grid):
        """Test _safe_block on queen cell - should not block it."""
        simple_grid_2x2.grid[0][0].value = QUEEN
        simple_grid_2x2.block_cell_by_coord(0, 0)
        assert simple_grid_2x2.grid[0][0].value == QUEEN

    def test_safe_block_already_blocked(self, simple_grid_2x2: Grid):
        """Test _safe_block on already blocked cell."""
        simple_grid_2x2.grid[0][0].value = BLOCKED
        simple_grid_2x2.block_cell_by_coord(0, 0)
        assert simple_grid_2x2.grid[0][0].value == BLOCKED

    def test_safe_block_multiple_calls(self, simple_grid_2x2: Grid):
        """Test multiple _safe_block calls."""
        simple_grid_2x2.block_cell_by_coord(0, 0)
        simple_grid_2x2.block_cell_by_coord(0, 1)
        simple_grid_2x2.block_cell_by_coord(1, 0)
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
        assert len(regions[0].cells) == 9

    def test_find_regions_multiple_colors(self, simple_grid_2x2: Grid):
        """Test _find_regions with multiple colors."""
        regions = simple_grid_2x2.regions
        assert len(regions) == 4

    # def test_find_regions_coordinates(self, simple_grid_2x2: Grid):
    #     """Test that region coordinates are correct."""
    #     regions = simple_grid_2x2.regions
    #     cyan_region = None
    #     for reg in regions:
    #         if (0, 0) in reg.cells:
    #             cyan_region = reg
    #             break
    #     assert cyan_region is not None
    #     assert (0, 0) in cyan_region.cells
    #     assert len(cyan_region) == 1

    def test_find_regions_order_preserved(self):
        """Test that region order matches color appearance order."""
        grid = Grid(
            [
                [Cell(0, 0, "first"), Cell(0, 1, "second")],
                [Cell(1, 0, "first"), Cell(1, 1, "third")],
            ]
        )
        regions = grid.regions
        assert (0, 0) in regions[0].cells or (1, 0) in regions[0].cells

    # def test_find_regions_all_cells_accounted_for(self):
    #     """Test that all cells are in some region."""
    #     grid = Grid(
    #         [
    #             [Cell(0, 0, "A"), Cell(0, 1, "B")],
    #             [Cell(1, 0, "A"), Cell(1, 1, "B")],
    #         ]
    #     )
    #     regions = grid.regions
    #     all_coords = {(r, c) for reg in regions for (r, c) in reg}
    #     expected_coords = {(0, 0), (0, 1), (1, 0), (1, 1)}
    #     assert all_coords == expected_coords

    # def test_find_regions_no_duplicate_coords(self):
    #     """Test that no coordinate appears in multiple regions."""
    #     grid = Grid(
    #         [
    #             [Cell(0, 0, "A"), Cell(0, 1, "B")],
    #             [Cell(1, 0, "A"), Cell(1, 1, "B")],
    #         ]
    #     )
    #     regions = grid.regions
    #     all_coords: list[tuple[int, int]] = []
    #     for reg in regions:
    #         all_coords.extend(reg.cells)
    #     assert len(all_coords) == len(set(all_coords)) == 4
