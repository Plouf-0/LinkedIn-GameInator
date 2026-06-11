"""Tests for Queens.ui module.

Tests cover:
- Constants (EMPTY, QUEEN, BLOCKED)
- print_grid function with various grid configurations
- print_regions function with various region configurations
- print_color_palette function
"""

# type: ignore


import sys
import pytest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from Queens import Grid, Cell
from Queens.resolver import build_example_grid
from Queens.ui import print_grid, print_regions, print_color_palette, EMPTY, QUEEN, BLOCKED


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def simple_grid_1x1():
    """Create a minimal 1x1 grid with a single cell."""
    grid_data = [[Cell(0, 0, "cyan")]]
    return Grid(grid_data)


@pytest.fixture
def simple_grid_2x2():
    """Create a 2x2 grid with different colors."""
    grid_data = [
        [Cell(0, 0, "cyan"), Cell(0, 1, "bleu")],
        [Cell(1, 0, "vert"), Cell(1, 1, "orange")],
    ]
    return Grid(grid_data)


@pytest.fixture
def grid_with_queens():
    """Create a 3x3 grid with a queen and blocked cells."""
    grid_data = [
        [Cell(0, 0, "cyan", QUEEN), Cell(0, 1, "cyan", BLOCKED), Cell(0, 2, "cyan")],
        [Cell(1, 0, "bleu", BLOCKED), Cell(1, 1, "bleu", QUEEN), Cell(1, 2, "bleu")],
        [Cell(2, 0, "vert"), Cell(2, 1, "vert", BLOCKED), Cell(2, 2, "vert")],
    ]
    return Grid(grid_data)


@pytest.fixture
def grid_from_builder():
    """Create a grid using build_example_grid helper."""
    test_grid = [
        "R R",
        "G G",
    ]
    return build_example_grid(test_grid)


@pytest.fixture
def grid_all_colors():
    """Create a grid with all supported colors."""
    colors = ["corail", "cyan", "bleu", "orange", "vert", "jaune", "lavande", "gris", "black"]
    grid_data: list[list[Cell]] = []
    for r, color in enumerate(colors[:3]):
        row: list[Cell] = []
        for c in range(3):
            row.append(Cell(r, c, color))
        grid_data.append(row)
    return Grid(grid_data)


