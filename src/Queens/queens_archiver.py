import logging
from datetime import date as dt
from pathlib import Path
from typing import cast

from Archiver import Archiver
from Queens.queens_grid import Cell, convert_color

logger = logging.getLogger(__name__)


class QueensArchiver(Archiver):
    def __init__(self) -> None:
        """Initialize the QueensArchiver class."""
        super().__init__("Queens")

    def archive_game(self, *args: object, **kwargs: object) -> None:
        """Implement the game archiving logic for the Queens game."""
        grid = cast("list[list[Cell]]", args[0])
        opt_filename = (
            cast(str, args[1]) if len(args) > 1 else cast(str, kwargs.get("opt_filename", ""))
        )
        self._archive_queens_grid(grid, opt_filename)

    def _archive_path(self, filename: str) -> Path:
        """Return the path of the archive file for the given name."""
        return Path(self._archive_game_path) / f"{filename}_Queens.txt"

    def _archive_queens_grid(self, grid: list[list[Cell]], opt_filename: str = "") -> None:
        """Archive the current state of the grid to a text file.

        One file is kept per day; if today's archive already exists the grid is
        not written again.
        """
        filename = opt_filename or str(dt.today())

        if self._create_archive(filename):
            return

        path = self._archive_path(filename)
        rows = [" ".join(convert_color(cell.color) or cell.color for cell in row) for row in grid]
        with path.open("a", encoding="utf-8") as f:
            f.write(f"Today's grid size is {len(grid)}x{len(grid[0])}.\n\n")
            f.write("\n".join(rows) + "\n")

    def _create_archive(self, filename: str) -> bool:
        """Create the archive file with its header if it does not exist yet.

        Output: True if the file already exists, False if it was created.
        """
        path = self._archive_path(filename)

        if path.exists():
            logger.info("Archive %s already exists, skipping.", path.name)
            return True

        with path.open("w", encoding="utf-8") as f:
            f.write(f"Archive of the LinkedIn's game Queens on the day of {filename}\n")
        return False
