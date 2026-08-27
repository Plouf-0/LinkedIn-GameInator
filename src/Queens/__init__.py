"""Queens package initialisation.

Expose the primary objects from the package for convenient imports:

        from Queens import Grid, Cell, build_example_grid, QueenResolver

Also expose the `ui` module for printing utilities.
"""

from __future__ import annotations

import logging

from Queens.brute_force_resolver import BruteForceResolver
from Queens.queens_grid import Cell, Grid, build_example_grid
from Queens.ui import print_grid

__all__ = [
    "Grid",
    "Cell",
    "build_example_grid",
    "BruteForceResolver",
    "print_grid",
]

__version__: str = "0.2.0"

# Package logger (users can configure logging as needed)
logger = logging.getLogger(__name__)