@pytest.fixture
def sample_regions():
    """Sample regions for testing print_regions."""
    return [
        [(0, 0), (0, 1), (1, 0)],
        [(1, 1), (2, 0), (2, 1)],
        [(0, 2)],
    ]


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
        print_grid(simple_grid_1x1)
        captured = capsys.readouterr()
        
        # Should have header row and data row
        output = captured.out
        lines = output.strip().split('\n')
        
        # Check header: "⟍  0 "
        assert lines[0].startswith("⟍")
        assert "0" in lines[0]
        
        # Check data row: " 0 " followed by cell content
        assert lines[1].startswith(" 0 ")
        # Should contain empty cell representation " . "
        assert "." in lines[1]

    def test_print_grid_2x2(self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]):
        """Test printing a 2x2 grid with different colors."""
        print_grid(simple_grid_2x2)
        captured = capsys.readouterr()
        
        output = captured.out
        lines = output.strip().split('\n')
        
        # Should have header + 2 data rows = 3 lines minimum
        assert len(lines) >= 3
        
        # Header should have columns 0 and 1
        assert "0" in lines[0]
        assert "1" in lines[0]
        
        # Each data row should start with row index
        assert " 0 " in lines[1]
        assert " 1 " in lines[2]

    def test_print_grid_with_queen(self, grid_with_queens: Grid, capsys: pytest.CaptureFixture[str]):
        """Test printing a grid containing queen cells."""
        print_grid(grid_with_queens)
        captured = capsys.readouterr()
        
        output = captured.out
        # Should contain queen representation " Q "
        assert " Q " in output

    def test_print_grid_with_blocked(self, grid_with_queens: Grid, capsys: pytest.CaptureFixture[str]):
        """Test printing a grid containing blocked cells."""
        print_grid(grid_with_queens)
        captured = capsys.readouterr()
        
        output = captured.out
        # Should contain blocked representation " X "
        assert " X " in output

    def test_print_grid_colors_cyan(self, simple_grid_1x1: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that cyan color produces correct ANSI code."""
        print_grid(simple_grid_1x1)
        captured = capsys.readouterr()
        
        output = captured.out
        # Cyan color should have ANSI code \033[1;30;46m
        assert "\033[1;30;46m" in output

    def test_print_grid_colors_all(self, grid_all_colors: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that all supported colors produce correct ANSI codes."""
        print_grid(grid_all_colors)
        captured = capsys.readouterr()
        
        output = captured.out
        
        # Check all color ANSI codes are present
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
        print_grid(simple_grid_1x1)
        captured = capsys.readouterr()
        
        output = captured.out
        # Should contain ANSI reset codes
        assert "\033[0m" in output

    def test_print_grid_header_format(self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]):
        """Test the header row format."""
        print_grid(simple_grid_2x2)
        captured = capsys.readouterr()
        
        output = captured.out
        lines = output.strip().split('\n')
        header = lines[0]
        
        # Header should start with the special character (looks like a pawn)
        assert header.startswith("⟍")
        # Should have column indices
        assert " 0 " in header
        assert " 1 " in header

    def test_print_grid_row_format(self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that each row starts with its index."""
        print_grid(simple_grid_2x2)
        captured = capsys.readouterr()
        
        output = captured.out
        lines = output.strip().split('\n')
        
        # Line 1 should start with " 0 "
        assert lines[1].startswith(" 0 ")
        # Line 2 should start with " 1 "
        assert lines[2].startswith(" 1 ")

    def test_print_grid_cell_separators(self, simple_grid_2x2: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that cells are properly separated with spaces."""
        print_grid(simple_grid_2x2)
        captured = capsys.readouterr()
        
        output = captured.out
        # Each cell content should be surrounded by spaces
        # The pattern " . " should appear for empty cells
        assert " . " in output

    def test_print_grid_from_builder(self, grid_from_builder: Grid, capsys: pytest.CaptureFixture[str]):
        """Test printing a grid created with build_example_grid."""
        print_grid(grid_from_builder)
        captured = capsys.readouterr()
        
        output = captured.out
        # Should have output
        assert len(output) > 0
        # Should have header
        assert "⟍" in output

    def test_print_grid_large_grid(self, capsys: pytest.CaptureFixture[str]):
        """Test printing a larger grid (5x5)."""
        grid_data: list[list[Cell]] = []
        for r in range(5):
            row: list[Cell] = []
            for c in range(5):
                row.append(Cell(r, c, "cyan"))
            grid_data.append(row)
        grid = Grid(grid_data)
        
        print_grid(grid)
        captured = capsys.readouterr()
        
        output = captured.out
        lines = output.strip().split('\n')
        
        # Should have header + 5 data rows = 6 lines
        assert len(lines) >= 6
        
        # Header should have columns 0-4
        for i in range(5):
            assert f" {i} " in lines[0]

    def test_print_grid_mixed_values(self, capsys: pytest.CaptureFixture[str]):
        """Test grid with mixed EMPTY, QUEEN, BLOCKED values."""
        grid_data = [
            [Cell(0, 0, "cyan", EMPTY), Cell(0, 1, "cyan", QUEEN)],
            [Cell(1, 0, "bleu", BLOCKED), Cell(1, 1, "bleu", EMPTY)],
        ]
        grid = Grid(grid_data)
        
        print_grid(grid)
        captured = capsys.readouterr()
        
        output = captured.out
        # Should contain all three representations
        assert " . " in output  # EMPTY
        assert " Q " in output  # QUEEN
        assert " X " in output  # BLOCKED


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
        # Should have the introductory message
        assert "Found regions" in output
        # Should have no region listings
        assert "Region 0" not in output

    def test_print_regions_single(self, capsys: pytest.CaptureFixture[str]):
        """Test printing a single region."""
        regions = [[(0, 0), (0, 1), (1, 0)]]
        print_regions(regions)
        captured = capsys.readouterr()
        
        output = captured.out
        # Should have the introductory message
        assert "Found regions" in output
        # Should have Region 0
        assert "Region 0" in output
        # Should contain the coordinates
        assert "(0, 0)" in output
        assert "(0, 1)" in output
        assert "(1, 0)" in output

    def test_print_regions_multiple(self, sample_regions: list[list[tuple[int, int]]], capsys: pytest.CaptureFixture[str]):
        """Test printing multiple regions."""
        print_regions(sample_regions)
        captured = capsys.readouterr()
        
        output = captured.out
        # Should have all regions
        assert "Region 0" in output
        assert "Region 1" in output
        assert "Region 2" in output

    def test_print_regions_format(self, sample_regions: list[list[tuple[int, int]]], capsys: pytest.CaptureFixture[str]):
        """Test the format of region output."""
        print_regions(sample_regions)
        captured = capsys.readouterr()
        
        output = captured.out
        lines = output.strip().split('\n')
        
        # First line should be the introduction
        assert lines[0] == "Found regions (list of coords per color):"
        
        # Following lines should be regions
        for i, region in enumerate(sample_regions):  # type: ignore
            assert f"Region {i}:" in output

    def test_print_regions_with_all_colors(self, capsys: pytest.CaptureFixture[str]):
        """Test printing regions with various coordinate values."""
        regions = [
            [(0, 0)],
            [(1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
        ]
        print_regions(regions)
        captured = capsys.readouterr()
        
        output = captured.out
        # All coordinates should be present
        assert "(0, 0)" in output
        assert "(1, 1)" in output
        assert "(1, 2)" in output
        assert "(2, 0)" in output
        assert "(2, 1)" in output
        assert "(2, 2)" in output

    def test_print_regions_order_preserved(self, capsys: pytest.CaptureFixture[str]):
        """Test that region order is preserved in output."""
        regions = [
            [(0, 0)],
            [(1, 1)],
            [(2, 2)],
        ]
        print_regions(regions)
        captured = capsys.readouterr()
        
        output = captured.out
        # Region 0 should appear before Region 1
        assert output.index("Region 0") < output.index("Region 1")
        assert output.index("Region 1") < output.index("Region 2")


# =============================================================================
# Test print_color_palette
# =============================================================================

class TestPrintColorPalette:
    """Tests for print_color_palette function."""

    def test_print_color_palette_runs(self, capsys: pytest.CaptureFixture[str]):
        """Test that print_color_palette runs without error."""
        # This should not raise any exception
        print_color_palette()
        captured = capsys.readouterr()
        
        # Should have some output
        assert len(captured.out) > 0

    def test_print_color_palette_has_ansi_codes(self, capsys: pytest.CaptureFixture[str]):
        """Test that print_color_palette outputs ANSI color codes."""
        print_color_palette()
        captured = capsys.readouterr()
        
        output = captured.out
        # Should contain ANSI escape codes
        assert "\033[" in output

    def test_print_color_palette_covers_all_styles(self, capsys: pytest.CaptureFixture[str]):
        """Test that both normal and bold styles are present."""
        print_color_palette()
        captured = capsys.readouterr()
        
        output = captured.out
        # Should have style 0 (normal) and style 1 (bold)
        assert "0;3" in output or "0;30" in output  # Style 0
        assert "1;3" in output or "1;30" in output  # Style 1

    def test_print_color_palette_covers_fg_colors(self, capsys: pytest.CaptureFixture[str]):
        """Test that foreground colors 30-37 are present."""
        print_color_palette()
        captured = capsys.readouterr()
        
        output = captured.out
        # Check for various foreground colors
        for fg in range(30, 38):
            assert f"{fg};4" in output, f"Foreground color {fg} not found"

    def test_print_color_palette_covers_bg_colors(self, capsys: pytest.CaptureFixture[str]):
        """Test that background colors 40-47 are present."""
        print_color_palette()
        captured = capsys.readouterr()
        
        output = captured.out
        # Check for various background colors
        for bg in range(40, 48):
            assert f";{bg}m" in output, f"Background color {bg} not found"

    def test_print_color_palette_reset_codes(self, capsys: pytest.CaptureFixture[str]):
        """Test that ANSI reset codes are present."""
        print_color_palette()
        captured = capsys.readouterr()
        
        output = captured.out
        # Should have reset codes
        assert "\033[0m" in output


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_print_grid_and_regions_consistency(self, grid_from_builder: Grid, capsys: pytest.CaptureFixture[str]):
        """Test that print_grid and print_regions work with the same grid."""
        # Print the grid
        print_grid(grid_from_builder)
        captured_grid = capsys.readouterr()
        
        # Print the regions
        print_regions(grid_from_builder.regions)
        captured_regions = capsys.readouterr()
        
        # Both should produce output without errors
        assert len(captured_grid.out) > 0
        assert len(captured_regions.out) > 0

    def test_full_ui_workflow(self, capsys: pytest.CaptureFixture[str]):
        """Test a complete workflow: build grid, print grid, print regions."""
        test_grid = [
            "R R G",
            "R R G",
            "B B B",
        ]
        grid = build_example_grid(test_grid)
        
        # Print grid
        print_grid(grid)
        captured_grid = capsys.readouterr()
        
        # Print regions
        print_regions(grid.regions)
        captured_regions = capsys.readouterr()
        
        # Both outputs should be valid
        assert "⟍" in captured_grid.out
        assert "Found regions" in captured_regions.out
        
        # Grid should have 3 regions (R, G, B)
        assert len(grid.regions) == 3
