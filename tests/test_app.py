"""Tests for the browser flow orchestration in WebScrapper.app."""

import pytest
from pytest_mock import MockerFixture
from selenium.common.exceptions import TimeoutException

from WebScrapper import app
from WebScrapper.app import (
    RESOLVERS,
    LinkedInFlowError,
    _enter_game_frame,
    _hide_google_signin,
    _open_game_name,
    _wait_for_game,
    _wait_for_login,
    _wait_until_game_left,
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

    def test_wait_for_game_enters_the_frame_and_returns_the_url(self, mocker: MockerFixture):
        """The URL is the handle used later to detect leaving the game."""
        mocker.patch("WebScrapper.app.WebDriverWait")
        enter = mocker.patch("WebScrapper.app._enter_game_frame")
        driver = mocker.Mock()
        driver.current_url = "https://www.linkedin.com/games/queens/"

        assert _wait_for_game(driver) == "https://www.linkedin.com/games/queens/"
        enter.assert_called_once_with(driver)

    def test_a_missing_game_frame_is_not_fatal(self, mocker: MockerFixture):
        wait = mocker.patch("WebScrapper.app.WebDriverWait")
        wait.return_value.until.side_effect = TimeoutException()

        _enter_game_frame(mocker.Mock())

    def test_wait_until_game_left_waits_for_the_url_to_change(self, mocker: MockerFixture):
        wait = mocker.patch("WebScrapper.app.WebDriverWait")
        url_changes = mocker.patch("WebScrapper.app.EC.url_changes")
        driver = mocker.Mock()

        _wait_until_game_left(driver, "https://www.linkedin.com/games/queens/")

        driver.switch_to.default_content.assert_called_once()
        url_changes.assert_called_once_with("https://www.linkedin.com/games/queens/")
        wait.return_value.until.assert_called_once()

    def test_wait_until_game_left_raises_on_timeout(self, mocker: MockerFixture):
        wait = mocker.patch("WebScrapper.app.WebDriverWait")
        wait.return_value.until.side_effect = TimeoutException()

        with pytest.raises(LinkedInFlowError, match="stayed on the same game"):
            _wait_until_game_left(mocker.Mock(), "https://www.linkedin.com/games/queens/")


# =============================================================================
# Test _open_game_name
# =============================================================================


class TestOpenGameName:
    @pytest.mark.parametrize(
        ("url", "title", "expected"),
        [
            ("https://www.linkedin.com/games/queens/", "Queens | LinkedIn", "Queens"),
            (
                "https://www.linkedin.com/games/mini-sudoku/",
                "Mini Sudoku | LinkedIn",
                "Mini Sudoku",
            ),
            ("https://www.linkedin.com/games/", "Games | LinkedIn", None),
            ("https://www.linkedin.com/feed/", "Queens | LinkedIn", None),
        ],
    )
    def test_detects_a_game_from_its_url_and_title(
        self, mocker: MockerFixture, url: str, title: str, expected: str | None
    ):
        driver = mocker.Mock()
        driver.current_url = url
        driver.title = title

        assert _open_game_name(driver) == expected


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


# =============================================================================
# Test the main loop
# =============================================================================


class TestMainLoop:
    """The loop must move on after each game instead of re-solving it."""

    @staticmethod
    def _driver(mocker: MockerFixture):
        driver = mocker.Mock()
        driver.title = "Queens | LinkedIn"
        mocker.patch("WebScrapper.app.webdriver.Firefox", return_value=driver)
        mocker.patch("WebScrapper.app.get_app_dir")
        mocker.patch("WebScrapper.app._hide_google_signin")
        mocker.patch("WebScrapper.app._wait_for_login")
        return driver

    def test_waits_for_the_page_to_change_before_the_next_game(self, mocker: MockerFixture):
        driver = self._driver(mocker)
        # The loop is bounded here, not by the assertions: a version that never
        # waits would otherwise hang the suite instead of failing it.
        mocker.patch(
            "WebScrapper.app._wait_for_game",
            side_effect=[mocker.Mock(), mocker.Mock(), LinkedInFlowError("stop")],
        )
        resolve = mocker.patch("WebScrapper.app.resolve_current_game")
        left = mocker.patch("WebScrapper.app._wait_until_game_left")

        app.main()

        assert resolve.call_count == 2
        assert left.call_count == 2, "each finished game must be waited out"
        driver.quit.assert_called_once()

    def test_a_failing_game_does_not_spin(self, mocker: MockerFixture):
        """A resolver blowing up must still wait, not retry immediately."""
        self._driver(mocker)
        mocker.patch(
            "WebScrapper.app._wait_for_game",
            side_effect=[mocker.Mock(), LinkedInFlowError("stop")],
        )
        resolve = mocker.patch(
            "WebScrapper.app.resolve_current_game",
            side_effect=RuntimeError("board is covered"),
        )
        left = mocker.patch("WebScrapper.app._wait_until_game_left")

        app.main()

        assert resolve.call_count == 1
        left.assert_called_once(), "a failed game must be waited out too"

    def test_the_browser_is_closed_on_interrupt(self, mocker: MockerFixture):
        driver = self._driver(mocker)
        mocker.patch("WebScrapper.app._wait_for_game", side_effect=KeyboardInterrupt)

        app.main()

        driver.quit.assert_called_once()
