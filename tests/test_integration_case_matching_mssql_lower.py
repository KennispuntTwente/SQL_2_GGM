import os
import subprocess
import configparser

import pytest
from sqlalchemy import MetaData, Table, text

from dev_sql_server.get_connection import get_connection
from staging_to_silver.functions.queries_setup import prepare_queries


def _docker_running() -> bool:
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def _slow_tests_enabled() -> bool:
    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


def _mssql_driver_available() -> bool:
    try:
        import pyodbc  # noqa: F401
        return any("ODBC Driver 18 for SQL Server" in d for d in pyodbc.drivers())
    except Exception:
        return False


@pytest.mark.slow
@pytest.mark.mssql
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not _mssql_driver_available(),
    reason="ODBC Driver 18 for SQL Server not installed; required for MSSQL test.",
)
def test_mssql_strict_lowercase_columns(tmp_path):
    # Reset staging matching env
    for k in [
        "STAGING_NAME_MATCHING",
        "STAGING_TABLE_NAME_CASE",
        "STAGING_COLUMN_NAME_CASE",
    ]:
        os.environ.pop(k, None)

    # Start SQL Server and create target table and staging with lowercase columns
    port = 1437
    engine = get_connection(
        db_type="mssql",
        db_name="src_case_lower",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=port,
        force_refresh=True,
        sql_folder=None,
        sql_suffix_filter=True,
        sql_schema=None,
        print_tables=False,
    )

    with engine.begin() as conn:
        conn.execute(text("IF OBJECT_ID(N'dbo.BESCHIKKING', N'U') IS NOT NULL DROP TABLE dbo.BESCHIKKING;"))
        conn.execute(
            text(
                """
                CREATE TABLE dbo.BESCHIKKING (
                    BESCHIKKING_ID NVARCHAR(50),
                    CLIENT_ID NVARCHAR(50),
                    HEEFT_VOORZIENINGEN_BESCHIKTE_VOORZIENING_ID NVARCHAR(50),
                    CODE NVARCHAR(20),
                    COMMENTAAR NVARCHAR(200),
                    DATUMAFGIFTE DATE,
                    GRONDSLAGEN INT,
                    WET NVARCHAR(255)
                )
                """
            )
        )
        conn.execute(text("IF OBJECT_ID(N'dbo.wvbesl', N'U') IS NOT NULL DROP TABLE dbo.wvbesl;"))
        conn.execute(text("CREATE TABLE dbo.wvbesl (besluitnr NVARCHAR(50), clientnr NVARCHAR(50));"))
        conn.execute(text("INSERT INTO dbo.wvbesl (besluitnr, clientnr) VALUES ('B300','c300');"))

    # Load queries
    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    cfg.set("settings", "SILVER_TABLE_NAME_CASE", "upper")
    queries = prepare_queries(cfg)

    # Helper to insert
    def _insert_from_select(select_name, select_stmt):
        md = MetaData()
        dest = Table(select_name, md, schema="dbo", autoload_with=engine, extend_existing=True)
        select_cols = [c.name for c in select_stmt.selected_columns]
        dest_map = {c.name.lower(): c for c in dest.columns}
        ordered = []
        for c in select_cols:
            try:
                ordered.append(dest.columns[c])
            except KeyError:
                ci = dest_map.get(c.lower())
                if ci is None:
                    raise KeyError(f"Destination column '{c}' not found in {dest.fullname}")
                ordered.append(ci)
        with engine.begin() as conn:
            conn.execute(dest.insert().from_select(ordered, select_stmt))

    # Strict with lowercase column preference should succeed against lower-case staging columns
    os.environ["STAGING_NAME_MATCHING"] = "strict"
    os.environ["STAGING_COLUMN_NAME_CASE"] = "lower"
    stmt = queries["BESCHIKKING"](engine, source_schema="dbo")
    _insert_from_select("BESCHIKKING", stmt)

    with engine.connect() as conn:
        cnt = conn.execute(text("SELECT COUNT(*) FROM dbo.BESCHIKKING WHERE CLIENT_ID='c300'")) .scalar_one()
    assert cnt == 1
