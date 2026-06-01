"""Queens package initialisation.

Expose the primary objects from the package for convenient imports:

	from Queens import Grid, Cell, build_example_grid, QueenResolver

Also expose the `ui` module for printing utilities.
"""

from __future__ import annotations

import logging
from typing import Final

from .resolver import Grid, Cell, QueenResolver
from . import ui

__all__ = [
	"Grid",
	"Cell",
	"build_example_grid",
	"QueenResolver",
	"ui",
]

__version__: str = "0.1.0"

# Package logger (users can configure logging as needed)
logger = logging.getLogger(__name__)

