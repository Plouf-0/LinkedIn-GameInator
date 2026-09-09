"""Tests for the command line entry point."""

import pytest
from pytest_mock import MockerFixture

from linkedin_gameinator import cli


class TestSelfTestChecks:
    def test_queens_check_passes(self):
        ok, detail = cli._check_queens()
        assert ok, detail
        assert "6 queens" in detail

    def test_queens_check_reports_a_failure(self, mocker: MockerFixture):
        mocker.patch(
            "Queens.brute_force_resolver.BruteForceResolver.resolve_grid",
            side_effect=RuntimeError("boom"),
        )
        ok, detail = cli._check_queens()
        assert not ok
        assert "RuntimeError: boom" in detail

    @pytest.mark.filterwarnings("ignore:Duo is not aligned")
    def test_queens_check_reports_an_unsolved_grid(self, mocker: MockerFixture):
        # Forcing the validity check to fail makes the search exhaust every
        # branch, which is noisy but is exactly the path under test.
        mocker.patch(
            "Queens.brute_force_resolver.BruteForceResolver.is_solution_valid",
            return_value=False,
        )
        ok, detail = cli._check_queens()
        assert not ok
        assert "did not reach a valid solution" in detail

    def test_sudoku_check_passes(self):
        ok, detail = cli._check_sudoku()
        assert ok, detail
        assert "4x4" in detail

    def test_sudoku_check_reports_a_missing_prolog(self, mocker: MockerFixture):
        from Sudoku.sudoku_pl_resolver import PrologUnavailableError

        mocker.patch(
            "Sudoku.sudoku_pl_resolver.solve",
            side_effect=PrologUnavailableError("install swi-prolog"),
        )
        ok, detail = cli._check_sudoku()
        assert not ok
        assert "install swi-prolog" in detail

    def test_sudoku_check_rejects_an_invalid_solution(self, mocker: MockerFixture):
        mocker.patch("Sudoku.sudoku_pl_resolver.solve", return_value=[[1, 1], [2, 2]])
        ok, detail = cli._check_sudoku()
        assert not ok
        assert "invalid solution" in detail


class TestSelfTest:
    def test_reports_success(self, capsys: pytest.CaptureFixture[str]):
        assert cli.self_test() == 0

        output = capsys.readouterr().out
        assert "PASS  Queens" in output
        assert "PASS  Sudoku" in output
        assert "self-test passed" in output

    def test_reports_failure_with_an_exit_code(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ):
        mocker.patch.object(cli, "_check_sudoku", return_value=(False, "nope"))

        assert cli.self_test() == 1
        assert "self-test failed (1 check(s))" in capsys.readouterr().out

    def test_swipl_origin_names_the_bundle_when_frozen(self, mocker: MockerFixture, tmp_path):
        mocker.patch.object(cli.sys, "_MEIPASS", str(tmp_path), create=True)
        mocker.patch("pyswip.core.SWI_HOME_DIR", str(tmp_path / "swipl"))

        assert cli._swipl_origin() == "the bundled SWI-Prolog"

    def test_swipl_origin_names_the_system_otherwise(self, mocker: MockerFixture):
        mocker.patch("pyswip.core.SWI_HOME_DIR", "/usr/lib/swi-prolog")

        assert "system SWI-Prolog at /usr/lib/swi-prolog" in cli._swipl_origin()


class TestParser:
    def test_self_test_runs_without_opening_a_browser(self, mocker: MockerFixture):
        run_scrapper = mocker.patch("WebScrapper.app.main")
        mocker.patch.object(cli, "self_test", return_value=0)

        with pytest.raises(SystemExit) as excinfo:
            cli.main(["--self-test"])

        assert excinfo.value.code == 0
        run_scrapper.assert_not_called()

    def test_default_run_starts_the_browser_flow(self, mocker: MockerFixture):
        run_scrapper = mocker.patch("WebScrapper.app.main")

        cli.main([])

        run_scrapper.assert_called_once_with()

    def test_verbose_turns_on_debug_logging(self, mocker: MockerFixture):
        mocker.patch("WebScrapper.app.main")
        basic_config = mocker.patch("logging.basicConfig")

        cli.main(["--verbose"])

        assert basic_config.call_args.kwargs["level"] == 10  # logging.DEBUG

    def test_version_exits_cleanly(self, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as excinfo:
            cli.main(["--version"])

        assert excinfo.value.code == 0
        assert cli.__version__ in capsys.readouterr().out
