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
