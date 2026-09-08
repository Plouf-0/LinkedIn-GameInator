import pytest
from pytest_mock import MockerFixture

from WebScrapper.Sudoku_api import put_sudoku_in_html


def test_put_sudoku_in_html_raises_when_board_cell_not_found(mocker: MockerFixture):
    driver = mocker.Mock()
    mocker.patch("WebScrapper.Sudoku_api.find_board_cell", return_value=None)

    grid = [[1]]

    with pytest.raises(Exception, match="Board cell with index 0 not found"):
        put_sudoku_in_html(driver, grid)
