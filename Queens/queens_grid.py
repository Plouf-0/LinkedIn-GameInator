# Queens/Queens_grid.py

from typing import List
from dataclasses import dataclass

EMPTY = 0
QUEEN = 1
BLOCKED = -1


# DONE
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
        self.value = BLOCKED

    def is_queen(self) -> bool:
        return self.value == QUEEN

    def is_blocked(self) -> bool:
        return self.value == BLOCKED

    def is_empty(self) -> bool:
        return self.value == EMPTY

    def __repr__(self) -> str:
        return f"Cell({self.row},{self.col},{self.color},{self.value})"


# DONE
class Grid:
    """Represents a grid of colored regions and supports queen placement and blocking operations."""

    @dataclass
    class Region:
        """Represents a group of cells sharing the same color within a grid."""

        cells: list[Cell]
        grid: "Grid"

        @property
        def color(self) -> str:
            return self.cells[0].color

        @property
        def empty_cells(self) -> List[Cell]:
            return [cell for cell in self.cells if cell.is_empty()]

        @property
        def nb_empty_cells(self) -> int:
            return len(self.empty_cells)

        @property
        def is_completed(self) -> bool:
            return self.nb_empty_cells == 0

        def block_all_cells(self) -> None:
            for cell in self.cells:
                if cell.is_empty():
                    cell.block_cell()

    def __init__(self, grid: List[List[Cell]]):
        self.grid: List[List[Cell]] = grid
        self.regions: list[Grid.Region] = self._setup_regions()

    def __getitem__(self, coord: tuple[int, int]) -> Cell:
        return self.grid[coord[0]][coord[1]]

    def __iter__(self):
        return iter(self.grid)

    def _get_row(self, row: int) -> list[Cell]:
        return self.grid[row]
    
    def _get_column(self, col: int) -> list[Cell]:
        return [self.grid[r][col] for r in range(len(self.grid))]

    # DONE
    def _setup_regions(self) -> List[Grid.Region]:
        """Identify unique colors in the grid and group cells into regions based on their color"""
        colors: List[str] = []
        regions: List[Grid.Region] = []
        for line in self.grid:
            for cell in line:
                if cell.color not in colors:
                    colors.append(cell.color)
                    regions.append(Grid.Region(cells=[], grid=self))
                regions[colors.index(cell.color)].cells.append(cell)
        return regions

    # DONE
    def get_region_by_cell(self, cell: Cell) -> Grid.Region:
        """Find the region that contains the given cell"""
        for region in self.regions:
            if cell in region.cells:
                return region
        raise ValueError(f"Cell {cell} not found in any region")

    # DONE
    def block_region(self, targetCell: Cell) -> None:
        """Claim the region of the target cell"""
        region: Grid.Region = self.get_region_by_cell(targetCell)
        region.block_all_cells()
        return

    # DONE
    def block_cell_by_coord(self, r: int, c: int) -> None:
        """Block the cell at (r, c) if it's within bounds and not already a queen"""
        if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
            cell = self.grid[r][c]
            if cell.value != QUEEN:
                cell.block_cell()
        return

    # DONE
    def queenify_cell(self, cell: Cell) -> None:
        """Claim the cell as a queen and block all cells in the same row, column, and diagonals"""
        cell.make_queen()
        for row in range(len(self.grid)):
            for column in range(len(self.grid[0])):
                if row == cell.row or column == cell.col:
                    if self.grid[row][column].value == EMPTY:
                        self.grid[row][column].value = BLOCKED

        self.block_cell_by_coord(cell.row - 1, cell.col - 1)
        self.block_cell_by_coord(cell.row - 1, cell.col + 1)
        self.block_cell_by_coord(cell.row + 1, cell.col - 1)
        self.block_cell_by_coord(cell.row + 1, cell.col + 1)
        self.block_region(cell)
        return

    # DONE
    def is_grid_finished(self) -> bool:
        """Check if all regions in the grid are completed (i.e., no empty cells remain)"""
        for region in self.regions:
            if not region.is_completed:
                return False
        return True

    def resolve_grid(self) -> List[List[Cell]]:
        """Placeholder for the grid-solving logic. This method should implement the algorithm to solve the grid based on the rules of the game."""
        return self.grid


# DONE
def build_example_grid(testGrid: list[str]) -> Grid:
    """Construit une grid d'exemple à partir d'une représentation ASCII.

    Lettres utilisées dans cet exemple:
    C = cyan, R = red, B = blue, O = orange, G = green
    """

    mapping = {
        "C": "cyan",
        "R": "red",
        "B": "blue",
        "O": "orange",
        "V": "green",  # "V" for vert (green in French)
        "Y": "yellow",
        "P": "purple",
        "W": "white",
        "G": "gray",
        "N": "black",  # "N" for noir (black in French)
    }

    grid: List[List[Cell]] = []
    for r, line in enumerate(testGrid):
        row: List[Cell] = []
        for c, token in enumerate(line.split()):
            color = mapping.get(token, "unknown")
            row.append(Cell(r, c, color))
        grid.append(row)

    return Grid(grid)
