# Queens/resolver.py

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

    # TODO: claime region
    def claim_cell(self, cell: Cell) -> None:
        cell.value = 1
        for row in range(len(self.grid)):
            for column in range(len(self.grid[0])):
                if row == cell.row or column == cell.col:
                    if self.grid[row][column].value == 0:
                        self.grid[row][column].value = -1
        self.grid[cell.row - 1][cell.col - 1].value = -1
        self.grid[cell.row - 1][cell.col + 1].value = -1
        self.grid[cell.row + 1][cell.col - 1].value = -1
        self.grid[cell.row + 1][cell.col + 1].value = -1
        return

    # TOTEST
    def claim_row(self, left: Cell, right: Cell) -> None:
        if left.row != right.row:
            raise ValueError("Left and right cells must be in the same row.")
        size = abs(left.col - right.col) + 1

        for cell in self.grid[left.row]:

            # if the selected cell is on the left or on the right of the region
            if cell.row < left.row or cell.row > right.row:
                cell.block_cell()

            # if the selected cell is on over or under the region
            elif (size == 2 and cell.col in (left.col, right.col)) or (
                size == 3 and cell.col == left.col + 1
            ):
                if left.row != 0:
                    upperCell = self.grid[left.row - 1][cell.col]
                    if upperCell.value != 1:
                        upperCell.block_cell()
                if left.row != len(self.grid) - 1:
                    lowerCell = self.grid[left.row + 1][cell.col]
                    if lowerCell.value != 1:
                        lowerCell.block_cell()

        return

    # TOTEST
    def claim_column(self, top: Cell, bottom: Cell) -> None:
        if top.col != bottom.col:
            raise ValueError("Top and bottom cells must be in the same column.")
        size = abs(top.row - bottom.row) + 1

        for row in self.grid:
            cell = row[top.col]

            # if the selected cell is on over or under the region
            if cell.row < top.row or cell.row > bottom.row:
                cell.block_cell()

            # claim all sides of the region if size = 2 on the centers if size = 3
            elif (size == 2 and cell.row in (top.row, bottom.row)) or (
                size == 3 and cell.row == top.row - 1
            ):
                if top.col != 0:
                    leftCell = row[top.col - 1]
                    if leftCell.value != 1:
                        leftCell.block_cell()
                if top.col != len(row) - 1:
                    rightCell = row[top.col + 1]
                    if rightCell.value != 1:
                        rightCell.block_cell()

        return

    # DONE
    def claim_region(self, region: list) -> None:
        for row in self.grid:
            for cell in row:
                if cell.coord in region and cell.is_empty():
                    cell.block_cell()
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
        "G": "green",
        "Y": "yellow",
        "P": "purple",
        "W": "white",
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
    for row in grid:
        for cell in row:
            if cell.color == "red":
                print("\033[41m", end="")
            elif cell.color == "cyan":
                print("\033[46m", end="")
            elif cell.color == "blue":
                print("\033[44m", end="")
            elif cell.color == "orange":
                print("\033[43m", end="")
            elif cell.color == "green":
                print("\033[42m", end="")
            elif cell.color == "yellow":
                print("\033[103m", end="")
            elif cell.color == "purple":
                print("\033[45m", end="")
            elif cell.color == "white":
                print("\033[40m", end="")
            else:
                print("\033[90m", end="")

            if cell.value == 1:
                print(" Q ", end="")
            elif cell.value == -1:
                print(" X ", end="")
            else:
                print(" . ", end="")
            print("\033[90m", end="")
        print("\033[90m")


# DONE
def printRegions(regions: list) -> None:
    print("Found regions (list of coords per color):")
    for i, region in enumerate(regions):
        print(f"Region {i}: {region}")


def main(grid: Grid) -> None:
    if not grid or grid == [[]]:
        print("This is the Queens resolver module.")

    regions = grid.find_regions()
    printRegions(regions)
    # grid.claimCell(grid[4][3])
    grid.claim_column(grid[3][3], grid[4][3])
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
    example = build_example_grid(testGrid)
    main(example)
