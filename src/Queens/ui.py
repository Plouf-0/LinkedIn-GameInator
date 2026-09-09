import sys

from Queens.queens_grid import BLOCKED, QUEEN, Cell, Grid

RESET = "\033[0m"

# Corner glyph of the coordinates header. A Windows console still defaults to a
# legacy code page that cannot encode it, so fall back to ASCII there rather
# than letting the whole render die on a UnicodeEncodeError.
CORNER = "⟍"
ASCII_CORNER = "\\"

# Background ANSI code used to render each color name. Every alias accepted by
# `Queens.queens_grid.COLORS` is listed so that both the French and the English
# LinkedIn interfaces render identically.
COLOR_ANSI: dict[str, str] = {
    "corail": "\033[1;30;41m",
    "red": "\033[1;30;41m",
    "coral": "\033[1;30;41m",
    "cyan": "\033[1;30;46m",
    "bleu": "\033[1;30;44m",
    "blue": "\033[1;30;44m",
    "orange": "\033[1;30;43m",
    "vert": "\033[1;30;42m",
    "green": "\033[1;30;42m",
    "jaune": "\033[1;30;103m",
    "yellow": "\033[1;30;103m",
    "lavande": "\033[1;30;45m",
    "purple": "\033[1;30;45m",
    "lavender": "\033[1;30;45m",
    "gris": "\033[1;30;40m",
    "gray": "\033[1;30;40m",
    "grey": "\033[1;30;40m",
    "black": "\033[1;30;47m",
    "beige": "\033[1;30;47m",
    "rose": "\033[1;30;105m",
    "pink": "\033[1;30;105m",
    "white": "\033[1;30;107m",
    "blanc": "\033[1;30;107m",
}

# Glyph used to render each cell state.
VALUE_GLYPH: dict[int, str] = {
    QUEEN: " Q ",
    BLOCKED: " X ",
}
EMPTY_GLYPH = " . "


def _corner() -> str:
    """Return the header corner glyph that the current stdout can encode."""
    encoding = getattr(sys.stdout, "encoding", None)
    if not encoding:
        return CORNER
    try:
        CORNER.encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return ASCII_CORNER
    return CORNER


def print_grid(grid: list[list[Cell]]) -> None:
    """Print the grid with ANSI colors.

    Expects a list of rows of `Cell`, each having `.color` and `.value`.
    Unknown colors are rendered without any background.
    """
    print(_corner() + "  ", end="")
    for i in range(len(grid)):
        print(f" {i} ", end="")
    print()
    for i, row in enumerate(grid):
        print(f" {i} ", end="")
        for cell in row:
            print(COLOR_ANSI.get(cell.color, RESET), end="")
            print(VALUE_GLYPH.get(cell.value, EMPTY_GLYPH), end="")
            print(RESET, end="")
        print(RESET + " ")


def print_regions(regions: list[Grid.Region]) -> None:
    print("Found regions (list of coords per color):")
    for i, region in enumerate(regions):
        print(f"Region {i}: {region.cells}")


def print_color_palette() -> None:
    for style in [0, 1]:  # 0: normal, 1: bold/bright
        for fg in range(30, 38):
            for bg in range(40, 48):
                code = f"{style};{fg};{bg}"
                print(f"\033[{code}m {code} {RESET}", end=" ")
            print()  # Newline after each row
        print()  # Extra newline between normal and bold
