import os
import sys
from abc import ABC, abstractmethod


def get_app_data_dir() -> str:
    """Return the per-user application data directory for the current OS."""
    if sys.platform == "win32":
        return os.getenv("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support")
    return os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")


class Archiver(ABC):
    def __init__(self, archive_name: str = "") -> None:
        """Initialize the Archiver class."""
        self._main_archive_path: str = ""
        self._archive_name: str = archive_name
        self._archive_game_path: str = os.path.join(self._main_archive_path, self._archive_name)

        if archive_name != "":
            self._setup_game_archive()

    def _setup_archive_main_dir(self) -> None:
        """Set up the main archive directory in the user's app data folder."""

        self._main_archive_path = os.path.join(get_app_data_dir(), "LinkedIn-Gameinator")

        if not os.path.exists(self._main_archive_path):
            os.makedirs(self._main_archive_path)

    def _setup_game_archive(self) -> None:
        """Set up a game-specific archive directory."""

        if not os.path.exists(self._main_archive_path) or self._main_archive_path == "":
            self._setup_archive_main_dir()

        self._archive_game_path = os.path.join(self._main_archive_path, self._archive_name)

        if not os.path.exists(self._archive_game_path):
            os.makedirs(self._archive_game_path)

    @abstractmethod
    def archive_game(self, *args: object, **kwargs: object) -> None:
        """Implement the game archiving logic to archive the grid based on the game."""
