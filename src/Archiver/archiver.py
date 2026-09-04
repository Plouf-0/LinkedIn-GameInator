import os
from abc import ABC, abstractmethod


class Archiver(ABC):
    def __init__(self, archive_name: str = "") -> None:
        """Initialize the Archiver class."""
        self._main_archive_path: str = ""
        self._archive_name: str = archive_name
        self._archive_game_path: str = os.path.join(self._main_archive_path, self._archive_name)

        if archive_name != "":
            self._setup_game_archive()

    def _setup_archive_main_dir(self) -> None:
        """Set up the main archive directory in the user's LOCALAPPDATA folder."""

        localappdata: str | None = os.getenv("LOCALAPPDATA")
        if localappdata is None:
            raise Exception("LOCALAPPDATA environment variable not found")

        self._main_archive_path = os.path.join(localappdata, "LinkedIn-Gameinator")

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
