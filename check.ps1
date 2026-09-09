# Windows counterpart of check.sh: runs the same checks as the CI
# "quality" and "tests" jobs (.github/workflows/ci.yml).
$ErrorActionPreference = "Stop"

function Invoke-Step {
    param([string]$Name, [scriptblock]$Command)
    Write-Host "==> $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE" }
}

Invoke-Step "Lint (ruff check)"          { uv run ruff check . }
Invoke-Step "Format check (ruff format)" { uv run ruff format --check . }
Invoke-Step "Type check (mypy)"          { uv run mypy . }
Invoke-Step "Pre-commit hooks"           { uv run pre-commit run --all-files --show-diff-on-failure }
Invoke-Step "Tests (pytest --cov)"       { uv run pytest --cov --cov-report=term }

Write-Host "==> All checks passed"
