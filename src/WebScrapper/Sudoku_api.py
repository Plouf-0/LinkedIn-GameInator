# WebScrapper/Sudoku_api.py

import logging
import re

from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from Sudoku.sudoku_pl_resolver import solve

logger = logging.getLogger(__name__)

COLS_PATTERN = re.compile(r"--cols:\s*(\d+)")
ROWS_PER_AREA_PATTERN = re.compile(r"sudoku-notes-grid-rows--(\d+)")

CELL_CLASS = "sudoku-cell"
PREFILLED_CLASS = "sudoku-cell-prefilled"

# How long to wait, in seconds, for the board to finish rendering. Generous on
# purpose: it also covers the start screen some games show before the board.
GRID_READY_TIMEOUT = 30


class SudokuGridError(RuntimeError):
    """Raised when the Sudoku grid cannot be read from or written to the page."""


def sudoku_api(driver: webdriver.Firefox) -> None:
    if "Sudoku" not in driver.title:
        raise SudokuGridError(f"Not on a Sudoku page (title: {driver.title!r})")

    grid: list[list[int]] = create_grid_from_html(driver)
    rows_per_area: int = get_amount_of_rows_by_area(driver)
    solved_grid: list[list[int]] = solve(grid, rows_per_area)
    logger.debug("Solution:\n%s", format_grid(solved_grid))

    put_sudoku_in_html(driver, solved_grid)


def parse_cols_total(style: str) -> int:
    """Read the number of columns from the grid's inline `style` attribute."""
    match = COLS_PATTERN.search(style)
    if match is None:
        raise SudokuGridError(f"Could not read the column count from style {style!r}")
    return int(match.group(1))


def parse_rows_per_area(css_class: str) -> int:
    """Read the number of rows per area from the grid's `class` attribute."""
    match = ROWS_PER_AREA_PATTERN.search(css_class)
    if match is None:
        raise SudokuGridError(f"Could not read the area height from class {css_class!r}")
    return int(match.group(1))


def board_is_rendered(driver: webdriver.Firefox, cols_total: int) -> bool:
    """Tell whether the board has finished painting and can be read.

    The game page exists well before its cells do, and a cell's text stays
    empty until it is actually painted. Reading too early yields a board that
    looks blank, which the solver would happily "solve" into an answer
    contradicting the real clues. So the read waits for two things: every cell
    of the board present, and every clue showing its digit.
    """
    cells = driver.find_elements(By.CLASS_NAME, CELL_CLASS)
    if len(cells) != cols_total * cols_total:
        return False

    clues = [cell for cell in cells if PREFILLED_CLASS in (cell.get_attribute("class") or "")]
    return bool(clues) and all(cell.text.strip() for cell in clues)


def wait_for_board(driver: webdriver.Firefox, cols_total: int) -> list[WebElement]:
    """Block until the board is readable, then return its cells."""
    try:
        WebDriverWait(
            driver,
            GRID_READY_TIMEOUT,
            # The board re-renders while it loads, so the elements the condition
            # looked at go stale: that means "not ready yet", not a failure.
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(lambda d: board_is_rendered(d, cols_total))
    except TimeoutException as e:
        raise SudokuGridError(
            f"The {cols_total}x{cols_total} board did not finish loading within "
            f"{GRID_READY_TIMEOUT}s; nothing was read or clicked."
        ) from e

    return driver.find_elements(By.CLASS_NAME, CELL_CLASS)


def check_grid_is_readable(grid: list[list[int]], cols_total: int) -> None:
    """Reject a board read mid-render instead of solving the wrong puzzle.

    A partial read is not harmless: a short board makes the solver work at the
    wrong size, and a board read without its clues has many valid solutions,
    none of which is this puzzle's.
    """
    if not grid:
        raise SudokuGridError("No Sudoku cell found in the page")

    if len(grid) != cols_total or any(len(row) != cols_total for row in grid):
        shape = "x".join(str(len(row)) for row in grid)
        raise SudokuGridError(
            f"Read an incomplete board: expected {cols_total}x{cols_total}, got rows of {shape}"
        )

    if not _clue_count(grid):
        raise SudokuGridError(
            "The board was read without a single clue, so any solution would be a guess. "
            "The page was most likely still loading."
        )


def create_grid_from_html(driver: webdriver.Firefox) -> list[list[int]]:
    grid: list[list[int]] = []

    sudoku_grid_div: WebElement = driver.find_element(By.CLASS_NAME, "sudoku-grid")
    cols_total: int = parse_cols_total(sudoku_grid_div.get_attribute("style") or "")

    cells: list[WebElement] = wait_for_board(driver, cols_total)
    for index, cell in enumerate(cells):
        row: int = index // cols_total

        if len(grid) <= row:
            grid.append([])

        cell_value: str = cell.text.strip()
        grid[row].append(int(cell_value) if cell_value else 0)

    check_grid_is_readable(grid, cols_total)

    logger.info("Read a %dx%d board with %d clue(s).", len(grid), cols_total, _clue_count(grid))
    logger.debug("Board read from the page:\n%s", format_grid(grid))
    return grid


def _clue_count(grid: list[list[int]]) -> int:
    return sum(1 for row in grid for value in row if value)


def format_grid(grid: list[list[int]]) -> str:
    """Render a grid for the logs, dots for the empty cells."""
    return "\n".join(" ".join(str(value) if value else "." for value in row) for row in grid)


def get_amount_of_rows_by_area(driver: webdriver.Firefox) -> int:
    sudoku_grid_div: WebElement = driver.find_element(By.CLASS_NAME, "sudoku-grid")
    return parse_rows_per_area(sudoku_grid_div.get_attribute("class") or "")


def put_sudoku_in_html(driver: webdriver.Firefox, grid: list[list[int]]) -> None:
    index: int = 0
    filled: int = 0
    for row in grid:
        for cell_value in row:
            board_cell: WebElement | None = find_board_cell(driver, index)
            if board_cell is None:
                raise SudokuGridError(f"Board cell with index {index} not found")
            index += 1

            cell_class: str = board_cell.get_attribute("class") or ""
            if PREFILLED_CLASS in cell_class:
                continue

            try:
                board_cell.click()
                click_value_button(driver, cell_value)
            except ElementNotInteractableException as e:
                raise SudokuGridError(
                    "The board cannot be clicked. This usually means the puzzle is already "
                    "finished and its result overlay is covering the grid."
                ) from e
            filled += 1

    logger.info("Filled %d of %d cell(s) in the page.", filled, index)
    if not filled:
        logger.warning("Every cell was already filled in; nothing to do.")


def find_board_cell(driver: webdriver.Firefox, index: int) -> WebElement | None:
    board_cells: list[WebElement] = driver.find_elements(By.CLASS_NAME, CELL_CLASS)

    for cell in board_cells:
        if (cell.get_attribute("data-cell-idx") or "") == str(index):
            return cell
    return None


def click_value_button(driver: webdriver.Firefox, value: int) -> None:
    for button in driver.find_elements(By.CLASS_NAME, "sudoku-input-button"):
        if (button.get_attribute("data-number") or "") == str(value):
            button.click()
            return
    raise SudokuGridError(f"No input button found for value {value}")
