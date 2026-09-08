# WebScrapper/Sudoku_api.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from Sudoku.sudoku_pl_resolver import solve

# The time to wait between placing numbers in the HTML, in seconds.
# Adjust as needed.
TIME_TO_RESOLVE = 4


def sudoku_api(driver: webdriver.Firefox) -> None:
    assert "Sudoku" in driver.title

    grid: list[list[int]] = create_grid_from_html(driver)
    rows_per_area: int = get_amount_of_rows_by_area(driver)
    solved_grid: list[list[int]] = solve(grid, rows_per_area)

    put_sudoku_in_html(driver, solved_grid)
    return


def create_grid_from_html(driver: webdriver.Firefox) -> list[list[int]]:
    grid: list[list[int]] = []

    sudoku_grid_div: WebElement = driver.find_element(By.CLASS_NAME, "sudoku-grid")
    sudoku_grid_div_size: str = sudoku_grid_div.get_attribute("style")  # type: ignore
    cols_total: int = int(sudoku_grid_div_size.split("--cols: ")[1].split()[0].rstrip(";"))

    cells: list[WebElement] = driver.find_elements(By.CLASS_NAME, "sudoku-cell")
    cell: WebElement
    index: int
    for index, cell in enumerate(cells):
        row: int = index // cols_total

        if len(grid) <= row:
            grid.append([])

        cell_value: str = cell.text
        if cell_value == "":
            grid[row].append(0)
        else:
            grid[row].append(int(cell_value))

    # SudokuArchiver().archive_game(grid)

    return grid


def get_amount_of_rows_by_area(driver: webdriver.Firefox) -> int:
    sudoku_grid_div: WebElement = driver.find_element(By.CLASS_NAME, "sudoku-grid")
    sudoku_grid_div_class: str = sudoku_grid_div.get_attribute("class")  # type: ignore
    amount_of_rows_by_area: int = int(
        sudoku_grid_div_class.split("sudoku-notes-grid-rows--")[1].split()[0]
    )
    return amount_of_rows_by_area


def put_sudoku_in_html(driver: webdriver.Firefox, grid: list[list[int]]) -> None:

    index: int = 0
    for row in grid:
        for cell_value in row:
            board_cell: WebElement | None = find_board_cell(driver, index)
            if board_cell is None:
                raise Exception(f"Board cell with index {index} not found")
            index += 1

            cell_class: str = board_cell.get_attribute("class") or ""  # type: ignore
            if "sudoku-cell-prefilled" not in cell_class:
                board_cell.click()
                click_value_button(driver, cell_value)
    return


def find_board_cell(driver: webdriver.Firefox, index: int) -> WebElement | None:
    board_cells: list[WebElement] = driver.find_elements(By.CLASS_NAME, "sudoku-cell")

    for cell in board_cells:
        cell_index: str = cell.get_attribute("data-cell-idx") or ""  # type: ignore
        if cell_index == str(index):
            return cell
    return None


def click_value_button(driver: webdriver.Firefox, value: int) -> None:
    value_button: list[WebElement] = driver.find_elements(By.CLASS_NAME, "sudoku-input-button")
    for button in value_button:
        button_number: str = button.get_attribute("data-number") or ""  # type: ignore
        if button_number == str(value):
            button.click()
            return
