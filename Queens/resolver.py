# Queens/resolver.py

from warnings import warn

EMPTY = 0
QUEEN = 1
BLOCKED = -1


# DONE
class Cell:
    def __init__(self, coord: tuple, color: str, value: int = 0):
        self.row, self.col = coord
        self.color = color
        self.value = value

    @property
    def coord(self) -> tuple[int, int]:
        return (self.row, self.col)

    def make_queen(self) -> None:
        self.value = QUEEN

    def block_cell(self) -> None:
        self.value = BLOCKED

    def is_empty(self) -> bool:
        return self.value == EMPTY

    def __repr__(self):
        return f"Cell({self.row},{self.col},{self.color},{self.value})"


# DONE
class Grid:
    def __init__(self, grid: list):
        self.grid = grid
        self.regions = self.find_regions()

    def __getitem__(self, index):
        return self.grid[index]

    def __iter__(self):
        return iter(self.grid)

    # DONE
    def find_regions(self) -> list:
        colors = []
        regions = []
        for line in self.grid:
            for cell in line:
                if cell.color not in colors:
                    colors.append(cell.color)
                    regions.append([])
                regions[colors.index(cell.color)].append((cell.row, cell.col))

        return regions

    # DONE
    def claim_region(self, targetCell: Cell) -> None:
        # find the region of the target cell
        region = None
        for regs in self.regions:
            if targetCell.coord in regs:
                region = regs
                break
        if region is None:
            warn(f"No region found for cell {targetCell.coord}")
            return

        for row, col in region:
            cell = self.grid[row][col]
            if cell.coord != targetCell.coord and cell.is_empty():
                cell.block_cell()
        return

    # DONE
    def claim_cell(self, cell: Cell) -> None:
        cell.value = QUEEN
        for row in range(len(self.grid)):
            for column in range(len(self.grid[0])):
                if row == cell.row or column == cell.col:
                    if self.grid[row][column].value == EMPTY:
                        self.grid[row][column].value = BLOCKED
        self.grid[cell.row - 1][cell.col - 1].value = BLOCKED
        self.grid[cell.row - 1][cell.col + 1].value = BLOCKED
        self.grid[cell.row + 1][cell.col - 1].value = BLOCKED
        self.grid[cell.row + 1][cell.col + 1].value = BLOCKED

        self.claim_region(cell)

        return

    # DONE
    def claim_row(self, left: Cell, right: Cell) -> None:
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

            # if the selected cell is on over or under the region
            elif (size == 2 and cell.col in (left.col, right.col)) or (
                size == 3 and cell.col == left.col + 1
            ):
                if left.row != BLOCKED:
                    upperCell = self.grid[left.row - 1][cell.col]
                    if upperCell.value != QUEEN:
                        upperCell.block_cell()
                if left.row != len(self.grid) - 1:
                    lowerCell = self.grid[left.row + 1][cell.col]
                    if lowerCell.value != QUEEN:
                        lowerCell.block_cell()

        return

    # DONE
    def claim_column(self, top: Cell, bottom: Cell) -> None:
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

            # claim all sides of the region if size = 2 on the centers if size = 3
            elif (size == 2 and cell.row in (top.row, bottom.row)) or (
                size == 3 and cell.row == top.row - 1
            ):
                if top.col != BLOCKED:
                    leftCell = row[top.col - 1]
                    if leftCell.value != QUEEN:
                        leftCell.block_cell()
                if top.col != len(row) - 1:
                    rightCell = row[top.col + 1]
                    if rightCell.value != QUEEN:
                        rightCell.block_cell()

        return

    # DONE
    def claim_corner(self, cells: list) -> None:
        if cells[0].row == cells[1].row:
            # ¤ ¤
            # ¤
            if cells[0].col == cells[1].col:
                self.grid[cells[0].row - 1][cells[0].col].block_cell()  # ↑
                self.grid[cells[0].row][cells[0].col - 1].block_cell()  # ←
                self.grid[cells[0].row + 1][cells[0].col + 1].block_cell()  # ↘
            # ¤ ¤
            #   ¤
            else:
                self.grid[cells[1].row - 1][cells[1].col].block_cell()  # ↑
                self.grid[cells[1].row][cells[1].col + 1].block_cell()  # →
                self.grid[cells[1].row + 1][cells[1].col - 1].block_cell()  # ↙
        # ¤
        # ¤ ¤
        elif cells[0].col == cells[1].col:
            self.grid[cells[1].row + 1][cells[1].col].block_cell()  # ↓
            self.grid[cells[1].row][cells[1].col - 1].block_cell()  # ←
            self.grid[cells[1].row - 1][cells[1].col + 1].block_cell()  # ↗
        #   ¤
        # ¤ ¤
        else:
            self.grid[cells[2].row + 1][cells[2].col].block_cell()  # ↓
            self.grid[cells[2].row][cells[2].col + 1].block_cell()  # →
            self.grid[cells[2].row - 1][cells[2].col - 1].block_cell()  # ↖

        return

    # WIP
    def resolve(self) -> None:

        singles = [
            self.grid[row][col]
            for region in self.regions
            if len(region) == 1
            for (row, col) in region
        ]

        duos = [
            (self.grid[r1][c1], self.grid[r2][c2])
            for region in self.regions
            if len(region) == 2
            for (r1, c1), (r2, c2) in [region]
        ]

        trios = [
            [self.grid[r1][c1], self.grid[r2][c2], self.grid[r3][c3]]
            for region in self.regions
            if len(region) == 3
            for (r1, c1), (r2, c2), (r3, c3) in [region]
        ]

        for cell in singles:
            self.claim_cell(cell)

        for duo in duos:
            if duo[0].row == duo[1].row:
                self.claim_row(duo[0], duo[1])
            elif duo[0].col == duo[1].col:
                self.claim_column(duo[0], duo[1])
            else:
                warn("Duo is not aligned in row or column.")

        for trio in trios:
            rows = {cell.row for cell in trio}
            cols = {cell.col for cell in trio}
            if len(rows) == 1:
                self.claim_row(trio[0], trio[2])
            elif len(cols) == 1:
                self.claim_column(trio[0], trio[2])
            else:
                self.claim_corner(trio)

        # One liner/column
        for region in self.regions:
            rows = {cell[0] for cell in region}
            cols = {cell[1] for cell in region}
            if len(rows) == 1:
                self.claim_row(self.grid[region[0][0]][region[0][1]], self.grid[region[-1][0]][region[-1][1]])
            elif len(cols) == 1:
                self.claim_column(self.grid[region[0][0]][region[0][1]], self.grid[region[-1][0]][region[-1][1]])
        return


