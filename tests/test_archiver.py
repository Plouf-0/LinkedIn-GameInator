"""Tests for Queens.resolver module.

Comprehensive test suite covering:
- Cell class functionality and edge cases
- Grid class methods and edge cases
- Region finding and claiming logic
- Parallel claiming logic
- Resolution algorithm
- Utility functions (build_example_grid, QueenResolver)
"""

# pyright: reportPrivateUsage=false

from pathlib import Path
import warnings
import os

import pytest

from Archiver import Archiver
from Queens.queens_archiver import QueensArchiver
from Queens.queens_grid import Cell, Grid


class _ConcreteArchiver(Archiver):
    """Minimal concrete Archiver used to test the shared base logic."""

    def archive_game(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError


# =============================================================================
# TOTEST Test setup_archive_main_dir
# =============================================================================

class TestArchiver:

    def test_setup_archive_main_dir(self):
        """Test setup_archive_main_dir"""
        localappdata: str | None = os.getenv("LOCALAPPDATA")

        if localappdata is None:
            warnings.warn("LOCALAPPDATA environment variable not found. Skipping test.")
            return

        if os.path.exists(localappdata + "/LinkedIn-Gameinator"):
            warnings.warn("Directory already exists. Skipping test.")

        else:
            archiver_instance = _ConcreteArchiver()
            archiver_instance._setup_archive_main_dir()
            assert archiver_instance._main_archive_path == os.path.join(
                localappdata, "LinkedIn-Gameinator"
            )
            assert os.path.exists(os.path.join(localappdata, "LinkedIn-Gameinator"))

    def test_setup_game_archive(self):
        """Test setup_game_archive"""
        localappdata: str | None = os.getenv("LOCALAPPDATA")

        if localappdata is None:
            warnings.warn("LOCALAPPDATA environment variable not found. Skipping test.")
            return

        archiver_instance = _ConcreteArchiver()
        archiver_instance._archive_name = "test_archive"
        archiver_instance._setup_game_archive()

        assert os.path.exists(
            os.path.join(localappdata, "LinkedIn-Gameinator", "test_archive")
        )

# =============================================================================
# Test Create archive
# =============================================================================


class TestCreateArchive:

    def test_create_archive(self):
        """Test that create_archive runs without error."""
        archive_instance = QueensArchiver()
        archive_instance._create_archive("test_archive_find_create")

        localappdata: str | None = os.getenv("LOCALAPPDATA")
        assert localappdata is not None, "LOCALAPPDATA environment variable is not set."

        assert os.path.exists(
            os.path.join(localappdata, "LinkedIn-Gameinator", "Queens")
        )

        path = Path(
            os.path.join(
                localappdata,
                "LinkedIn-Gameinator",
                "Queens",
                "test_archive_find_create_Queens.txt",
            )
        )
        assert path.exists()

    def test_achive_queens_grid(self, all_colors_grid: Grid):
        """Test that _archive_queens_grid runs without error and creates a file."""
        grid: list[list[Cell]] = all_colors_grid.grid
        archive_instance = QueensArchiver()
        archive_instance._archive_queens_grid(grid, "test_archive")

        localappdata: str | None = os.getenv("LOCALAPPDATA")
        assert localappdata is not None, "LOCALAPPDATA environment variable is not set."

        path = Path(
            os.path.join(
                localappdata,
                "LinkedIn-Gameinator",
                "Queens",
                "test_archive_Queens.txt",
            )
        )
        assert path.exists()
        lines = path.read_text(encoding="utf-8").splitlines()
        path.unlink()

        assert len(lines) == 5
        assert (
            lines[0]
            == "Archive of the LinkedIn's game Queens on the day of test_archive"
        )
        assert lines[1] == "Today's grid size is 2x10."
        assert lines[2] == ""
        assert lines[3] == "B C G N O P R V W Y"
        assert lines[4] == "Y W V R P O N G C B"
