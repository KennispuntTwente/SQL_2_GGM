# Configures pytest to filter tests based on database markers
# This allows running tests only for specific databases via CLI or env var

import os
import pytest
from pathlib import Path

# Expose fixtures defined in tests.integration_utils (e.g., oracle_source_engine)
# so they are discoverable by pytest across all test modules.
pytest_plugins = ["tests.integration_utils"]

# Known database marker names we support for filtering
KNOWN_DB_MARKERS = {"postgres", "mssql", "mysql", "mariadb", "oracle", "sqlite"}

# Normalization map to handle common aliases
_ALIAS = {
    "postgresql": "postgres",
    "pg": "postgres",
    "sqlserver": "mssql",
    "microsoftsql": "mssql",
    "microsoft-sql": "mssql",
    "mariadb": "mariadb",
    "mysql": "mysql",
    "postgres": "postgres",
    "mssql": "mssql",
    "oracle": "oracle",
    "sqlite": "sqlite",
    "sqlite3": "sqlite",
}


def _normalize_db(name: str) -> str:
    return _ALIAS.get(name.strip().lower(), name.strip().lower())


def _selected_dbs(config: pytest.Config) -> set[str] | None:
    # Priority: CLI option --db, then TEST_DB env var (comma-separated)
    opt = config.getoption("--db")
    if opt:
        return { _normalize_db(x) for x in opt.split(",") if x.strip() }
    env = os.getenv("TEST_DB")
    if env:
        return { _normalize_db(x) for x in env.split(",") if x.strip() }
    return None


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--db",
        action="store",
        default=None,
        help=(
            "Comma-separated database filter (e.g., --db=postgres,oracle). "
            "Supported: postgres, mssql, mysql, mariadb, oracle, sqlite."
        ),
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    selected = _selected_dbs(config)
    if not selected:
        return  # No filtering requested

    for item in list(items):
        # Determine the DB this item targets, via marker or parameter value
        item_db_markers = [m.name for m in item.iter_markers() if m.name in KNOWN_DB_MARKERS]

        # If test is parametrized with db_type, check that too
        param_db: str | None = None
        callspec = getattr(item, "callspec", None)
        if callspec is not None and "db_type" in callspec.params:
            param_db = _normalize_db(str(callspec.params["db_type"]))

        # Decide if the test should run under the filter:
        # - If it carries a known DB marker: run only if any matches
        # - Else if it has a db_type param: run only if it matches
        # - Else: leave it alone (generic tests still run)
        should_consider = bool(item_db_markers) or (param_db is not None)
        if not should_consider:
            continue

        matches = False
        if item_db_markers and any(_normalize_db(m) in selected for m in item_db_markers):
            matches = True
        if param_db and param_db in selected:
            matches = True

        if not matches:
            item.add_marker(pytest.mark.skip(reason=f"Skipped by --db/TEST_DB filter (wanted {','.join(sorted(selected))})"))


# ----------------------------------------------------------------------------
# Test session hygiene for stray root-level marker files
# ----------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def _cleanup_root_marker_files():
    """
    Some local runs produce empty marker files named 'available' and 'use' in
    the repository root (likely from external tooling). Keep the repo clean by
    removing any stale files at session start, and if they reappear during the
    run, move them into a dedicated test artifacts folder for inspection.
    """
    repo_root = Path(__file__).resolve().parents[1]
    artifacts_dir = repo_root / "tests" / "_artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _purge_or_stash(stage: str):
        for name in ("available", "use"):
            p = repo_root / name
            if p.exists() and p.is_file():
                # Move into artifacts with stage suffix to avoid overwriting
                target = artifacts_dir / f"{name}.{stage}"
                try:
                    p.rename(target)
                except Exception:
                    # If rename fails (e.g., cross-device), fall back to unlink
                    try:
                        p.unlink()
                    except Exception:
                        pass

    # Remove or stash stale files before tests start
    _purge_or_stash(stage="pre")
    yield
    # If they were recreated during tests, stash them post-run too
    _purge_or_stash(stage="post")
