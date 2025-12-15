import os
from pathlib import Path

import pytest
from sqlalchemy import MetaData, Table, text

from dev_sql_server.get_connection import get_connection
from staging_to_silver.functions.queries_setup import prepare_queries
from staging_to_silver.functions.schema_qualifier import qualify_schema
import configparser
from tests.integration_utils import (
    docker_running,
    mssql_driver_available,
    port_for_worker,
    slow_tests_enabled,
)


@pytest.mark.slow
@pytest.mark.mssql
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not mssql_driver_available(),
    reason="ODBC Driver 18 for SQL Server not installed; required for MSSQL test.",
)
def test_mssql_case_matching_with_crossdb_source(tmp_path: Path):
    # Clean staging name/column matching env
    os.environ.pop("STAGING_NAME_MATCHING", None)
    os.environ.pop("STAGING_TABLE_NAME_CASE", None)
    os.environ.pop("STAGING_COLUMN_NAME_CASE", None)

    # Start a SQL Server container and create a source database
    port = port_for_worker(1436)
    src_db = "src_case"
    engine = get_connection(
        db_type="mssql",
        db_name=src_db,
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=port,
        force_refresh=True,
        sql_folder=None,
        sql_suffix_filter=True,
        sql_schema=None,
        print_tables=False,
    )

    # Create a minimal destination table (dbo.BESCHIKKING) in the same DB for easy validation
    with engine.begin() as conn:
        conn.execute(
            text(
                "IF OBJECT_ID(N'dbo.BESCHIKKING', N'U') IS NOT NULL DROP TABLE dbo.BESCHIKKING;"
            )
        )
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
        # Prepare uppercase-quoted source table WVBESL with uppercase columns
        conn.execute(
            text("IF OBJECT_ID(N'dbo.WVBESL', N'U') IS NOT NULL DROP TABLE dbo.WVBESL;")
        )
        conn.execute(
            text(
                "CREATE TABLE dbo.WVBESL (BESLUITNR NVARCHAR(50), CLIENTNR NVARCHAR(50));"
            )
        )
        conn.execute(
            text("INSERT INTO dbo.WVBESL (BESLUITNR, CLIENTNR) VALUES ('B200','C200');")
        )

    # Load queries
    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    cfg.set("settings", "SILVER_TABLE_NAME_CASE", "upper")
    queries = prepare_queries(cfg)

    # Helper to insert
    def _insert_from_select(select_name, select_stmt):
        md = MetaData()
        dest = Table(
            select_name, md, schema="dbo", autoload_with=engine, extend_existing=True
        )
        select_cols = [c.name for c in select_stmt.selected_columns]
        dest_map = {c.name.lower(): c for c in dest.columns}
        ordered = []
        for c in select_cols:
            try:
                ordered.append(dest.columns[c])
            except KeyError:
                ci = dest_map.get(c.lower())
                if ci is None:
                    raise KeyError(
                        f"Destination column '{c}' not found in {dest.fullname}"
                    )
                ordered.append(ci)
        with engine.begin() as conn:
            conn.execute(dest.insert().from_select(ordered, select_stmt))

    # Build source_schema as three-part name using qualify_schema to exercise rsplit fallback
    source_schema_3part = qualify_schema("mssql", src_db, "dbo", default_schema="dbo")

    # Case A: auto mode should match regardless of case
    os.environ["STAGING_NAME_MATCHING"] = "auto"
    os.environ.pop("STAGING_COLUMN_NAME_CASE", None)
    stmt_auto = queries["BESCHIKKING"](engine, source_schema=source_schema_3part)
    _insert_from_select("BESCHIKKING", stmt_auto)

    with engine.connect() as conn:
        cnt_auto = conn.execute(
            text("SELECT COUNT(*) FROM dbo.BESCHIKKING")
        ).scalar_one()
    assert cnt_auto >= 1

    # Case B: strict mode with UPPER column preference
    os.environ["STAGING_NAME_MATCHING"] = "strict"
    os.environ["STAGING_COLUMN_NAME_CASE"] = "upper"
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO dbo.WVBESL (BESLUITNR, CLIENTNR) VALUES ('B201','C201');")
        )
    stmt_strict = queries["BESCHIKKING"](engine, source_schema=source_schema_3part)
    _insert_from_select("BESCHIKKING", stmt_strict)

    with engine.connect() as conn:
        cnt_strict = conn.execute(
            text("SELECT COUNT(*) FROM dbo.BESCHIKKING")
        ).scalar_one()
    assert cnt_strict >= cnt_auto + 1
