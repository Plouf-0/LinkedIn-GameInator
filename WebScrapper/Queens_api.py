# WebScrapper/Queens_api.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from Queens.resolver import Cell, Grid
from Queens.ui import print_grid

from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

def queens_api(driver: webdriver.Firefox) -> None:
    
    grid = create_grid_from_html(driver)
    grid.resolve()
    print_grid(grid)
    return



def create_grid_from_html(driver: webdriver.Firefox) -> Grid:
    assert "Queens" in driver.title

    grid: List[List[Cell]] = []

    divs: list[WebElement] = driver.find_elements(By.CSS_SELECTOR, "div[aria-label]")
    div: WebElement
    label: str
    for div in divs:
        label = div.get_attribute("aria-label") # type: ignore
        if "couleur" in label:

            parts = label.split(', ')
            color = parts[0].split('couleur ')[1].split(' ')[0]
            row = int(parts[1].split('ligne ')[1]) -1
            column = int(parts[2].split('colonne ')[1]) -1

            while len(grid) <= row:
                grid.append([])
            grid[row].append(Cell((row, column), color))
            grid[row].sort(key=lambda c: c.coord[1]) # type: ignore

    return Grid(grid)



testGrid3 = [
    "P P P P P P P P",
    "P V V P P W W P",
    "P V V P P W W P",
    "P P P P P P P P",
    "P P P P P P P P",
    "P R R P P P P P",
    "P R R P P P P P",
    "P P P P P P P P",
]
