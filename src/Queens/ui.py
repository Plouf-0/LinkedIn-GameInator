from datetime import date as dt
from pathlib import Path

from Queens.queens_grid import Cell, convert_color

EMPTY = 0
QUEEN = 1
BLOCKED = -1

ARCHIVE_PATH = Path(__file__).parent / "Archive"


def print_grid(grid: list[list[Cell]]) -> None:
    """Print the grid with ANSI colors.

    Expects an object with attribute `grid: List[List[Cell]]` and `Cell` having
    `.color` and `.value` attributes.
    """
    print("⟍  ", end="")
    for i in range(len(grid)):
        print(f" {i} ", end="")
    print()
    for i, row in enumerate(grid):
        print(f" {i} ", end="")
        for cell in row:
            if cell.color == "corail" or cell.color == "red":
                print("\033[1;30;41m", end="")
            elif cell.color == "cyan":
                print("\033[1;30;46m", end="")
            elif cell.color == "bleu" or cell.color == "blue":
                print("\033[1;30;44m", end="")
            elif cell.color == "orange":
                print("\033[1;30;43m", end="")
            elif cell.color == "vert":
                print("\033[1;30;42m", end="")
            elif cell.color == "jaune" or cell.color == "yellow":
                print("\033[1;30;103m", end="")
            elif cell.color == "lavande" or cell.color == "purple":
                print("\033[1;30;45m", end="")
            elif cell.color == "gris" or cell.color == "gray":
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


def print_regions(regions: list[list[Cell]]) -> None:
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


def find_or_create_archive(filename: str) -> bool:
    """Find the archive file with the given name in the current directory.

    Output: True if the file already exists, False if it was created.
    """
    path = Path(f"{ARCHIVE_PATH}/{filename}_Queens.txt")

    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Archive of the LinkedIn's game Queens on the day of {filename}\n")
        return False
    else:
        print("File already exists.")
        return True


def achive_queens_grid(grid: list[list[Cell]], opt_filename: str = "") -> None:
    """Archive the current state of the grid to a text file."""
    today: str = str(dt.today())

    if opt_filename == "":
        path = Path(f"{ARCHIVE_PATH}/{today}_Queens.txt")
        if find_or_create_archive(today):
            return
    else:
        path = Path(f"{ARCHIVE_PATH}/{opt_filename}_Queens.txt")
        if find_or_create_archive(opt_filename):
            return

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"Today's grid size is {len(grid)}x{len(grid[0])}.\n\n")
        for r in grid:
            row: str = ""
            for cell in r:
                row += convert_color(cell.color) + " "
            f.write(row.strip() + "\n")
    return
