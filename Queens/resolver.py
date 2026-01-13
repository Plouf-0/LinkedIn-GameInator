# Queens/resolver.py


class grid:
    def __init__(self, table: list):
        self.table = table


class Cell:
    def __init__(self, position: tuple, color: str, value: int = 0):
        self.position = position
        self.color = color
        # 0 = empty, 1 = queen, -1 = blocked
        self.value = value


def build_example_table(testGrid) -> list:
    """Construit une table d'exemple à partir d'une représentation ASCII.

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

    table = []
    for r, line in enumerate(testGrid):
        row = []
        for c, token in enumerate(line.split()):
            color = mapping.get(token, "unknown")
            row.append(Cell((r, c), color))
        table.append(row)

    return table


def findRegions(table: list) -> list:
    colors = []
    regions = []
    for line in table:
        for cell in line:
            if cell.color not in colors:
                colors.append(cell.color)
                regions.append([])
            regions[colors.index(cell.color)].append(cell.position)

    return regions


def printRegions(regions: list) -> None:
    print("Found regions (list of positions per color):")
    for i, region in enumerate(regions):
        print(f"Region {i}: {region}")


def claimCell(table: list, cell: Cell) -> None:
    cell.value = 1
    for row in range(len(table)):
        for column in range(len(table[0])):
            if row == cell.position[0] or column == cell.position[1]:
                if table[row][column].value == 0:
                    table[row][column].value = -1
    table[cell.position[0] - 1][cell.position[1] - 1].value = -1
    table[cell.position[0] - 1][cell.position[1] + 1].value = -1
    table[cell.position[0] + 1][cell.position[1] - 1].value = -1
    table[cell.position[0] + 1][cell.position[1] + 1].value = -1
    return


def claimRow(table: list, left: Cell, right: Cell) -> None:
    size = abs(left.position[1] - right.position[1])
    for cell in table[left.position[0]]:
        if cell.position[0] < left.position[0] or cell.position[0] > right.position[0]:
            cell.value = -1

        if cell.position[0] in (left.position[0] - 1, left.position[0] + 1):
            if (size == 2 and cell.position[1] in (left.position[1], right.position[1])) or (
                size == 3 and cell.position[1] == left.position[1] + 1
            ):
                cell.value = -1

    return

def claimRegion(table: list, region: list) -> None:
    for cell in table:
        if cell.position in region:
            cell.value = -1
    return

def printGrid(table: list) -> None:
    for row in table:
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


def main(table: list) -> None:
    if not table or table == [[]]:
        print("This is the Queens resolver module.")

    regions = findRegions(table)
    printRegions(regions)
    claimCell(table, table[4][3])  # Example: claim cell at (3, 3)
    printGrid(table)


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
    example = build_example_table(testGrid)
    main(example)
