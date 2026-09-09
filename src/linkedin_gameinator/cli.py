"""Command line entry point.

Beyond launching the browser flow, this exposes a `--self-test` that exercises
both resolvers without a network or a browser. That is what makes it possible
to check a built executable -- in particular whether the SWI-Prolog it carries
actually works on a machine that has none installed.
"""

from __future__ import annotations

import argparse
import logging
import sys

__version__ = "0.1.0"

# A 6x6 board whose regions force a unique solution, small enough to solve
# instantly and varied enough to exercise propagation and backtracking.
SELF_TEST_QUEENS = [
    "R R B B B B",
    "R R R B B B",
    "G G Y Y B B",
    "G G Y Y W B",
    "G G Y W W P",
    "G G W W P P",
]

SELF_TEST_SUDOKU = [
    [1, 0, 0, 0],
    [0, 0, 3, 0],
    [0, 4, 0, 0],
    [0, 0, 0, 2],
]


def _check_queens() -> tuple[bool, str]:
    from Queens.brute_force_resolver import BruteForceResolver
    from Queens.queens_grid import build_example_grid

    try:
        grid = BruteForceResolver(build_example_grid(SELF_TEST_QUEENS))
        grid.resolve_grid()
    except Exception as e:  # noqa: BLE001 - a self-test reports, it does not raise
        return False, f"{type(e).__name__}: {e}"

    if not grid.is_solution_valid():
        return False, "the resolver did not reach a valid solution"
    return True, f"{len(grid.queens)} queens placed"


def _check_sudoku() -> tuple[bool, str]:
    from Sudoku.sudoku_pl_resolver import solve

    try:
        solution = solve(SELF_TEST_SUDOKU, rows_per_area=2)
    except Exception as e:  # noqa: BLE001 - a self-test reports, it does not raise
        return False, f"{type(e).__name__}: {e}"

    size = len(solution)
    expected = list(range(1, size + 1))
    if any(sorted(row) != expected for row in solution):
        return False, f"invalid solution: {solution}"

    return True, f"{size}x{size} grid solved, using {_swipl_origin()}"


def _swipl_origin() -> str:
    """Describe which SWI-Prolog answered: the bundled one or the system's."""
    try:
        from pyswip import core
    except Exception:
        return "an unknown SWI-Prolog"

    home = core.SWI_HOME_DIR or "?"
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle and str(home).startswith(str(bundle)):
        return "the bundled SWI-Prolog"
    return f"the system SWI-Prolog at {home}"


def self_test() -> int:
    """Run both resolvers offline and report. Returns a process exit code."""
    print(f"linkedin-gameinator {__version__}")
    print(f"frozen: {getattr(sys, 'frozen', False)}")

    failures = 0
    for name, check in (("Queens", _check_queens), ("Sudoku (SWI-Prolog)", _check_sudoku)):
        ok, detail = check()
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
        failures += not ok

    print("self-test passed" if not failures else f"self-test failed ({failures} check(s))")
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linkedin-gameinator",
        description="Solve the LinkedIn games in a real browser.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="check both resolvers offline and exit; no browser is opened",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="log the resolvers' reasoning step by step",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.self_test:
        raise SystemExit(self_test())

    from WebScrapper.app import main as run_scrapper

    run_scrapper()
