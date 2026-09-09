# Queens/Queens_grid.py

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

EMPTY = 0
QUEEN = 1
BLOCKED = -1

# Maps the initial used in archives to every accepted name for that color.
# The first name is the canonical one (what `convert_color` returns for an
# initial); the others are aliases, so that both the French and the English
# LinkedIn interfaces are understood.
COLORS = {
    "B": ["bleu", "blue"],
    "C": ["corail", "red", "coral"],
    "G": ["gris", "gray", "grey"],
    "N": ["beige", "black"],
    "O": ["orange"],
    "P": ["lavande", "purple", "lavender"],
    "R": ["rose", "pink"],
    "V": ["vert", "green"],
    "W": ["white", "blanc"],
    "Y": ["jaune", "yellow"],
}

COLOR_TO_INITIAL = {color: initial for initial, colors in COLORS.items() for color in colors}


@dataclass
class Cell:
    """Represents a grid cell with coordinates, color, and occupancy state.

    Attributes:
        row: int: Row index of the cell.
        col: int: Column index of the cell.
        color: str: Color identifier for the cell's region.
        value: int: Current state of the cell (EMPTY, QUEEN, or BLOCKED).
    """

    row: int
    col: int
    color: str
    value: int = EMPTY

    def make_queen(self) -> None:
        self.value = QUEEN

    def block_cell(self) -> None:
        """Block the cell, unless it already holds a queen.

        Blocking is only ever a deduction ("no queen can go here"), so it must
        never destroy a placement that has already been made.
        """
        if self.value != QUEEN:
            self.value = BLOCKED

    def is_queen(self) -> bool:
        return self.value == QUEEN

    def is_blocked(self) -> bool:
        return self.value == BLOCKED

    def is_empty(self) -> bool:
        return self.value == EMPTY

    def __repr__(self) -> str:
        return f"Cell({self.row},{self.col},{self.color},{self.value})"


