# Configures pytest to filter tests based on database markers
# This allows running tests only for specific databases via CLI or env var

import os
import pytest

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
