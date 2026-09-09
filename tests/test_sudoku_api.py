"""Tests for the Sudoku scraping layer.

The attribute parsing is pure; the rest is driven through a mocked driver.
"""

import logging

import pytest
from pytest_mock import MockerFixture

from WebScrapper.Sudoku_api import (
    SudokuGridError,
    click_value_button,
    create_grid_from_html,
    find_board_cell,
    parse_cols_total,
    parse_rows_per_area,
    put_sudoku_in_html,
    sudoku_api,
)


def _cell(mocker: MockerFixture, text: str = "", **attributes: str):
    element = mocker.Mock()
    element.text = text
    element.get_attribute.side_effect = lambda name: attributes.get(name)
    return element


# =============================================================================
# Test attribute parsing
# =============================================================================


class TestParseAttributes:
    @pytest.mark.parametrize(
        ("style", "expected"),
        [
            ("--cols: 6; --rows: 6;", 6),
            ("--rows: 9; --cols: 9", 9),
            ("--cols:4;", 4),
        ],
    )
    def test_parse_cols_total(self, style: str, expected: int):
        assert parse_cols_total(style) == expected

    def test_parse_cols_total_raises_without_a_match(self):
        with pytest.raises(SudokuGridError, match="column count"):
            parse_cols_total("color: red;")

    @pytest.mark.parametrize(
        ("css_class", "expected"),
        [
            ("sudoku-grid sudoku-notes-grid-rows--2", 2),
            ("sudoku-notes-grid-rows--3 sudoku-grid", 3),
        ],
    )
    def test_parse_rows_per_area(self, css_class: str, expected: int):
        assert parse_rows_per_area(css_class) == expected

    def test_parse_rows_per_area_raises_without_a_match(self):
        with pytest.raises(SudokuGridError, match="area height"):
            parse_rows_per_area("sudoku-grid")


# =============================================================================
# Test create_grid_from_html
# =============================================================================


class TestCreateGridFromHtml:
    def test_reads_the_board_row_by_row(self, mocker: MockerFixture):
        driver = mocker.Mock()
        grid_div = _cell(mocker, style="--cols: 4;")
        driver.find_element.return_value = grid_div
        driver.find_elements.return_value = [
            _cell(mocker, text)
            for text in ["1", "", "3", "", "", "4", "", "2", "2", "", "4", "", "", "3", "", "1"]
        ]

        assert create_grid_from_html(driver) == [
            [1, 0, 3, 0],
            [0, 4, 0, 2],
            [2, 0, 4, 0],
            [0, 3, 0, 1],
        ]

    def test_raises_when_the_board_is_empty(self, mocker: MockerFixture):
        driver = mocker.Mock()
        driver.find_element.return_value = _cell(mocker, style="--cols: 4;")
        driver.find_elements.return_value = []

        with pytest.raises(SudokuGridError, match="No Sudoku cell found"):
            create_grid_from_html(driver)


# =============================================================================
# Test put_sudoku_in_html
# =============================================================================


