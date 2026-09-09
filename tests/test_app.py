"""Tests for the browser flow orchestration in WebScrapper.app."""

import pytest
from pytest_mock import MockerFixture
from selenium.common.exceptions import TimeoutException

from WebScrapper.app import (
    RESOLVERS,
    LinkedInFlowError,
    _hide_google_signin,
    _wait_for_game,
    _wait_for_login,
    resolve_current_game,
)
from WebScrapper.Queens_api import queens_api
from WebScrapper.Sudoku_api import sudoku_api

# =============================================================================
# Test resolve_current_game
# =============================================================================


class TestResolveCurrentGame:
    def test_implemented_games_are_wired_to_their_resolver(self):
        assert RESOLVERS["Queens"] is queens_api
        assert RESOLVERS["Mini Sudoku"] is sudoku_api

    @pytest.mark.parametrize(
        ("name", "title"),
        [("Queens", "Queens n°123 | LinkedIn"), ("Mini Sudoku", "Mini Sudoku n°45 | LinkedIn")],
    )
    def test_dispatches_to_the_matching_resolver(
        self, mocker: MockerFixture, name: str, title: str
    ):
        resolver = mocker.Mock()
        mocker.patch.dict("WebScrapper.app.RESOLVERS", {name: resolver})
        driver = mocker.Mock()

        resolve_current_game(driver, title)

        resolver.assert_called_once_with(driver)

    def test_reports_unimplemented_games(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ):
        resolve_current_game(mocker.Mock(), "Tango n°7 | LinkedIn")

        assert "Tango: resolver not yet implemented" in capsys.readouterr().out

    def test_reports_unknown_games(self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]):
        resolve_current_game(mocker.Mock(), "Feed | LinkedIn")

        assert "Game not recognised" in capsys.readouterr().out


# =============================================================================
# Test the waiting steps
# =============================================================================


class TestWaitSteps:
    def test_wait_for_login_raises_on_timeout(self, mocker: MockerFixture):
        wait = mocker.patch("WebScrapper.app.WebDriverWait")
        wait.return_value.until.side_effect = TimeoutException()

        with pytest.raises(LinkedInFlowError, match="User did not login"):
            _wait_for_login(mocker.Mock())

    def test_wait_for_login_returns_once_logged_in(self, mocker: MockerFixture):
        wait = mocker.patch("WebScrapper.app.WebDriverWait")

        _wait_for_login(mocker.Mock())

        wait.return_value.until.assert_called_once()

    def test_wait_for_game_raises_on_timeout(self, mocker: MockerFixture):
        wait = mocker.patch("WebScrapper.app.WebDriverWait")
        wait.return_value.until.side_effect = TimeoutException()

        with pytest.raises(LinkedInFlowError, match="User did not select a game"):
            _wait_for_game(mocker.Mock())

    def test_wait_for_game_returns_the_title(self, mocker: MockerFixture):
        mocker.patch("WebScrapper.app.WebDriverWait")
        driver = mocker.Mock()
        driver.title = "Queens | LinkedIn"

        assert _wait_for_game(driver) == "Queens | LinkedIn"


# =============================================================================
# Test _hide_google_signin
# =============================================================================


class TestHideGoogleSignin:
    def test_hides_both_overlays(self, mocker: MockerFixture):
        mocker.patch("WebScrapper.app.WebDriverWait")
        driver = mocker.Mock()

        _hide_google_signin(driver)

        assert driver.execute_script.call_count == 2

    def test_a_missing_overlay_is_not_fatal(self, mocker: MockerFixture):
        wait = mocker.patch("WebScrapper.app.WebDriverWait")
        wait.return_value.until.side_effect = TimeoutException()
        driver = mocker.Mock()

        _hide_google_signin(driver)

        driver.execute_script.assert_not_called()
