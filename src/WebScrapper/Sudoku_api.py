# WebScrapper/Sudoku_api.py

import logging
import re

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from Sudoku.sudoku_pl_resolver import solve

logger = logging.getLogger(__name__)

COLS_PATTERN = re.compile(r"--cols:\s*(\d+)")
ROWS_PER_AREA_PATTERN = re.compile(r"sudoku-notes-grid-rows--(\d+)")


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


def create_grid_from_html(driver: webdriver.Firefox) -> list[list[int]]:
    grid: list[list[int]] = []

    sudoku_grid_div: WebElement = driver.find_element(By.CLASS_NAME, "sudoku-grid")
    cols_total: int = parse_cols_total(sudoku_grid_div.get_attribute("style") or "")

    cells: list[WebElement] = driver.find_elements(By.CLASS_NAME, "sudoku-cell")
    for index, cell in enumerate(cells):
        row: int = index // cols_total

        if len(grid) <= row:
            grid.append([])

        cell_value: str = cell.text
        grid[row].append(int(cell_value) if cell_value else 0)

    if not grid:
        raise SudokuGridError("No Sudoku cell found in the page")

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
            if "sudoku-cell-prefilled" in cell_class:
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
    board_cells: list[WebElement] = driver.find_elements(By.CLASS_NAME, "sudoku-cell")

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
