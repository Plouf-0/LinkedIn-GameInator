"""Tests for Queens.ui module.

Comprehensive test suite covering:
- Constants (EMPTY, QUEEN, BLOCKED)
- print_grid function with various grid configurations
- print_regions function with various region configurations
- print_color_palette function
"""

# pyright: reportPrivateUsage=false

from pathlib import Path

import pytest

from Queens.queens_grid import BLOCKED, EMPTY, QUEEN, Cell, Grid, build_example_grid
from Queens.ui import (
    ARCHIVE_PATH,
    achive_queens_grid,
    find_or_create_archive,
    print_color_palette,
    print_grid,
    print_regions,
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
def grid_with_queens():
    """Create a 3x3 grid with queen and blocked cells."""
    return Grid(
        [
            [
                Cell(0, 0, "cyan", QUEEN),
                Cell(0, 1, "cyan", BLOCKED),
                Cell(0, 2, "cyan"),
            ],
            [
                Cell(1, 0, "blue", BLOCKED),
                Cell(1, 1, "blue", QUEEN),
                Cell(1, 2, "blue"),
            ],
            [
                Cell(2, 0, "green"),
                Cell(2, 1, "green", BLOCKED),
                Cell(2, 2, "green"),
            ],
        ]
    )


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
def grid_from_builder():
    """Create a grid using build_example_grid helper."""
    test_grid = [
        "R R",
        "G G",
    ]
    return Grid(build_example_grid(test_grid))


@pytest.fixture
def grid_all_colors() -> Grid:
    """Create a grid with all supported colors."""
    colors = [
        "corail",
        "cyan",
        "bleu",
        "orange",
        "vert",
        "jaune",
        "lavande",
        "gris",
        "black",
    ]
    grid_data: list[list[Cell]] = []
    for r, color in enumerate(colors[:3]):
        row: list[Cell] = []
        for c in range(3):
            row.append(Cell(r, c, color))
        grid_data.append(row)
    return Grid(grid_data)


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
            [
                Cell(2, 0, "blue"),
                Cell(2, 1, "blue", BLOCKED),
                Cell(2, 2, "blue"),
            ],
        ]
    )


@pytest.fixture
def big_grid():
    """Create a larger 5x5 grid."""
    return Grid([[Cell(r, c, "cyan") for c in range(5)] for r in range(5)])


@pytest.fixture
def all_colors_grid():
    """Create a grid that includes all supported colors."""
    test_grid = [
        "B C G N O P R V W Y",
        "Y W V R P O N G C B",
    ]
    return Grid(build_example_grid(test_grid))


# =============================================================================
# Test Constants
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_empty_constant(self):
        """Test that EMPTY constant is 0."""
        assert EMPTY == 0

    def test_queen_constant(self):
        """Test that QUEEN constant is 1."""
        assert QUEEN == 1

    def test_blocked_constant(self):
        """Test that BLOCKED constant is -1."""
        assert BLOCKED == -1

    def test_constants_are_distinct(self):
        """Test that all constants have distinct values."""
        values = {EMPTY, QUEEN, BLOCKED}
        assert len(values) == 3


# =============================================================================
# Test print_grid
# =============================================================================


