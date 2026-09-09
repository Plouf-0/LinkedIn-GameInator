# WebScrapper/app.py
import logging
from collections.abc import Callable

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from Archiver.archiver import get_app_dir
from WebScrapper.Queens_api import queens_api
from WebScrapper.Sudoku_api import sudoku_api

logger = logging.getLogger(__name__)

LOGIN_URL = (
    "https://www.linkedin.com/uas/login"
    "?session_redirect=%2Fgames%2F&fromSignIn=true&trk=games_nav-header-signin"
)

# How long to wait, in seconds, for each step of the flow.
PAGE_LOAD_TIMEOUT = 1
LOGIN_TIMEOUT = 600
GAME_SELECTION_TIMEOUT = 600

# Game title fragment -> resolver. Games without a resolver map to None.
RESOLVERS: dict[str, Callable[[webdriver.Firefox], None] | None] = {
    "Mini Sudoku": sudoku_api,
    "Queens": queens_api,
    "Patches": None,
    "Zip": None,
    "Tango": None,
    "Crossclimb": None,
    "Pinpoint": None,
    "Wend": None,
}


class LinkedInFlowError(RuntimeError):
    """Raised when the LinkedIn page does not reach an expected state."""


def _hide_google_signin(driver: webdriver.Firefox) -> None:
    """Hide the Google one-tap overlays that sit on top of the login form.

    Purely cosmetic: a failure here must not stop the run.
    """
    overlays = (
        (By.CLASS_NAME, "alternate-signin-container"),
        (By.ID, "credential_picker_container"),
    )
    scripts = (
        "(document.getElementsByClassName('alternate-signin-container'))[0]"
        ".setAttribute('style', 'visibility: hidden');",
        "document.getElementById('credential_picker_container')"
        ".setAttribute('style', 'visibility: hidden');",
    )

    for locator, script in zip(overlays, scripts, strict=True):
        try:
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.presence_of_element_located(locator))
            driver.execute_script(script)
        except TimeoutException:
            logger.debug("Google sign-in overlay %s not present, nothing to hide.", locator[1])
        except Exception:
            logger.debug("Could not hide the Google sign-in overlay %s.", locator[1])


def _wait_for_login(driver: webdriver.Firefox) -> None:
    """Block until the user has logged in, or raise on timeout."""
    print("Please login your LinkedIn account")
    try:
        WebDriverWait(driver, LOGIN_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "msg-overlay-list-bubble"))
        )
    except TimeoutException as e:
        raise LinkedInFlowError("User did not login") from e
    print("User logged in")


def _wait_for_game(driver: webdriver.Firefox) -> str:
    """Block until a game is opened and return its page title."""
    print("Now select a game to complete")
    try:
        WebDriverWait(driver, GAME_SELECTION_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "clock-small"))
        )
    except TimeoutException as e:
        raise LinkedInFlowError("User did not select a game") from e
    return driver.title


def resolve_current_game(driver: webdriver.Firefox, title: str) -> None:
    """Dispatch to the resolver matching the opened game."""
    for name, resolver in RESOLVERS.items():
        if name in title:
            if resolver is None:
                print(f"{name}: resolver not yet implemented")
                return
            resolver(driver)
            return
    print("Game not recognised")


def main() -> None:
    """Drive the browser flow. Logging is configured by the CLI entry point."""
    get_app_dir()

    driver: webdriver.Firefox = webdriver.Firefox()
    try:
        driver.get(LOGIN_URL)
        if "LinkedIn" not in driver.title:
            raise LinkedInFlowError(f"Unexpected page title: {driver.title!r}")

        _hide_google_signin(driver)
        _wait_for_login(driver)

        while True:
            title = _wait_for_game(driver)
            print("game selected: " + title)
            try:
                resolve_current_game(driver, title)
            except Exception:
                logger.exception("Could not resolve %s.", title)
    except LinkedInFlowError as e:
        logger.error("%s", e)
    except KeyboardInterrupt:
        print("\nInterrupted, closing the browser.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
