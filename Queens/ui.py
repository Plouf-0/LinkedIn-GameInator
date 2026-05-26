from typing import List, Tuple, TYPE_CHECKING

EMPTY = 0
QUEEN = 1
BLOCKED = -1

if TYPE_CHECKING:
    from .resolver import Grid


def print_grid(grid: "Grid") -> None:
    """Print the grid with ANSI colors.

    Expects an object with attribute `grid: List[List[Cell]]` and `Cell` having
    `.color` and `.value` attributes.
    """
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


def print_regions(regions: List[List[Tuple[int, int]]]) -> None:
    print("Found regions (list of coords per color):")
    for i, region in enumerate(regions):
        print(f"Region {i}: {region}")


def print_color_palette() -> None:
    for style in [0, 1]:  # 0: normal, 1: bold/bright
        for fg in range(30, 38):
            for bg in range(40, 48):
                code = f"{style};{fg};{bg}"
                print(f"\033[{code}m {code} \033[0m", end=" ")
            print()  # Newline after each row
        print()  # Extra newline between normal and bold

    return