class TestPrintGrid:
    """Tests for print_grid function."""

    def test_print_grid_1x1_empty(self, simple_grid_1x1: Grid, capsys: pytest.CaptureFixture[str]):
        """Test printing a minimal 1x1 grid with empty cell."""
        print_grid(simple_grid_1x1.grid)
        captured = capsys.readouterr()

        output = captured.out
        lines = output.strip().split("\n")

        assert lines[0].startswith("⟍")
        assert "0" in lines[0]
        assert lines[1].startswith(" 0 ")
        assert "." in lines[1]

    def test_print_grid_2x2(self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]):
        """Test printing a 2x2 grid with different colors."""
        print_grid(simple_grid_2x2.grid)
        captured = capsys.readouterr()

        output = captured.out
        lines = output.strip().split("\n")

        assert len(lines) >= 3
        assert "0" in lines[0]
        assert "1" in lines[0]
        assert " 0 " in lines[1]
        assert " 1 " in lines[2]

    def test_print_grid_with_queen(
        self, grid_with_queens: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing a grid containing queen cells."""
        print_grid(grid_with_queens.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " Q " in output

    def test_print_grid_with_blocked(
        self, grid_with_queens: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing a grid containing blocked cells."""
        print_grid(grid_with_queens.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " X " in output

    def test_print_grid_colors_cyan(
        self, simple_grid_1x1: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test that cyan color produces correct ANSI code."""
        print_grid(simple_grid_1x1.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert "\033[1;30;46m" in output

    def test_print_grid_colors_all(self, grid_all_colors: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that all supported colors produce correct ANSI codes."""
        print_grid(grid_all_colors.grid)
        captured = capsys.readouterr()

        output = captured.out

        color_codes = {
            "corail": "\033[1;30;41m",
            "cyan": "\033[1;30;46m",
            "bleu": "\033[1;30;44m",
            "orange": "\033[1;30;43m",
            "vert": "\033[1;30;42m",
            "jaune": "\033[1;30;103m",
            "lavande": "\033[1;30;45m",
            "gris": "\033[1;30;40m",
            "black": "\033[1;30;47m",
        }

        for color, code in color_codes.items():
            if color in [c.color for row in grid_all_colors.grid for c in row]:
                assert code in output, f"Color code for {color} not found in output"

    def test_print_grid_ansi_reset(self, simple_grid_1x1: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that ANSI reset codes are present."""
        print_grid(simple_grid_1x1.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert "\033[0m" in output

    def test_print_grid_header_format(
        self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test the header row format."""
        print_grid(simple_grid_2x2.grid)
        captured = capsys.readouterr()

        output = captured.out
        lines = output.strip().split("\n")
        header = lines[0]

        assert header.startswith("⟍")
        assert " 0 " in header
        assert " 1 " in header

    def test_print_grid_row_format(self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that each row starts with its index."""
        print_grid(simple_grid_2x2.grid)
        captured = capsys.readouterr()

        output = captured.out
        lines = output.strip().split("\n")

        assert lines[1].startswith(" 0 ")
        assert lines[2].startswith(" 1 ")

    def test_print_grid_cell_separators(
        self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test that cells are properly separated with spaces."""
        print_grid(simple_grid_2x2.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " . " in output

    def test_print_grid_from_builder(
        self, grid_from_builder: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing a grid created with build_example_grid."""
        print_grid(grid_from_builder.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert len(output) > 0
        assert "⟍" in output

    def test_print_grid_large_grid(self, big_grid: Grid, capsys: pytest.CaptureFixture[str]):
        """Test printing a larger grid (5x5)."""
        print_grid(big_grid.grid)
        captured = capsys.readouterr()

        output = captured.out
        lines = output.strip().split("\n")

        assert len(lines) >= 6
        for i in range(5):
            assert f" {i} " in lines[0]

    def test_print_grid_mixed_values(self, capsys: pytest.CaptureFixture[str]):
        """Test grid with mixed EMPTY, QUEEN, BLOCKED values."""
        grid = Grid(
            [
                [Cell(0, 0, "cyan", EMPTY), Cell(0, 1, "cyan", QUEEN)],
                [Cell(1, 0, "blue", BLOCKED), Cell(1, 1, "blue", EMPTY)],
            ]
        )

        print_grid(grid.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " . " in output
        assert " Q " in output
        assert " X " in output

    def test_print_grid_empty_cell_method(
        self, empty_cell: Cell, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing grid with cell using is_empty method."""
        grid = Grid([[empty_cell]])
        print_grid(grid.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " . " in output
        assert empty_cell.is_empty()

    def test_print_grid_queen_cell_method(
        self, queen_cell: Cell, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing grid with cell using is_queen method."""
        grid = Grid([[queen_cell]])
        print_grid(grid.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " Q " in output
        assert queen_cell.is_queen()

    def test_print_grid_blocked_cell_method(
        self, blocked_cell: Cell, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing grid with cell using is_blocked method."""
        grid = Grid([[blocked_cell]])
        print_grid(grid.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " X " in output
        assert blocked_cell.is_blocked()


# =============================================================================
# Test print_regions
# =============================================================================


class TestPrintRegions:
    """Tests for print_regions function."""

    def test_print_regions_empty(self, capsys: pytest.CaptureFixture[str]):
        """Test printing an empty list of regions."""
        print_regions([])
        captured = capsys.readouterr()

        output = captured.out
        assert "Found regions" in output
        assert "Region 0" not in output

    def test_print_regions_single(self, capsys: pytest.CaptureFixture[str]):
        """Test printing a single region."""
        regions = [[Cell(0, 0, "red"), Cell(0, 1, "red"), Cell(1, 0, "red")]]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        assert "Found regions" in output
        assert "Region 0" in output
        assert "Cell(0,0,red" in output or "(0, 0)" in output
        assert "Cell(0,1,red" in output or "(0, 1)" in output
        assert "Cell(1,0,red" in output or "(1, 0)" in output

    def test_print_regions_multiple(
        self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing multiple regions from grid."""
        regions = [region.cells for region in simple_grid_2x2.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        assert "Region 0" in output
        assert "Region 1" in output
        assert "Region 2" in output
        assert "Region 3" in output

    def test_print_regions_format(self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]):
        """Test the format of region output."""
        regions = [region.cells for region in simple_grid_2x2.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        lines = output.strip().split("\n")

        assert lines[0] == "Found regions (list of coords per color):"

        for i in range(len(regions)):
            assert f"Region {i}:" in output

    def test_print_regions_with_all_colors(
        self, grid_all_colors: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing regions with various coordinate values."""
        regions = [region.cells for region in grid_all_colors.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        for i in range(len(regions)):
            assert f"Region {i}:" in output

    def test_print_regions_order_preserved(
        self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test that region order is preserved in output."""
        regions = [region.cells for region in simple_grid_2x2.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        assert output.index("Region 0") < output.index("Region 1")
        assert output.index("Region 1") < output.index("Region 2")

    def test_print_regions_from_grid_regions(
        self, grid_from_builder: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing regions extracted from grid.regions."""
        regions = [region.cells for region in grid_from_builder.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        assert "Found regions" in output
        assert len(grid_from_builder.regions) > 0

    def test_print_regions_single_color(
        self, grid_single_color: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing regions with single color grid."""
        regions = [region.cells for region in grid_single_color.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        assert "Region 0:" in output
        assert len(regions) == 1

    def test_print_regions_with_queens(
        self, grid_with_queens: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing regions from grid with queens."""
        regions = [region.cells for region in grid_with_queens.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        assert "Found regions" in output
        assert "Region 0" in output


# =============================================================================
# Test print_color_palette
# =============================================================================


class TestPrintColorPalette:
    """Tests for print_color_palette function."""

    def test_print_color_palette_runs(self, capsys: pytest.CaptureFixture[str]):
        """Test that print_color_palette runs without error."""
        print_color_palette()
        captured = capsys.readouterr()

        assert len(captured.out) > 0

    def test_print_color_palette_has_ansi_codes(self, capsys: pytest.CaptureFixture[str]):
        """Test that print_color_palette outputs ANSI color codes."""
        print_color_palette()
        captured = capsys.readouterr()

        output = captured.out
        assert "\033[" in output

    def test_print_color_palette_covers_all_styles(self, capsys: pytest.CaptureFixture[str]):
        """Test that both normal and bold styles are present."""
        print_color_palette()
        captured = capsys.readouterr()

        output = captured.out
        assert "0;3" in output or "0;30" in output
        assert "1;3" in output or "1;30" in output

    def test_print_color_palette_covers_fg_colors(self, capsys: pytest.CaptureFixture[str]):
        """Test that foreground colors 30-37 are present."""
        print_color_palette()
        captured = capsys.readouterr()

        output = captured.out
        for fg in range(30, 38):
            assert f"{fg};4" in output, f"Foreground color {fg} not found"

    def test_print_color_palette_covers_bg_colors(self, capsys: pytest.CaptureFixture[str]):
        """Test that background colors 40-47 are present."""
        print_color_palette()
        captured = capsys.readouterr()

        output = captured.out
        for bg in range(40, 48):
            assert f";{bg}m" in output, f"Background color {bg} not found"

    def test_print_color_palette_reset_codes(self, capsys: pytest.CaptureFixture[str]):
        """Test that ANSI reset codes are present."""
        print_color_palette()
        captured = capsys.readouterr()

        output = captured.out
        assert "\033[0m" in output


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_print_grid_and_regions_consistency(
        self, grid_from_builder: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test that print_grid and print_regions work with the same grid."""
        print_grid(grid_from_builder.grid)
        captured_grid = capsys.readouterr()

        regions = [region.cells for region in grid_from_builder.regions]
        print_regions(regions)
        captured_regions = capsys.readouterr()

        assert len(captured_grid.out) > 0
        assert len(captured_regions.out) > 0

    def test_full_ui_workflow(self, capsys: pytest.CaptureFixture[str]):
        """Test a complete workflow: build grid, print grid, print regions."""
        test_grid = [
            "R R G",
            "R R G",
            "B B B",
        ]
        grid = Grid(build_example_grid(test_grid))

        print_grid(grid.grid)
        captured_grid = capsys.readouterr()

        regions = [region.cells for region in grid.regions]
        print_regions(regions)
        captured_regions = capsys.readouterr()

        assert "⟍" in captured_grid.out
        assert "Found regions" in captured_regions.out
        assert len(grid.regions) == 3

    def test_grid_with_all_methods(self, grid_mixed: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that all cell methods work with print_grid."""
        print_grid(grid_mixed.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert " Q " in output
        assert " X " in output
        assert " . " in output

        for row in grid_mixed.grid:
            for cell in row:
                assert cell.is_queen() or cell.is_blocked() or cell.is_empty()

    def test_print_grid_with_single_color_grid(
        self, grid_single_color: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing a grid with single color region."""
        print_grid(grid_single_color.grid)
        captured = capsys.readouterr()

        output = captured.out
        assert len(output) > 0
        assert len(grid_single_color.regions) == 1

    def test_print_regions_from_single_color(
        self, grid_single_color: Grid, capsys: pytest.CaptureFixture[str]
    ):
        """Test printing regions from single color grid."""
        regions = [region.cells for region in grid_single_color.regions]
        print_regions(regions)
        captured = capsys.readouterr()

        output = captured.out
        assert "Region 0:" in output
        assert len(regions) == 1
        assert len(regions[0]) == 9

    def test_print_complex_example_grid(self, capsys: pytest.CaptureFixture[str]):
        """Test printing a complex 10x10 example grid with multiple colors."""
        # Create grid directly with French color names that match ui.py
        grid_data: list[list[Cell]] = []
        for r in range(10):
            row: list[Cell] = []
            for c in range(10):
                # Determine color based on the pattern
                if r == 0:
                    color = "pourpre"
                elif r == 1:
                    if c == 4:
                        color = "vert"
                    elif c == 6:
                        color = "black"
                    else:
                        color = "pourpre"
                elif r == 2:
                    if c == 4:
                        color = "vert"
                    elif c == 6:
                        color = "black"
                    else:
                        color = "pourpre"
                elif r == 3:
                    if c == 3:
                        color = "bleu"
                    elif c == 4:
                        color = "vert"
                    elif c == 5:
                        color = "gris"
                    elif c == 6:
                        color = "black"
                    else:
                        color = "pourpre"
                elif r == 4:
                    if c == 3:
                        color = "bleu"
                    elif c == 4:
                        color = "vert"
                    elif c == 5:
                        color = "gris"
                    elif c == 6:
                        color = "black"
                    else:
                        color = "pourpre"
                elif r == 5:
                    if 2 <= c <= 7:
                        color = "rouge"
                    else:
                        color = "pourpre"
                elif r == 6:
                    if 2 <= c <= 7:
                        color = "cyan"
                    else:
                        color = "pourpre"
                elif r == 7:
                    if 1 <= c <= 8:
                        color = "orange"
                    else:
                        color = "pourpre"
                elif r == 8:
                    if 1 <= c <= 8:
                        color = "blanc"
                    else:
                        color = "pourpre"
                elif r == 9:
                    if c < 9:
                        color = "jaune"
                    else:
                        color = "pourpre"
                else:
                    color = "pourpre"
                row.append(Cell(r, c, color))
            grid_data.append(row)
        grid = Grid(grid_data)

        print_grid(grid.grid)
        captured = capsys.readouterr()

        output = captured.out
        lines = output.strip().split("\n")

        assert len(lines) >= 11
        assert "⟍" in lines[0]
        for i in range(10):
            assert f" {i} " in lines[0]

        # Verify each row starts with its index
        for row_idx in range(10):
            assert lines[row_idx + 1].startswith(f" {row_idx} ")

        # Verify all cells are empty (.) in the output
        assert output.count(" . ") >= 90

        # Colors in our grid: pourpre, vert, black, bleu, gris, rouge, cyan, orange, blanc, jaune
        # Note: pourpre, rouge, blanc don't have specific ANSI codes in ui.py,
        # they will use the default \033[0m
        # So we check the ones that DO have codes
        assert "\033[1;30;42m" in output  # vert (green) - rows 1,2 at col 4; rows 3,4 at col 4
        assert "\033[1;30;47m" in output  # black - rows 1,2 at col 6; rows 3,4 at col 6
        assert "\033[1;30;44m" in output  # bleu (blue) - rows 3,4 at col 3
        assert "\033[1;30;40m" in output  # gris (gray) - rows 3,4 at col 5
        assert "\033[1;30;46m" in output  # cyan - row 6 at cols 2-7
        assert "\033[1;30;43m" in output  # orange - row 7 at cols 1-8
        assert "\033[1;30;103m" in output  # jaune (yellow) - row 9 at cols 0-8

        # Verify that colors without specific codes use default reset
        assert "\033[0m" in output

        # Verify specific rows contain expected color codes
        # Row 1 (line 2 in output): contains vert at col 4 and black at col 6
        assert "\033[1;30;42m" in lines[2]  # vert in row 1
        assert "\033[1;30;47m" in lines[2]  # black in row 1

        # Row 2 (line 3 in output): contains vert at col 4 and black at col 6
        assert "\033[1;30;42m" in lines[3]  # vert in row 2
        assert "\033[1;30;47m" in lines[3]  # black in row 2

        # Row 3 (line 4 in output): contains bleu at col 3,
        # vert at col 4, gris at col 5, black at col 6
        assert "\033[1;30;44m" in lines[4]  # bleu in row 3
        assert "\033[1;30;42m" in lines[4]  # vert in row 3
        assert "\033[1;30;40m" in lines[4]  # gris in row 3
        assert "\033[1;30;47m" in lines[4]  # black in row 3

        # Row 4 (line 5 in output): contains bleu at col 3,
        # vert at col 4, gris at col 5, black at col 6
        assert "\033[1;30;44m" in lines[5]  # bleu in row 4
        assert "\033[1;30;42m" in lines[5]  # vert in row 4
        assert "\033[1;30;40m" in lines[5]  # gris in row 4
        assert "\033[1;30;47m" in lines[5]  # black in row 4

        # Row 6 (line 7 in output): contains cyan at cols 2-7 (6 cells)
        assert lines[7].count("\033[1;30;46m") >= 6  # cyan cells in row 6

        # Row 7 (line 8 in output): contains orange at cols 1-8 (8 cells)
        assert lines[8].count("\033[1;30;43m") >= 8  # orange cells in row 7

        # Row 9 (line 10 in output): contains jaune at cols 0-8 (9 cells)
        assert lines[10].count("\033[1;30;103m") >= 9  # jaune cells in row 9

        regions = [region.cells for region in grid.regions]
        print_regions(regions)
        captured_regions = capsys.readouterr()

        assert "Found regions" in captured_regions.out
        assert len(grid.regions) == 10


# =============================================================================
# Test Create archive
# =============================================================================


class TestCreateArchive:
    def test_find_or_create_archive_runs(self):
        """Test that find_or_create_archive runs without error."""
        find_or_create_archive("test_archive_find_create")
        path = Path(f"{ARCHIVE_PATH}/test_archive_find_create_Queens.txt")
        assert path.exists()

    def test_create_archive_runs(self, all_colors_grid: Grid):
        """Test that achive_queens_grid runs without error and creates a file."""
        grid: list[list[Cell]] = all_colors_grid.grid
        achive_queens_grid(grid, "test_archive")

        path = Path(f"{ARCHIVE_PATH}/test_archive_Queens.txt")
        assert path.exists()
        lines = path.read_text(encoding="utf-8").splitlines()
        path.unlink()

        assert len(lines) == 5
        assert lines[0] == "Archive of the LinkedIn's game Queens on the day of test_archive"
        assert lines[1] == "Today's grid size is 2x10."
        assert lines[2] == ""
        assert lines[3] == "B C G N O P R V W Y"
        assert lines[4] == "Y W V R P O N G C B"