class Grid:
    """Represents a grid of colored regions and supports queen placement and blocking operations."""

    @dataclass
    class Region:
        """Represents a group of cells sharing the same color within a grid."""

        cells: list[Cell]

        @property
        def color(self) -> str:
            return self.cells[0].color

        @property
        def empty_cells(self) -> list[Cell]:
            return [cell for cell in self.cells if cell.is_empty()]

        @property
        def nb_empty_cells(self) -> int:
            return len(self.empty_cells)

        @property
        def has_queen(self) -> bool:
            return any(cell.is_queen() for cell in self.cells)

        @property
        def is_dead(self) -> bool:
            """True when the region can no longer receive its queen."""
            return not self.has_queen and self.nb_empty_cells == 0

        @property
        def is_completed(self) -> bool:
            return self.nb_empty_cells == 0

        def block_all_cells(self) -> None:
            for cell in self.cells:
                if cell.is_empty():
                    cell.block_cell()

    def __init__(self, grid: list[list[Cell]]):
        self.grid: list[list[Cell]] = grid
        self._regions_by_color: dict[str, Grid.Region] = {}
        self.regions: list[Grid.Region] = self._setup_regions()

    def __getitem__(self, coord: tuple[int, int]) -> Cell:
        return self.grid[coord[0]][coord[1]]

    def __iter__(self) -> Iterator[list[Cell]]:
        return iter(self.grid)

    @property
    def nb_rows(self) -> int:
        return len(self.grid)

    @property
    def nb_cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def _get_row(self, row: int) -> list[Cell]:
        return self.grid[row]

    def _get_column(self, col: int) -> list[Cell]:
        return [self.grid[r][col] for r in range(len(self.grid))]

    def _setup_regions(self) -> list[Grid.Region]:
        """Identify unique colors in the grid and group cells into regions based on their color"""
        regions: list[Grid.Region] = []
        for line in self.grid:
            for cell in line:
                region = self._regions_by_color.get(cell.color)
                if region is None:
                    region = Grid.Region(cells=[])
                    self._regions_by_color[cell.color] = region
                    regions.append(region)
                region.cells.append(cell)
        return regions

    def get_region_by_cell(self, cell: Cell) -> Grid.Region:
        """Find the region that contains the given cell.

        Lookup is done by color, which is what defines a region, so this is O(1).
        """
        region = self._regions_by_color.get(cell.color)
        if region is None:
            raise ValueError(f"Cell {cell} not found in any region")
        return region

    def block_region(self, targetCell: Cell) -> None:
        """Claim the region of the target cell"""
        region: Grid.Region = self.get_region_by_cell(targetCell)
        region.block_all_cells()
        return

    def block_cell_by_coord(self, r: int, c: int) -> None:
        """Block the cell at (r, c) if it's within bounds and not already a queen"""
        if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
            cell = self.grid[r][c]
            if cell.value != QUEEN:
                cell.block_cell()
        return

    def queenify_cell(self, cell: Cell) -> None:
        """Claim the cell as a queen and block all cells in the same row, column, and diagonals"""
        cell.make_queen()
        for row in range(self.nb_rows):
            for column in range(self.nb_cols):
                if (row == cell.row or column == cell.col) and self.grid[row][column].is_empty():
                    self.grid[row][column].block_cell()

        self.block_cell_by_coord(cell.row - 1, cell.col - 1)
        self.block_cell_by_coord(cell.row - 1, cell.col + 1)
        self.block_cell_by_coord(cell.row + 1, cell.col - 1)
        self.block_cell_by_coord(cell.row + 1, cell.col + 1)
        self.block_region(cell)
        return

    def is_grid_finished(self) -> bool:
        """Check if all regions in the grid are completed (i.e., no empty cells remain).

        This only tells you that there is nothing left to deduce, *not* that the
        grid holds a valid solution. Use `is_solution_valid` for that.
        """
        return all(region.is_completed for region in self.regions)

    @property
    def queens(self) -> list[Cell]:
        """Every cell currently holding a queen."""
        return [cell for row in self.grid for cell in row if cell.is_queen()]

    def is_solution_valid(self) -> bool:
        """Check that the grid holds a complete, legal Queens solution.

        A grid is solved when there is exactly one queen per row, per column and
        per region, and no two queens touch diagonally.
        """
        size = len(self.grid)
        if size == 0:
            return False

        queens = self.queens
        if len(queens) != size:
            return False

        if len({cell.row for cell in queens}) != size:
            return False
        if len({cell.col for cell in queens}) != size:
            return False
        if len({cell.color for cell in queens}) != len(self.regions):
            return False

        for i, first in enumerate(queens):
            for second in queens[i + 1 :]:
                if abs(first.row - second.row) <= 1 and abs(first.col - second.col) <= 1:
                    return False
        return True

    def resolve_grid(self) -> list[list[Cell]]:
        """Placeholder for the grid-solving logic. This method should implement the algorithm
        to solve the grid based on the rules of the game."""
        raise NotImplementedError


def convert_color(value: str) -> str:
    """Convert a color name or initial to its corresponding list of color names."""
    normalized_value: str = value.strip().lower()

    if len(normalized_value) == 1:
        normalized_value = normalized_value.upper()
        color: list[str] = COLORS.get(normalized_value, [])
        return color[0] if len(color) > 0 else ""

    initial = COLOR_TO_INITIAL.get(normalized_value)
    return initial if initial else ""


def build_example_grid(testGrid: list[str]) -> list[list[Cell]]:
    """Build a grid of Cell objects from a list of strings representing the grid layout."""

    grid: list[list[Cell]] = []
    for r, line in enumerate(testGrid):
        row: list[Cell] = []
        for c, token in enumerate(line.split()):
            color = convert_color(token)
            if not color:
                raise ValueError(f"Invalid color token '{token}' at row {r}, column {c}")
            row.append(Cell(r, c, color))
        grid.append(row)

    return grid
