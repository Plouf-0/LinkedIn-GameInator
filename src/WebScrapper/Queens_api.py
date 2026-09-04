# WebScrapper/Queens_api.py

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from Queens.brute_force_resolver import BruteForceResolver, Cell, Grid
from Queens.queens_archiver import QueensArchiver
from Queens.ui import print_grid

# The time to wait between placing queens in the HTML, in seconds.
# Adjust as needed.
TIME_TO_RESOLVE = 4


def queens_api(driver: webdriver.Firefox) -> None:
    assert "Queens" in driver.title

    grid = BruteForceResolver(create_grid_from_html(driver))
    print_grid(grid.grid)
    grid.resolve_grid()
    print_grid(grid.grid)
    put_queens_in_html(driver, grid)

    while True:
        pass
    return


def create_grid_from_html(driver: webdriver.Firefox) -> list[list[Cell]]:
    grid: list[list[Cell]] = []

    divs: list[WebElement] = driver.find_elements(By.CSS_SELECTOR, "div[aria-label]")
    div: WebElement
    label: str
    for div in divs:
        label = div.get_attribute("aria-label")  # type: ignore
        if "couleur" in label:
            parts = label.split(", ")
            color = parts[0].split("couleur ")[1].split(" ")[0]
            row = int(parts[1].split("ligne ")[1]) - 1
            column = int(parts[2].split("colonne ")[1]) - 1

            while len(grid) <= row:
                grid.append([])
            grid[row].append(Cell(row, column, color))
            grid[row].sort(key=lambda c: c.col)  # type: ignore

    QueensArchiver().archive_game(grid)

    return grid


def put_queens_in_html(driver: webdriver.Firefox, grid: Grid) -> None:
    for row in grid.grid:
        for cell in row:
            if cell.is_queen():
                div = driver.find_element(
                    By.CSS_SELECTOR,
                    f"div[aria-label*='ligne {cell.row + 1}, colonne {cell.col + 1}']",
                )
                div.click()
                div.click()
                time.sleep(TIME_TO_RESOLVE / (len(grid.regions)))
    return
