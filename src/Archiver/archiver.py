import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path

APP_DIR_NAME = "LinkedIn-Gameinator"


def get_app_data_dir() -> str:
    """Return the per-user application data directory for the current OS."""
    if sys.platform == "win32":
        return os.getenv("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support")
    return os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")


def get_app_dir() -> Path:
    """Return the application's own data directory, creating it if needed."""
    app_dir = Path(get_app_data_dir()) / APP_DIR_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


class Archiver(ABC):
    def __init__(self, archive_name: str = "") -> None:
        """Initialize the Archiver class."""
        self._main_archive_path: str = ""
        self._archive_name: str = archive_name
        self._archive_game_path: str = ""

        if archive_name != "":
            self._setup_game_archive()

    def _setup_archive_main_dir(self) -> None:
        """Set up the main archive directory in the user's app data folder."""
        self._main_archive_path = str(get_app_dir())

    def _setup_game_archive(self) -> None:
        """Set up a game-specific archive directory."""
        if not self._main_archive_path:
            self._setup_archive_main_dir()

        game_path = Path(self._main_archive_path) / self._archive_name
        game_path.mkdir(parents=True, exist_ok=True)
        self._archive_game_path = str(game_path)

    @abstractmethod
    def archive_game(self, *args: object, **kwargs: object) -> None:
        """Implement the game archiving logic to archive the grid based on the game."""
