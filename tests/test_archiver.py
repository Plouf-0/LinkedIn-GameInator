"""Tests for the Archiver base class and the Queens archiver.

Every test runs against a temporary app-data directory, so the suite never
touches (nor leaves anything behind in) the real user profile.
"""

# pyright: reportPrivateUsage=false

from pathlib import Path

import pytest

from Archiver import Archiver
from Archiver.archiver import APP_DIR_NAME, get_app_data_dir, get_app_dir
from Queens.queens_archiver import QueensArchiver
from Queens.queens_grid import Cell, Grid


class _ConcreteArchiver(Archiver):
    """Minimal concrete Archiver used to test the shared base logic."""

    def archive_game(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError


@pytest.fixture(autouse=True)
def app_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the archiver to a throwaway app-data directory."""
    monkeypatch.setattr("Archiver.archiver.get_app_data_dir", lambda: str(tmp_path))
    return tmp_path


# =============================================================================
# Test get_app_data_dir / get_app_dir
# =============================================================================


class TestAppDataDir:
    def test_get_app_data_dir_is_absolute(self, monkeypatch: pytest.MonkeyPatch):
        """The real helper returns an absolute path on every platform."""
        monkeypatch.undo()
        assert Path(get_app_data_dir()).is_absolute()

    def test_get_app_dir_creates_directory(self, app_data_dir: Path):
        """get_app_dir creates the application directory on first call."""
        expected = app_data_dir / APP_DIR_NAME
        assert not expected.exists()
        assert get_app_dir() == expected
        assert expected.is_dir()


# =============================================================================
# Test setup_archive_main_dir
# =============================================================================


class TestArchiver:
    def test_setup_archive_main_dir(self, app_data_dir: Path):
        """Test setup_archive_main_dir"""
        archiver_instance = _ConcreteArchiver()
        archiver_instance._setup_archive_main_dir()

        expected = app_data_dir / APP_DIR_NAME
        assert archiver_instance._main_archive_path == str(expected)
        assert expected.is_dir()

    def test_setup_game_archive(self, app_data_dir: Path):
        """Test setup_game_archive"""
        archiver_instance = _ConcreteArchiver()
        archiver_instance._archive_name = "test_archive"
        archiver_instance._setup_game_archive()

        expected = app_data_dir / APP_DIR_NAME / "test_archive"
        assert archiver_instance._archive_game_path == str(expected)
        assert expected.is_dir()

    def test_named_archiver_sets_up_on_init(self, app_data_dir: Path):
        """Passing a name to the constructor creates the game directory right away."""
        assert (app_data_dir / APP_DIR_NAME / "Queens").is_dir() is False
        QueensArchiver()
        assert (app_data_dir / APP_DIR_NAME / "Queens").is_dir()


# =============================================================================
# Test Create archive
# =============================================================================


class TestCreateArchive:
    def test_create_archive(self, app_data_dir: Path):
        """A fresh archive is created with its header and reports False."""
        archive_instance = QueensArchiver()
        assert archive_instance._create_archive("test_archive_find_create") is False

        path = app_data_dir / APP_DIR_NAME / "Queens" / "test_archive_find_create_Queens.txt"
        assert path.exists()
        assert path.read_text(encoding="utf-8").startswith("Archive of the LinkedIn's game Queens")

    def test_create_archive_twice_reports_existing(self, app_data_dir: Path):
        """Creating the same archive again reports True and leaves it untouched."""
        archive_instance = QueensArchiver()
        archive_instance._create_archive("test_archive")

        path = app_data_dir / APP_DIR_NAME / "Queens" / "test_archive_Queens.txt"
        before = path.read_text(encoding="utf-8")

        assert archive_instance._create_archive("test_archive") is True
        assert path.read_text(encoding="utf-8") == before

    def test_achive_queens_grid(self, all_colors_grid: Grid, app_data_dir: Path):
        """_archive_queens_grid writes the header and the grid."""
        grid: list[list[Cell]] = all_colors_grid.grid
        archive_instance = QueensArchiver()
        archive_instance._archive_queens_grid(grid, "test_archive")

        path = app_data_dir / APP_DIR_NAME / "Queens" / "test_archive_Queens.txt"
        assert path.exists()
        lines = path.read_text(encoding="utf-8").splitlines()

        assert lines == [
            "Archive of the LinkedIn's game Queens on the day of test_archive",
            "Today's grid size is 2x10.",
            "",
            "B C G N O P R V W Y",
            "Y W V R P O N G C B",
        ]

    def test_archive_queens_grid_does_not_duplicate(
        self, all_colors_grid: Grid, app_data_dir: Path
    ):
        """Archiving twice under the same name leaves a single copy of the grid."""
        grid: list[list[Cell]] = all_colors_grid.grid
        archive_instance = QueensArchiver()
        archive_instance._archive_queens_grid(grid, "test_archive")
        archive_instance._archive_queens_grid(grid, "test_archive")

        path = app_data_dir / APP_DIR_NAME / "Queens" / "test_archive_Queens.txt"
        assert len(path.read_text(encoding="utf-8").splitlines()) == 5

    def test_archive_queens_grid_defaults_to_today(self, all_colors_grid: Grid, app_data_dir: Path):
        """With no name given, the archive is named after today's date."""
        from datetime import date

        archive_instance = QueensArchiver()
        archive_instance._archive_queens_grid(all_colors_grid.grid)

        path = app_data_dir / APP_DIR_NAME / "Queens" / f"{date.today()}_Queens.txt"
        assert path.exists()

    def test_archive_game_dispatches(self, all_colors_grid: Grid, app_data_dir: Path):
        """archive_game forwards its arguments to _archive_queens_grid."""
        archive_instance = QueensArchiver()
        archive_instance.archive_game(all_colors_grid.grid, "from_archive_game")

        path = app_data_dir / APP_DIR_NAME / "Queens" / "from_archive_game_Queens.txt"
        assert path.exists()

    def test_archive_game_accepts_keyword_filename(self, all_colors_grid: Grid, app_data_dir: Path):
        """archive_game also accepts the filename as a keyword argument."""
        archive_instance = QueensArchiver()
        archive_instance.archive_game(all_colors_grid.grid, opt_filename="from_kwargs")

        path = app_data_dir / APP_DIR_NAME / "Queens" / "from_kwargs_Queens.txt"
        assert path.exists()
