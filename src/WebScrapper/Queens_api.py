# WebScrapper/Queens_api.py

import logging
import re
import time

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from Queens.brute_force_resolver import BruteForceResolver, Cell, Grid
from Queens.queens_archiver import QueensArchiver
from Queens.ui import print_grid

logger = logging.getLogger(__name__)

# Total time budget, in seconds, spread over the queens placed in the page.
TIME_TO_RESOLVE = 4

# LinkedIn labels its cells "couleur <color>, ligne <r>, colonne <c>" in French
# and "<color> color, row <r>, column <c>" in English.
CELL_LABEL_PATTERNS = (
    re.compile(
        r"couleur\s+(?P<color>[^\s,]+).*?ligne\s+(?P<row>\d+).*?colonne\s+(?P<col>\d+)", re.I
    ),
    re.compile(r"(?P<color>[^\s,]+)\s+color.*?row\s+(?P<row>\d+).*?column\s+(?P<col>\d+)", re.I),
)


class QueensGridError(RuntimeError):
    """Raised when the Queens grid cannot be read from or written to the page."""


def queens_api(driver: webdriver.Firefox) -> None:
    if "Queens" not in driver.title:
        raise QueensGridError(f"Not on a Queens page (title: {driver.title!r})")

    grid = BruteForceResolver(create_grid_from_html(driver))
    print_grid(grid.grid)
    grid.resolve_grid()
    print_grid(grid.grid)

    if not grid.is_solution_valid():
        raise QueensGridError("The resolver did not find a valid solution; nothing was clicked.")

    put_queens_in_html(driver, grid)


def parse_cell_label(label: str) -> Cell | None:
    """Parse a LinkedIn cell `aria-label` into a `Cell`.

    Returns None when the label is not a Queens cell. Row and column are
    converted from the 1-based indices used in the page to 0-based indices.
    """
    for pattern in CELL_LABEL_PATTERNS:
        match = pattern.search(label)
        if match:
            return Cell(
                int(match.group("row")) - 1,
                int(match.group("col")) - 1,
                match.group("color").lower(),
            )
    return None


def create_grid_from_html(driver: webdriver.Firefox) -> list[list[Cell]]:
    grid: list[list[Cell]] = []

    divs: list[WebElement] = driver.find_elements(By.CSS_SELECTOR, "div[aria-label]")
    for div in divs:
        cell = parse_cell_label(div.get_attribute("aria-label") or "")
        if cell is None:
            continue

        while len(grid) <= cell.row:
            grid.append([])
        grid[cell.row].append(cell)
        grid[cell.row].sort(key=lambda c: c.col)

    if not grid or not grid[0]:
        raise QueensGridError("No Queens cell found in the page")

    QueensArchiver().archive_game(grid)

    return grid


def find_cell_elements(driver: webdriver.Firefox) -> dict[tuple[int, int], WebElement]:
    """Map each (row, column) of the board to its element, in either language."""
    elements: dict[tuple[int, int], WebElement] = {}
    for div in driver.find_elements(By.CSS_SELECTOR, "div[aria-label]"):
        cell = parse_cell_label(div.get_attribute("aria-label") or "")
        if cell is not None:
            elements[(cell.row, cell.col)] = div
    return elements


def put_queens_in_html(driver: webdriver.Firefox, grid: Grid) -> None:
    queens = grid.queens
    if not queens:
        logger.warning("No queen to place.")
        return

    elements = find_cell_elements(driver)
    delay = TIME_TO_RESOLVE / len(queens)

    for cell in queens:
        div = elements.get((cell.row, cell.col))
        if div is None:
            raise QueensGridError(f"No cell found at row {cell.row + 1}, column {cell.col + 1}")
        try:
            # Two clicks: the first marks the cell, the second turns it into a queen.
            div.click()
            div.click()
        except ElementNotInteractableException as e:
            raise QueensGridError(
                "The board cannot be clicked. This usually means the puzzle is already "
                "finished and its result overlay is covering the grid."
            ) from e
        time.sleep(delay)

    logger.info("Placed %d queen(s) in the page.", len(queens))
