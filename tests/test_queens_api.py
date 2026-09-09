"""Tests for the Queens scraping layer.

The label parsing and the grid assembly are pure enough to be exercised without
a real browser; the driver is replaced by a mock returning canned elements.
"""

import pytest
from pytest_mock import MockerFixture

from Queens.brute_force_resolver import BruteForceResolver
from Queens.queens_grid import Cell, build_example_grid
from WebScrapper.Queens_api import (
    QueensGridError,
    create_grid_from_html,
    find_cell_elements,
    parse_cell_label,
    put_queens_in_html,
    queens_api,
)


def _element(mocker: MockerFixture, label: str):
    element = mocker.Mock()
    element.get_attribute.return_value = label
    return element


# =============================================================================
# Test parse_cell_label
# =============================================================================


class TestParseCellLabel:
    def test_parses_french_label(self):
        cell = parse_cell_label("couleur Rose, ligne 3, colonne 5")
        assert cell == Cell(2, 4, "rose")

    def test_parses_english_label(self):
        cell = parse_cell_label("Pink color, row 3, column 5")
        assert cell == Cell(2, 4, "pink")

    def test_indices_are_zero_based(self):
        cell = parse_cell_label("couleur bleu, ligne 1, colonne 1")
        assert cell is not None
        assert (cell.row, cell.col) == (0, 0)

    @pytest.mark.parametrize(
        "label",
        ["", "Fermer", "ligne 1, colonne 2", "couleur bleu", "Sudoku cell 4"],
    )
    def test_returns_none_for_non_cell_labels(self, label: str):
        assert parse_cell_label(label) is None


# =============================================================================
# Test create_grid_from_html
# =============================================================================


class TestCreateGridFromHtml:
    def test_builds_sorted_grid_and_archives_it(self, mocker: MockerFixture):
        archiver = mocker.patch("WebScrapper.Queens_api.QueensArchiver")
        driver = mocker.Mock()
        # Deliberately out of order, and with one unrelated element in the middle.
        driver.find_elements.return_value = [
            _element(mocker, "couleur bleu, ligne 2, colonne 2"),
            _element(mocker, "Fermer la boîte de dialogue"),
            _element(mocker, "couleur rose, ligne 1, colonne 2"),
            _element(mocker, "couleur bleu, ligne 1, colonne 1"),
            _element(mocker, "couleur rose, ligne 2, colonne 1"),
        ]

        grid = create_grid_from_html(driver)

        assert [[cell.color for cell in row] for row in grid] == [
            ["bleu", "rose"],
            ["rose", "bleu"],
        ]
        assert [[cell.col for cell in row] for row in grid] == [[0, 1], [0, 1]]
        archiver.return_value.archive_game.assert_called_once_with(grid)

    def test_raises_when_no_cell_found(self, mocker: MockerFixture):
        mocker.patch("WebScrapper.Queens_api.QueensArchiver")
        driver = mocker.Mock()
        driver.find_elements.return_value = [_element(mocker, "Fermer")]

        with pytest.raises(QueensGridError, match="No Queens cell found"):
            create_grid_from_html(driver)


# =============================================================================
# Test find_cell_elements / put_queens_in_html
# =============================================================================


class TestPutQueensInHtml:
    def test_find_cell_elements_keys_by_coordinates(self, mocker: MockerFixture):
        driver = mocker.Mock()
        first = _element(mocker, "couleur bleu, ligne 1, colonne 1")
        second = _element(mocker, "Blue color, row 2, column 3")
        driver.find_elements.return_value = [first, _element(mocker, "noise"), second]

        assert find_cell_elements(driver) == {(0, 0): first, (1, 2): second}

    def test_clicks_each_queen_twice(self, mocker: MockerFixture):
        mocker.patch("WebScrapper.Queens_api.time.sleep")
        driver = mocker.Mock()
        elements = {
            (0, 0): mocker.Mock(),
            (1, 1): mocker.Mock(),
        }
        mocker.patch("WebScrapper.Queens_api.find_cell_elements", return_value=elements)

        grid = BruteForceResolver(build_example_grid(["R B", "B R"]))
        grid[0, 0].make_queen()
        grid[1, 1].make_queen()

        put_queens_in_html(driver, grid)

        assert elements[(0, 0)].click.call_count == 2
        assert elements[(1, 1)].click.call_count == 2

    def test_raises_when_target_cell_is_missing(self, mocker: MockerFixture):
        mocker.patch("WebScrapper.Queens_api.time.sleep")
        mocker.patch("WebScrapper.Queens_api.find_cell_elements", return_value={})
        driver = mocker.Mock()

        grid = BruteForceResolver(build_example_grid(["R B", "B R"]))
        grid[0, 0].make_queen()

        with pytest.raises(QueensGridError, match="No cell found at row 1, column 1"):
            put_queens_in_html(driver, grid)

    def test_a_covered_board_gives_a_readable_error(self, mocker: MockerFixture):
        """A finished puzzle hides its grid behind an overlay."""
        from selenium.common.exceptions import ElementNotInteractableException

        mocker.patch("WebScrapper.Queens_api.time.sleep")
        div = mocker.Mock()
        div.click.side_effect = ElementNotInteractableException("not scrolled into view")
        mocker.patch("WebScrapper.Queens_api.find_cell_elements", return_value={(0, 0): div})

        grid = BruteForceResolver(build_example_grid(["R B", "B R"]))
        grid[0, 0].make_queen()

        with pytest.raises(QueensGridError, match="already .*finished"):
            put_queens_in_html(mocker.Mock(), grid)

    def test_does_nothing_without_queens(self, mocker: MockerFixture):
        find = mocker.patch("WebScrapper.Queens_api.find_cell_elements")
        grid = BruteForceResolver(build_example_grid(["R B", "B R"]))

        put_queens_in_html(mocker.Mock(), grid)

        find.assert_not_called()


# =============================================================================
# Test queens_api
# =============================================================================


class TestQueensApi:
    def test_rejects_a_non_queens_page(self, mocker: MockerFixture):
        driver = mocker.Mock()
        driver.title = "Mini Sudoku | LinkedIn"

        with pytest.raises(QueensGridError, match="Not on a Queens page"):
            queens_api(driver)

    def test_does_not_click_when_the_solution_is_invalid(self, mocker: MockerFixture):
        driver = mocker.Mock()
        driver.title = "Queens | LinkedIn"
        # A 2x2 grid can never hold two non-adjacent queens.
        mocker.patch(
            "WebScrapper.Queens_api.create_grid_from_html",
            return_value=build_example_grid(["R R", "G G"]),
        )
        put = mocker.patch("WebScrapper.Queens_api.put_queens_in_html")

        with pytest.raises(QueensGridError, match="did not find a valid solution"):
            queens_api(driver)
        put.assert_not_called()