class TestPutSudokuInHtml:
    def test_skips_prefilled_cells(self, mocker: MockerFixture):
        driver = mocker.Mock()
        prefilled = _cell(mocker, **{"class": "sudoku-cell sudoku-cell-prefilled"})
        editable = _cell(mocker, **{"class": "sudoku-cell"})
        mocker.patch(
            "WebScrapper.Sudoku_api.find_board_cell",
            side_effect=[prefilled, editable],
        )
        click_button = mocker.patch("WebScrapper.Sudoku_api.click_value_button")

        put_sudoku_in_html(driver, [[1, 2]])

        prefilled.click.assert_not_called()
        editable.click.assert_called_once()
        click_button.assert_called_once_with(driver, 2)

    def test_counts_only_the_cells_it_filled(
        self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
    ):
        prefilled = _cell(mocker, **{"class": "sudoku-cell sudoku-cell-prefilled"})
        editable = _cell(mocker, **{"class": "sudoku-cell"})
        mocker.patch("WebScrapper.Sudoku_api.find_board_cell", side_effect=[prefilled, editable])
        mocker.patch("WebScrapper.Sudoku_api.click_value_button")

        with caplog.at_level(logging.INFO, logger="WebScrapper.Sudoku_api"):
            put_sudoku_in_html(mocker.Mock(), [[1, 2]])

        assert "Filled 1 of 2 cell(s)" in caplog.text

    def test_warns_when_the_board_was_already_complete(
        self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
    ):
        prefilled = _cell(mocker, **{"class": "sudoku-cell sudoku-cell-prefilled"})
        mocker.patch("WebScrapper.Sudoku_api.find_board_cell", return_value=prefilled)

        with caplog.at_level(logging.WARNING, logger="WebScrapper.Sudoku_api"):
            put_sudoku_in_html(mocker.Mock(), [[1, 2]])

        assert "already filled in" in caplog.text

    def test_a_covered_board_gives_a_readable_error(self, mocker: MockerFixture):
        from selenium.common.exceptions import ElementNotInteractableException

        cell = _cell(mocker, **{"class": "sudoku-cell"})
        cell.click.side_effect = ElementNotInteractableException("not scrolled into view")
        mocker.patch("WebScrapper.Sudoku_api.find_board_cell", return_value=cell)

        with pytest.raises(SudokuGridError, match="already .*finished"):
            put_sudoku_in_html(mocker.Mock(), [[1]])

    def test_raises_when_board_cell_not_found(self, mocker: MockerFixture):
        driver = mocker.Mock()
        mocker.patch("WebScrapper.Sudoku_api.find_board_cell", return_value=None)

        with pytest.raises(SudokuGridError, match="Board cell with index 0 not found"):
            put_sudoku_in_html(driver, [[1]])


# =============================================================================
# Test element lookups
# =============================================================================


class TestElementLookups:
    def test_find_board_cell_matches_on_index(self, mocker: MockerFixture):
        driver = mocker.Mock()
        wanted = _cell(mocker, **{"data-cell-idx": "7"})
        driver.find_elements.return_value = [_cell(mocker, **{"data-cell-idx": "6"}), wanted]

        assert find_board_cell(driver, 7) is wanted

    def test_find_board_cell_returns_none_when_absent(self, mocker: MockerFixture):
        driver = mocker.Mock()
        driver.find_elements.return_value = [_cell(mocker, **{"data-cell-idx": "6"})]

        assert find_board_cell(driver, 7) is None

    def test_click_value_button(self, mocker: MockerFixture):
        driver = mocker.Mock()
        wanted = _cell(mocker, **{"data-number": "5"})
        driver.find_elements.return_value = [_cell(mocker, **{"data-number": "4"}), wanted]

        click_value_button(driver, 5)

        wanted.click.assert_called_once()

    def test_click_value_button_raises_when_absent(self, mocker: MockerFixture):
        driver = mocker.Mock()
        driver.find_elements.return_value = []

        with pytest.raises(SudokuGridError, match="No input button found for value 5"):
            click_value_button(driver, 5)


# =============================================================================
# Test sudoku_api
# =============================================================================


class TestSudokuApi:
    def test_rejects_a_non_sudoku_page(self, mocker: MockerFixture):
        driver = mocker.Mock()
        driver.title = "Queens | LinkedIn"

        with pytest.raises(SudokuGridError, match="Not on a Sudoku page"):
            sudoku_api(driver)

    def test_solves_and_writes_back(self, mocker: MockerFixture):
        driver = mocker.Mock()
        driver.title = "Mini Sudoku | LinkedIn"
        mocker.patch("WebScrapper.Sudoku_api.create_grid_from_html", return_value=[[0, 2], [2, 0]])
        mocker.patch("WebScrapper.Sudoku_api.get_amount_of_rows_by_area", return_value=2)
        solve = mocker.patch("WebScrapper.Sudoku_api.solve", return_value=[[1, 2], [2, 1]])
        put = mocker.patch("WebScrapper.Sudoku_api.put_sudoku_in_html")

        sudoku_api(driver)

        solve.assert_called_once_with([[0, 2], [2, 0]], 2)
        put.assert_called_once_with(driver, [[1, 2], [2, 1]])
