# Running tests in this repo

To run tests reliably on Windows with the project virtual environment, you have two options:

## Option A: Use the venv interpreter directly (recommended)

This avoids shell activation issues and uses the venv's Python explicitly.

```bash
./.venv/Scripts/python -m pytest -q
```

Run a single test file:

```bash
./.venv/Scripts/python -m pytest -q tests/test_download_parquet.py
```

## Option B: Activate the venv first (PowerShell)

If you prefer activating the environment, use PowerShell:

```powershell
& .\.venv\Scripts\Activate.ps1
pytest -q
```

If your default terminal is bash (Git Bash on Windows), you can still call the venv Python as in Option A.

## Notes
- The project targets Python 3.12+. Ensure your venv is created with a compatible Python.
- If you add tests that require external databases, prefer SQLite-backed SQLAlchemy engines for local tests, or mock external calls.

## Running slow integration tests (Docker-based)

Some tests spin up temporary database containers (e.g., Postgres, Oracle, MySQL/MariaDB, MSSQL) and can take a while. These tests are skipped by default and only run when explicitly enabled.

- Tests considered slow: `tests/test_oracle_db.py`, `tests/test_source_to_staging.py`.
- Requirements: Docker Desktop must be installed and running. If Docker isn’t running, these tests will be skipped automatically.
- Enable with the environment variable `RUN_SLOW_TESTS=1`.

Git Bash on Windows (your default shell)

```bash
export RUN_SLOW_TESTS=1
./.venv/Scripts/python -m pytest -q  # run all tests including slow ones

# or target a specific slow test
./.venv/Scripts/python -m pytest -q tests/test_oracle_db.py
./.venv/Scripts/python -m pytest -q tests/test_source_to_staging.py
```

PowerShell

```powershell
$env:RUN_SLOW_TESTS = "1"
& .\.venv\Scripts\python -m pytest -q  # run all tests including slow ones

# or target a specific slow test
& .\.venv\Scripts\python -m pytest -q tests\test_oracle_db.py
& .\.venv\Scripts\python -m pytest -q tests\test_source_to_staging.py
```

Oracle client (only needed if running Oracle-related slow tests)

- If your environment uses Oracle’s Instant Client, provide its path via the config key `SRC_CONNECTORX_ORACLE_CLIENT_PATH`.
- Easiest is to add it to `source_to_staging/.env`, for example:

```env
SRC_CONNECTORX_ORACLE_CLIENT_PATH=C:\\oracle\\instantclient_21_18
```

The tests will initialize the Oracle client if this value is present; otherwise thin mode may be used if supported.
