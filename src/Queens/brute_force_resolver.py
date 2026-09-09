# Queens/resolver.py

import logging
from warnings import warn

from Queens.queens_grid import Cell, Grid
from Queens.ui import print_grid

logger = logging.getLogger(__name__)

# Upper bound on constraint-propagation passes. The propagation is monotonic
# (it only ever fills cells in), so it always converges well before this; the
# limit only guards against a rule that would never reach a fixed point.
MAX_ITERATIONS = 100


class BruteForceResolver(Grid):
    """Resolver that solves the grid by iterated constraint propagation.

    It applies the usual Queens deductions (single-cell regions, aligned pairs
    and triples, corners, parallel regions) until nothing changes. It does not
    backtrack, so a grid that requires a guess is left unfinished rather than
    solved -- check `is_solution_valid()` before trusting the result.
    """

    def __init__(self, grid: list[list[Cell]]):
        super().__init__(grid)

    # DONE
    def _block_row(self, left: Cell, right: Cell) -> None:
        """Block the cells outside of the row selected by two cells in the same region

        Example :
        ```
        grid._block_row(grid[1, 2], grid[1, 5])
        0 . . . . . . . .
        1 X X R R R R X X
        2 . . . . . . . .
        ```
        Note :
        Special case for size 2 and 3.
        """
        if left.row != right.row:
            raise ValueError("Left and right cells must be in the same row.")
        if left.col > right.col:
            left, right = right, left
            warn("Left and right cells were swapped to maintain order.", stacklevel=2)
        size = abs(left.col - right.col) + 1

        for cell in self.grid[left.row]:
            # if the selected cell is on the left or on the right of the region
            if (
                (cell.col < left.col or cell.col > right.col)
                and cell.is_empty()
                and cell.color != left.color
            ):
                cell.block_cell()

            # claim all sides of the region if size = 2
            elif size == 2 and cell.col in (left.col, right.col):
                if cell.row != 0 and self.grid[cell.row - 1][cell.col].color != left.color:
                    self.grid[cell.row - 1][cell.col].block_cell()
                if (
                    cell.row != self.nb_rows - 1
                    and self.grid[cell.row + 1][cell.col].color != left.color
                ):
                    self.grid[cell.row + 1][cell.col].block_cell()
            # claim the centers if size = 3
            elif size == 3 and cell.col == left.col + 1:
                if cell.row != 0 and self.grid[cell.row - 1][cell.col].color != left.color:
                    self.grid[cell.row - 1][cell.col].block_cell()
                if (
                    cell.row < self.nb_rows - 1
                    and self.grid[cell.row + 1][cell.col].color != left.color
                ):
                    self.grid[cell.row + 1][cell.col].block_cell()
        return

    # DONE
    def _block_row_parallel(self, cells1: list[Cell], cells2: list[Cell]) -> None:
        """Block cells in the same row of the cells1 and cells2
        that are not of the same color as the given parallel regions.

        Example :
        ```
        cells1 = [cell[1, 1], cell[2, 1]]
        cells2 = [cell[1, 5], cell[2, 5]]
        grid._block_row_parallel(cells1, cells2)
        0 . . . . . . .
        1 X R X X X B X
        2 X R X X X B X
        3 . . . . . . .
        ```
        """
        color1 = cells1[0].color
        color2 = cells2[0].color
        rows: set[int] = {cell.row for cell in cells1}

        for row in rows:
            for cell in self.grid[row]:
                if cell.is_empty() and cell.color not in (color1, color2):
                    cell.block_cell()
        return

    # DONE
    def _block_column_parallel(self, cells1: list[Cell], cells2: list[Cell]) -> None:
        """Block cells in the same column of the cells1 and cells2
        that are not of the same color as the given parallel regions.

        Example :
        ```
        cells1 = [cell[1, 1], cell[1, 2]]
        cells2 = [cell[4, 1], cell[4, 2]]
        grid._block_column_parallel(cells1, cells2)
        0 1 2 3
        . X X .
        . R R .
        . X X .
        . X X .
        . B B .
        . X X .
        ```
        """
        color1 = cells1[0].color
        color2 = cells2[0].color
        cols: set[int] = {cell.col for cell in cells1}

        for col in cols:
            for cell in self.grid:
                target_cell = cell[col]
                if target_cell.is_empty() and target_cell.color not in (color1, color2):
                    target_cell.block_cell()
        return

    # DONE
    def _block_column(self, top: Cell, bottom: Cell) -> None:
        """Block cells in the same column of the given top and bottom cells
        that are not of the same color as the given top and bottom cells.

        Example :
        ```
        grid._block_column(grid[2, 1], grid[3, 1])
        0 1 2
        . X .
        . X .
        . R .
        . R .
        . X .
        . X .
        ```
        Note :
        Special case for size 2 and 3.
        """
        if top.col != bottom.col:
            raise ValueError("Top and bottom cells must be in the same column.")
        if top.row > bottom.row:
            top, bottom = bottom, top
            warn("Top and bottom cells were swapped to maintain order.", stacklevel=2)
        size = abs(top.row - bottom.row) + 1

        for row in self.grid:
            cell = row[top.col]

            # if the selected cell is on over or under the region
            if (
                (cell.row < top.row or cell.row > bottom.row)
                and cell.is_empty()
                and cell.color != top.color
            ):
                cell.block_cell()

            # claim all sides of the region if size = 2
            elif size == 2 and cell.row in (top.row, bottom.row):
                if cell.col != 0 and self.grid[cell.row][cell.col - 1].color != top.color:
                    self.grid[cell.row][cell.col - 1].block_cell()
                if (
                    cell.col != self.nb_cols - 1
                    and self.grid[cell.row][cell.col + 1].color != top.color
                ):
                    self.grid[cell.row][cell.col + 1].block_cell()
            # claim the centers if size = 3
            elif size == 3 and cell.row == top.row + 1:
                if cell.col != 0 and self.grid[cell.row][cell.col - 1].color != top.color:
                    self.grid[cell.row][cell.col - 1].block_cell()
                if (
                    cell.col < self.nb_cols - 1
                    and self.grid[cell.row][cell.col + 1].color != top.color
                ):
                    self.grid[cell.row][cell.col + 1].block_cell()
        return

    # DONE
    def _claim_corner(self, cells: list[Cell]) -> None:
        """Claim cells around the given 3 cells that form a corner
        that are not of the same color as the given 3 cells."""
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
                if cells[0].row + 1 < self.nb_rows and cells[0].col + 1 < self.nb_cols:
                    self.grid[cells[0].row + 1][cells[0].col + 1].block_cell()  # ↘
            # ¤ ¤
            #   ¤
            else:
                if cells[1].row - 1 >= 0:
                    self.grid[cells[1].row - 1][cells[1].col].block_cell()  # ↑
                if cells[1].col + 1 < self.nb_cols:
                    self.grid[cells[1].row][cells[1].col + 1].block_cell()  # →
                if cells[1].row + 1 < self.nb_rows and cells[1].col - 1 >= 0:
                    self.grid[cells[1].row + 1][cells[1].col - 1].block_cell()  # ↙
        # ¤
        # ¤ ¤
        elif cells[0].col == cells[1].col:
            if cells[1].row + 1 < self.nb_rows:
                self.grid[cells[1].row + 1][cells[1].col].block_cell()  # ↓
            if cells[1].col - 1 >= 0:
                self.grid[cells[1].row][cells[1].col - 1].block_cell()  # ←
            if cells[1].row - 1 >= 0 and cells[1].col + 1 < self.nb_cols:
                self.grid[cells[1].row - 1][cells[1].col + 1].block_cell()  # ↗
        #   ¤
        # ¤ ¤
        else:
            if cells[2].row + 1 < self.nb_rows:
                self.grid[cells[2].row + 1][cells[2].col].block_cell()  # ↓
            if cells[2].col + 1 < self.nb_cols:
                self.grid[cells[2].row][cells[2].col + 1].block_cell()  # →
            if cells[2].row - 1 >= 0 and cells[2].col - 1 >= 0:
                self.grid[cells[2].row - 1][cells[2].col - 1].block_cell()  # ↖
        return

    # WIP first version for 2 empty-cells regions
    def _claim_parallel(self, regions: list[list[Cell]]) -> None:
        """Claim cells in the same row or column of the given parallel regions
        that are not of the same color as the given parallel regions."""
        horizontal_regions: list[list[Cell]] = []
        vertical_regions: list[list[Cell]] = []
        for region in regions:
            rows: set[int] = {cell.row for cell in region}
            cols: set[int] = {cell.col for cell in region}
            if len(rows) == 2:
                vertical_regions.append(region)
            if len(cols) == 2:
                horizontal_regions.append(region)
        for vertical_region_index in range(len(vertical_regions)):
            for vertical_region_index2 in range(vertical_region_index + 1, len(vertical_regions)):
                vertical_region1 = vertical_regions[vertical_region_index]
                vertical_region2 = vertical_regions[vertical_region_index2]
                rows1 = {cell.row for cell in vertical_region1}
                rows2 = {cell.row for cell in vertical_region2}
                if rows1 == rows2:
                    self._block_row_parallel(vertical_region1, vertical_region2)

        for horizontal_region_index in range(len(horizontal_regions)):
            for horizontal_region_index2 in range(
                horizontal_region_index + 1, len(horizontal_regions)
            ):
                horizontal_region1 = horizontal_regions[horizontal_region_index]
                horizontal_region2 = horizontal_regions[horizontal_region_index2]
                cols1 = {cell.col for cell in horizontal_region1}
                cols2 = {cell.col for cell in horizontal_region2}
                if cols1 == cols2:
                    self._block_column_parallel(horizontal_region1, horizontal_region2)
        return

    def resolve_grid(self) -> list[list[Cell]]:
        """Run constraint propagation until the grid stops changing.

        Returns the grid, solved or not; call `is_solution_valid()` to know
        which. Progress is reported through the module logger, not printed.
        """
        for iteration in range(1, MAX_ITERATIONS + 1):
            singles: list[Cell] = [
                region.empty_cells[0] for region in self.regions if region.nb_empty_cells == 1
            ]

            duos: list[list[Cell]] = [
                region.empty_cells for region in self.regions if region.nb_empty_cells == 2
            ]

            trios: list[list[Cell]] = [
                region.empty_cells for region in self.regions if region.nb_empty_cells == 3
            ]

            for cell in singles:
                self.queenify_cell(cell)

            for duo in duos:
                if duo[0].row == duo[1].row:
                    self._block_row(duo[0], duo[1])
                elif duo[0].col == duo[1].col:
                    self._block_column(duo[0], duo[1])
                else:
                    warn("Duo is not aligned in row or column.", stacklevel=2)

            for trio in trios:
                rows: set[int] = {cell.row for cell in trio}
                cols: set[int] = {cell.col for cell in trio}
                if len(rows) == 1:
                    self._block_row(trio[0], trio[2])
                elif len(cols) == 1:
                    self._block_column(trio[0], trio[2])
                elif len(rows) == 2 and len(cols) == 2:
                    self._claim_corner(trio)

            two_row_regions: list[Grid.Region] = []
            two_col_regions: list[Grid.Region] = []
            for region in self.regions:
                if region.is_completed:
                    continue

                rows = {cell.row for cell in region.empty_cells}
                cols = {cell.col for cell in region.empty_cells}
                if len(rows) == 1:
                    self._block_row(
                        self.grid[region.empty_cells[0].row][region.empty_cells[0].col],
                        self.grid[region.empty_cells[-1].row][region.empty_cells[-1].col],
                    )
                elif len(cols) == 1:
                    self._block_column(
                        self.grid[region.empty_cells[0].row][region.empty_cells[0].col],
                        self.grid[region.empty_cells[-1].row][region.empty_cells[-1].col],
                    )

                if len(rows) == 2:
                    two_row_regions.append(region)
                if len(cols) == 2:
                    two_col_regions.append(region)

            for region in two_row_regions:
                rows = {cell.row for cell in region.empty_cells}
                for other_region in two_row_regions:
                    if region is other_region:
                        continue
                    other_rows: set[int] = {cell.row for cell in other_region.empty_cells}
                    if rows == other_rows:
                        self._block_row_parallel(
                            [region.empty_cells[0], region.empty_cells[-1]],
                            [other_region.empty_cells[0], other_region.empty_cells[-1]],
                        )

            for region in two_col_regions:
                cols = {cell.col for cell in region.empty_cells}
                for other_region in two_col_regions:
                    if region is other_region:
                        continue
                    other_cols: set[int] = {cell.col for cell in other_region.empty_cells}
                    if cols == other_cols:
                        self._block_column_parallel(
                            [region.empty_cells[0], region.empty_cells[-1]],
                            [other_region.empty_cells[0], other_region.empty_cells[-1]],
                        )

            if self.is_grid_finished():
                if self.is_solution_valid():
                    logger.info("Grid solved in %d iteration(s).", iteration)
                else:
                    logger.warning(
                        "Propagation converged in %d iteration(s) but the result "
                        "is not a valid solution.",
                        iteration,
                    )
                break

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("State after iteration %d:", iteration)
                print_grid(self.grid)
        else:
            logger.warning("Max iterations (%d) reached, stopping resolution.", MAX_ITERATIONS)

        return self.grid