# DONE
def build_example_grid(testGrid: list) -> Grid:
    """Construit une grid d'exemple à partir d'une représentation ASCII.

    Lettres utilisées dans cet exemple:
    C = cyan, R = red, B = blue, O = orange, G = green
    """

    mapping = {
        "C": "cyan",
        "R": "red",
        "B": "blue",
        "O": "orange",
        "V": "green", # "V" for vert (green in French)
        "Y": "yellow",
        "P": "purple",
        "W": "white",
        "G": "gray",
        "N": "black", # "N" for noir (black in French)
    }

    grid = []
    for r, line in enumerate(testGrid):
        row = []
        for c, token in enumerate(line.split()):
            color = mapping.get(token, "unknown")
            row.append(Cell((r, c), color))
        grid.append(row)

    return Grid(grid)


# DONE
def printGrid(grid: Grid) -> None:
    print("⟍  ", end="")
    for i in range(len(grid.grid)):
        print(f" {i} ", end="")
    print()
    for i, row in enumerate(grid.grid):
        print(f" {i} ", end="")
        for cell in row:
            if cell.color == "red":
                print("\033[1;30;41m", end="")
            elif cell.color == "cyan":
                print("\033[1;30;46m", end="")
            elif cell.color == "blue":
                print("\033[1;30;44m", end="")
            elif cell.color == "orange":
                print("\033[1;30;43m", end="")
            elif cell.color == "green":
                print("\033[1;30;42m", end="")
            elif cell.color == "yellow":
                print("\033[1;30;103m", end="")
            elif cell.color == "purple":
                print("\033[1;30;45m", end="")
            elif cell.color == "gray":
                print("\033[1;30;40m", end="")
            elif cell.color == "black":
                print("\033[1;30;47m", end="")
            else:
                print("\033[0m", end="")

            if cell.value == QUEEN:
                print(" Q ", end="")
            elif cell.value == BLOCKED:
                print(" X ", end="")
            else:
                print(" . ", end="")
            print("\033[0m", end="")
        print("\033[0m ")

    return

# DONE
def printRegions(regions: list) -> None:
    print("Found regions (list of coords per color):")
    for i, region in enumerate(regions):
        print(f"Region {i}: {region}")

# DONE
def print_color_palette() -> None:
    for style in [0, 1]:  # 0: normal, 1: bold/bright
        for fg in range(30, 38):
            for bg in range(40, 48):
                code = f"{style};{fg};{bg}"
                print(f"\033[{code}m {code} \033[0m", end=" ")
            print()  # Newline after each row
        print()  # Extra newline between normal and bold

    return


def main(grid: Grid) -> None:
    if not grid or grid == [[]]:
        print("This is the Queens resolver module.")

    printGrid(grid)

    # printRegions(grid.regions)
    # grid.claim_cell(grid[4][1])
    # grid.claim_column(grid[3][3], grid[4][3])
    # grid.claim_row(grid[5][2], grid[5][4])

    grid.resolve()

    printGrid(grid)


if __name__ == "__main__":
    testGrid = [
        "Y Y Y P W W W",
        "Y Y Y P W W W",
        "Y Y P P P W W",
        "R P P O P P W",
        "R R P O P G G",
        "R R B B B G G",
        "R R R R B G G",
    ]

    testGrid2 = [
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
    example = build_example_grid(testGrid2)
    main(example)
