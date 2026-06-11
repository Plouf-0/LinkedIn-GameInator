# Queens/resolver.py

import logging
from warnings import warn
from typing import List, Set

from .queens_grid import Cell, Grid, build_example_grid

logger = logging.getLogger(__name__)

# Try to import UI helpers from the same folder; prefer relative import when used as a package
try:
    from . import ui  # type: ignore
except Exception:
    import ui  # type: ignore


class BruteForceResolver(Grid):
    """Resolver that uses brute-force backtracking to solve the grid."""

    # DONE
    def _claim_row(self, left: Cell, right: Cell) -> None:
        """Claim cells in the same row of the given left and right cells that are not of the same color as the given left and right cells."""
        if left.row != right.row:
            raise ValueError("Left and right cells must be in the same row.")
        if left.col > right.col:
            left, right = right, left
            warn("Left and right cells were swapped to maintain order.")
        size = abs(left.col - right.col) + 1

        for cell in self.grid[left.row]:

            # if the selected cell is on the left or on the right of the region
            if (cell.col < left.col or cell.col > right.col) and cell.is_empty():
                cell.block_cell()

            # claim all sides of the region if size = 2
            elif size == 2 and cell.col in (left.col, right.col):
                if cell.row != 0:
                    self.grid[cell.row - 1][cell.col].block_cell()
                if cell.row != len(self.grid[0]) - 1:
                    self.grid[cell.row + 1][cell.col].block_cell()
            # claim the centers if size = 3
            elif size == 3 and cell.col == left.col + 1:
                if cell.row != 0:
                    self.grid[cell.row - 1][cell.col].block_cell()
                if cell.row < len(self.grid) - 1:
                    self.grid[cell.row + 1][cell.col].block_cell()
        return

    # DONE
    def _claim_row_parallel(self, cells1: List[Cell], cells2: List[Cell]) -> None:
        """Claim cells in the same row of the cells1 and cells2 that are not of the same color as the given parallel regions."""
        color1 = cells1[0].color
        color2 = cells2[0].color
        rows: Set[int] = {cell.row for cell in cells1}

        for row in rows:
            for cell in self.grid[row]:
                if cell.color != color1 and cell.color != color2:
                    if cell.is_empty():
                        cell.block_cell()
        return

    # DONE
    def _claim_column_parallel(self, cells1: List[Cell], cells2: List[Cell]) -> None:
        """Claim cells in the same column of the cells1 and cells2 that are not of the same color as the given parallel regions."""
        color1 = cells1[0].color
        color2 = cells2[0].color
        cols: Set[int] = {cell.col for cell in cells1}

        for col in cols:
            for cell in self.grid:
                target_cell = cell[col]
                if target_cell.color != color1 and target_cell.color != color2:
                    if target_cell.is_empty():
                        target_cell.block_cell()
        return

    # DONE
    def _claim_column(self, top: Cell, bottom: Cell) -> None:
        """Claim cells in the same column of the given top and bottom cells that are not of the same color as the given top and bottom cells."""
        if top.col != bottom.col:
            raise ValueError("Top and bottom cells must be in the same column.")
        if top.row > bottom.row:
            top, bottom = bottom, top
            warn("Top and bottom cells were swapped to maintain order.")
        size = abs(top.row - bottom.row) + 1

        for row in self.grid:
            cell = row[top.col]

            # if the selected cell is on over or under the region
            if cell.row < top.row or cell.row > bottom.row and cell.is_empty():
                cell.block_cell()

            # claim all sides of the region if size = 2
            elif size == 2 and cell.row in (top.row, bottom.row):
                if cell.col != 0:
                    self.grid[cell.row][cell.col - 1].block_cell()
                if cell.col != len(self.grid[0]) - 1:
                    self.grid[cell.row][cell.col + 1].block_cell()
            # claim the centers if size = 3
            elif size == 3 and cell.row == top.row + 1:
                if cell.col != 0:
                    self.grid[cell.row][cell.col - 1].block_cell()
                if cell.col < len(self.grid[0]) - 1:
                    self.grid[cell.row][cell.col + 1].block_cell()
        return

    # DONE
    def _claim_corner(self, cells: List[Cell]) -> None:
        """Claim cells around the given 3 cells that form a corner that are not of the same color as the given 3 cells."""
        if len(cells) != 3:
            raise ValueError("Exactly 3 cells are required to claim a corner.")

        if cells[0].row == cells[1].row:
            # ¤ ¤
            # ¤
            if cells[0].col == cells[2].col:
                if cells[0].row - 1 >= 0:
                    self.grid[cells[0].row - 1][cells[0].col].block_cell()  # ↑
                if cells[0].col - 1 >= 0:
                    self.grid[cells[0].row][cells[0].col - 1].block_cell()  # ←
                if cells[0].row + 1 < len(self.grid) and cells[0].col + 1 < len(
                    self.grid
                ):
                    self.grid[cells[0].row + 1][cells[0].col + 1].block_cell()  # ↘
            # ¤ ¤
            #   ¤
            else:
                if cells[1].row - 1 >= 0:
                    self.grid[cells[1].row - 1][cells[1].col].block_cell()  # ↑
                if cells[1].col + 1 < len(self.grid):
                    self.grid[cells[1].row][cells[1].col + 1].block_cell()  # →
                if cells[1].row + 1 < len(self.grid) and cells[1].col - 1 >= 0:
                    self.grid[cells[1].row + 1][cells[1].col - 1].block_cell()  # ↙
        # ¤
        # ¤ ¤
        elif cells[0].col == cells[1].col:
            if cells[1].row + 1 < len(self.grid):
                self.grid[cells[1].row + 1][cells[1].col].block_cell()  # ↓
            if cells[1].col - 1 >= 0:
                self.grid[cells[1].row][cells[1].col - 1].block_cell()  # ←
            if cells[1].row - 1 >= 0 and cells[1].col + 1 < len(self.grid):
                self.grid[cells[1].row - 1][cells[1].col + 1].block_cell()  # ↗
        #   ¤
        # ¤ ¤
        else:
            if cells[2].row + 1 < len(self.grid):
                self.grid[cells[2].row + 1][cells[2].col].block_cell()  # ↓
            if cells[2].col + 1 < len(self.grid):
                self.grid[cells[2].row][cells[2].col + 1].block_cell()  # →
            if cells[2].row - 1 >= 0 and cells[2].col - 1 >= 0:
                self.grid[cells[2].row - 1][cells[2].col - 1].block_cell()  # ↖
        return

    # WIP first version for 2 empty-cells regions
    def _claim_parallel(self, regions: List[List[Cell]]) -> None:
        """Claim cells in the same row or column of the given parallel regions that are not of the same color as the given parallel regions."""
        horizontal_regions: List[List[Cell]] = []
        vertical_regions: List[List[Cell]] = []
        for region in regions:
            rows: Set[int] = {cell.row for cell in region}
            cols: Set[int] = {cell.col for cell in region}
            if len(rows) == 2:
                vertical_regions.append(region)
            if len(cols) == 2:
                horizontal_regions.append(region)
        for vertical_region_index in range(len(vertical_regions)):
            for vertical_region_index2 in range(
                vertical_region_index + 1, len(vertical_regions)
            ):
                vertical_region1 = vertical_regions[vertical_region_index]
                vertical_region2 = vertical_regions[vertical_region_index2]
                rows1 = {cell.row for cell in vertical_region1}
                rows2 = {cell.row for cell in vertical_region2}
                if rows1 == rows2:
                    self._claim_row_parallel(vertical_region1, vertical_region2)

        for horizontal_region_index in range(len(horizontal_regions)):
            for horizontal_region_index2 in range(
                horizontal_region_index + 1, len(horizontal_regions)
            ):
                horizontal_region1 = horizontal_regions[horizontal_region_index]
                horizontal_region2 = horizontal_regions[horizontal_region_index2]
                cols1 = {cell.col for cell in horizontal_region1}
                cols2 = {cell.col for cell in horizontal_region2}
                if cols1 == cols2:
                    self._claim_column_parallel(horizontal_region1, horizontal_region2)
        return

    # WIP
    def resolve_grid(self) -> List[List[Cell]]:

        max_iterations = 100

        iteration = 0
        while iteration < max_iterations:
            iteration += 1

            singles: List[Cell] = [
                region.empty_cells[0]
                for region in self.regions
                if region.nb_empty_cells == 1
            ]

            duos: List[list[Cell]] = [
                region.empty_cells
                for region in self.regions
                if region.nb_empty_cells == 2
            ]

            trios: List[List[Cell]] = [
                region.empty_cells
                for region in self.regions
                if region.nb_empty_cells == 3
            ]

            for cell in singles:
                self.queenify_cell(cell)

            for duo in duos:
                if duo[0].row == duo[1].row:
                    self._claim_row(duo[0], duo[1])
                elif duo[0].col == duo[1].col:
                    self._claim_column(duo[0], duo[1])
                else:
                    warn("Duo is not aligned in row or column.")

            for trio in trios:
                rows = {cell.row for cell in trio}
                cols = {cell.col for cell in trio}
                if len(rows) == 1:
                    self._claim_row(trio[0], trio[2])
                elif len(cols) == 1:
                    self._claim_column(trio[0], trio[2])
                else:
                    self._claim_corner(trio)

            # One liner/column
            for region in self.regions:
                if region.is_completed:
                    continue

                rows: Set[int] = {cell.row for cell in region.empty_cells}
                cols: Set[int] = {cell.col for cell in region.empty_cells}
                if len(rows) == 1:
                    self._claim_row(
                        self.grid[region.empty_cells[0].row][region.empty_cells[0].col],
                        self.grid[region.empty_cells[-1].row][
                            region.empty_cells[-1].col
                        ],
                    )
                elif len(cols) == 1:
                    self._claim_column(
                        self.grid[region.empty_cells[0].row][region.empty_cells[0].col],
                        self.grid[region.empty_cells[-1].row][
                            region.empty_cells[-1].col
                        ],
                    )

            empty_cells_regions: List[Grid.Region] = [
                region for region in self.regions
                if region.nb_empty_cells != 0
            ]

            two_rowcol_regions: List[List[Cell]] = []
            for region in empty_cells_regions:
                rows: Set[int] = {cell.row for cell in region.cells}
                cols: Set[int] = {cell.col for cell in region.cells}
                if len(rows) == 2 or len(cols) == 2:
                    two_rowcol_regions.append(region.cells)
            self._claim_parallel(two_rowcol_regions)

            if self.is_grid_finished():
                logger.info("Grid solved!")
                print("Grid solved!")
                break

            if iteration == max_iterations:
                logger.info("Max iterations reached, stopping resolution.")
                print("Max iterations reached, stopping resolution.")

        return self.grid


def QueenResolver(grid: Grid) -> None:
    """Résout et affiche une grille de jeu des reines.

    Fonction principale à appeler depuis le module WebScrapper.
    Affiche la grille initiale, la résout, puis affiche le résultat.

    Args:
        grid: Objet Grid à résoudre et afficher.
    """
    if not grid or not grid.grid:
        print("This is the Queens resolver module.")

    # Use the UI module for printing
    ui.print_grid(grid)
    grid.resolve_grid()
    ui.print_grid(grid)
