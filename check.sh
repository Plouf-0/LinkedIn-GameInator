#!/usr/bin/env bash
# Runs the same checks as the CI "quality" and "tests" jobs (.github/workflows/ci.yml),
# so you can catch failures locally instead of in GitHub Actions.
set -e

echo "==> Lint (ruff check)"
uv run ruff check .

echo "==> Format check (ruff format)"
uv run ruff format --check .

echo "==> Type check (mypy)"
uv run mypy .

echo "==> Tests (pytest --cov)"
uv run pytest --cov --cov-report=term

echo "==> All checks passed"
