import os
from datetime import date as dt
from pathlib import Path
from typing import cast

from Archiver import Archiver
from Queens.queens_grid import Cell, convert_color


class QueensArchiver(Archiver):
    def __init__(
        self,
    ) -> None:
        """Initialize the QueensArchiver class."""
        super().__init__("Queens")

    def archive_game(self, *args: object, **kwargs: object) -> None:
        """Implement the game archiving logic for the Queens game."""
        grid = cast("list[list[Cell]]", args[0])
        opt_filename = (
            cast(str, args[1])
            if len(args) > 1
            else cast(str, kwargs.get("opt_filename", ""))
        )
        self._archive_queens_grid(grid, opt_filename)

    def _archive_queens_grid(
        self, grid: list[list[Cell]], opt_filename: str = ""
    ) -> None:
        """Archive the current state of the grid to a text file."""
        today: str = str(dt.today())

        if opt_filename == "":
            path = Path(f"{self._archive_game_path}/{today}_Queens.txt")
            if self._create_archive(today):
                return
        else:
            path = Path(f"{self._archive_game_path}/{opt_filename}_Queens.txt")
            if self._create_archive(opt_filename):
                return

        with open(path, "a", encoding="utf-8") as f:
            f.write(f"Today's grid size is {len(grid)}x{len(grid[0])}.\n\n")
            for r in grid:
                row: str = ""
                for cell in r:
                    row += convert_color(cell.color) + " "
                f.write(row.strip() + "\n")
        return

    def _create_archive(self, filename: str) -> bool:
        """Create archive if doesn't exists.

        Output: True if the file already exists, False if it was created.
        """
        path = Path(os.path.join(self._archive_game_path, f"{filename}_Queens.txt"))

        if not path.exists():
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    f"Archive of the LinkedIn's game Queens on the day of {filename}\n"
                )
            return False
        else:
            print("File already exists.")
            return True
