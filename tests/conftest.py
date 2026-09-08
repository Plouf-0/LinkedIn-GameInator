import pytest

from Queens.queens_grid import Grid, build_example_grid


@pytest.fixture
def all_colors_grid():
    """Create a grid that includes all supported colors."""
    test_grid = [
        "B C G N O P R V W Y",
        "Y W V R P O N G C B",
    ]
    return Grid(build_example_grid(test_grid))
