# Tests staging_to_silver integration; Postgres and MSSQL backends
# Focuses on correct query execution and data insertion into silver schema from staging schema
# This ensures end-to-end functionality of staging_to_silver queries against real databases

import os
import subprocess

import pytest
from sqlalchemy import MetaData, Table, text
from dotenv import load_dotenv

from dev_sql_server.get_connection import get_connection
import configparser
from staging_to_silver.functions.queries_setup import prepare_queries


load_dotenv("tests/.env")


def _docker_running() -> bool:
    try:
        res = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=5
        )
        return res.returncode == 0
    except Exception:
        return False


def _slow_tests_enabled() -> bool:
    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


def _mssql_driver_available() -> bool:
    try:
        import pyodbc  # noqa

        return any("ODBC Driver 18 for SQL Server" in d for d in pyodbc.drivers())
    except Exception:
        return False


def _insert_from_select(engine, target_schema: str, select_name: str, select_stmt):
    # Reflect destination and perform column-order match in a case-insensitive way
    md = MetaData()
    try:
        dest_table = Table(
            select_name,
            md,
            schema=target_schema,
            autoload_with=engine,
            extend_existing=True,
        )
    except Exception:
        # Retry with lowercased name to handle Postgres' unquoted lowercasing
        dest_table = Table(
            select_name.lower(),
            md,
            schema=target_schema,
            autoload_with=engine,
            extend_existing=True,
        )

    select_col_order = [c.name for c in select_stmt.selected_columns]
    dest_cols_map_ci = {c.name.lower(): c for c in dest_table.columns}
    dest_cols = []
    for col_name in select_col_order:
        try:
            dest_cols.append(dest_table.columns[col_name])
        except KeyError:
            ci = dest_cols_map_ci.get(col_name.lower())
            if ci is None:
                raise KeyError(
                    f"Destination column '{col_name}' not found in table {dest_table.fullname}."
                )
            dest_cols.append(ci)

    with engine.begin() as conn:
        conn.execute(dest_table.insert().from_select(dest_cols, select_stmt))


@pytest.mark.slow
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_staging_to_silver_postgres(tmp_path):
    # Start Postgres with silver schema initialized from GGM DDL
    engine = get_connection(
        db_type="postgres",
        db_name="ggm_staging_to_silver",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=5433,
        force_refresh=True,
        sql_folder="./ggm_selectie",
        sql_suffix_filter=True,
        sql_schema="silver",
        print_tables=False,
    )

    # Create staging schema and populate minimal data for both lower- and upper-case source tables
    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "staging"'))
        # Lower-case tables for BESCHIKTE_VOORZIENING query
        conn.execute(
            text(
                """
            DROP TABLE IF EXISTS staging.wvind_b CASCADE;
            CREATE TABLE staging.wvind_b (
                besluitnr VARCHAR(50),
                volgnr_ind VARCHAR(50),
                dd_eind TIMESTAMP,
                dd_begin TIMESTAMP,
                volume INTEGER,
                status_indicatie VARCHAR(50),
                kode_regeling VARCHAR(50),
                clientnr VARCHAR(50)
            );
            DROP TABLE IF EXISTS staging.szregel CASCADE;
            CREATE TABLE staging.szregel (
                kode_regeling VARCHAR(50),
                omschryving VARCHAR(50)
            );
            DROP TABLE IF EXISTS staging.wvbesl CASCADE;
            CREATE TABLE staging.wvbesl (
                besluitnr VARCHAR(50)
            );
            DROP TABLE IF EXISTS staging.wvdos CASCADE;
            CREATE TABLE staging.wvdos (
                besluitnr VARCHAR(50),
                volgnr_ind VARCHAR(50),
                kode_reden_einde_voorz VARCHAR(50)
            );
            DROP TABLE IF EXISTS staging.abc_refcod CASCADE;
            CREATE TABLE staging.abc_refcod (
                code VARCHAR(50),
                omschrijving VARCHAR(50),
                domein VARCHAR(100)
            );
            """
            )
        )
        conn.execute(
            text(
                """
            INSERT INTO staging.wvind_b (besluitnr, volgnr_ind, dd_eind, dd_begin, volume, status_indicatie, kode_regeling, clientnr)
            VALUES ('B001','01','2024-01-01 00:00:00','2023-12-02 00:00:00',10,'active','KR1','C1');
            INSERT INTO staging.szregel (kode_regeling, omschryving) VALUES ('KR1','JEUGDWET');
            INSERT INTO staging.wvbesl (besluitnr) VALUES ('B001');
            INSERT INTO staging.wvdos (besluitnr, volgnr_ind, kode_reden_einde_voorz) VALUES ('B001','01','RC1');
            INSERT INTO staging.abc_refcod (code, omschrijving, domein) VALUES ('RC1','Some reason','JZG_REDEN_EINDE_PRODUCT');
            """
            )
        )

        # Upper-case table for BESCHIKKING query (quoted to force exact case)
        conn.execute(text('DROP TABLE IF EXISTS staging."WVBESL" CASCADE;'))
        conn.execute(
            text(
                'CREATE TABLE staging."WVBESL" ("BESLUITNR" VARCHAR(50), "CLIENTNR" VARCHAR(50));'
            )
        )
        conn.execute(
            text(
                'INSERT INTO staging."WVBESL" ("BESLUITNR", "CLIENTNR") VALUES (\'B001\', \'C1\');'
            )
        )

    # Load queries via the same setup path as main.py (prepare_queries)
    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    cfg.set("settings", "SILVER_TABLE_NAME_CASE", "upper")
    queries = prepare_queries(cfg)

    # Run BESCHIKTE_VOORZIENING (lowercase source tables) → into silver
    stmt_bv = queries["BESCHIKTE_VOORZIENING"](engine, source_schema="staging")
    _insert_from_select(
        engine,
        target_schema="silver",
        select_name="BESCHIKTE_VOORZIENING",
        select_stmt=stmt_bv,
    )

    # Run BESCHIKKING (uppercase source table name) → into silver
    stmt_b = queries["BESCHIKKING"](engine, source_schema="staging")
    _insert_from_select(
        engine, target_schema="silver", select_name="BESCHIKKING", select_stmt=stmt_b
    )

    # Validate inserted rows
    with engine.connect() as conn:
        cnt_bv = conn.execute(
            text("SELECT COUNT(*) FROM silver.beschikte_voorziening")
        ).scalar_one()
        cnt_b = conn.execute(
            text("SELECT COUNT(*) FROM silver.beschikking")
        ).scalar_one()
    assert cnt_bv >= 1
    assert cnt_b >= 1


@pytest.mark.slow
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
def test_staging_to_silver_mssql(tmp_path):
    # Start MSSQL with silver schema initialized from GGM DDL
    engine = get_connection(
        db_type="mssql",
        db_name="ggm_staging_to_silver",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=1434,
        force_refresh=True,
        sql_folder="./ggm_selectie",
        sql_suffix_filter=True,
        sql_schema=None,  # use default schema (dbo) for sa to avoid ALTER USER
        print_tables=False,
    )

    # Prepare staging schema (dbo) with uppercase-named tables expected by some queries
    with engine.begin() as conn:
        # Ensure fresh state
        for t in ["SZUKHIS", "WVDOS", "WVIND_B", "WVBESL", "SZCLIENT", "SZWERKER"]:
            conn.execute(
                text(f"IF OBJECT_ID(N'dbo.{t}', N'U') IS NOT NULL DROP TABLE dbo.{t};")
            )

        # Create minimal tables
        conn.execute(text("CREATE TABLE dbo.WVBESL (BESLUITNR INT, CLIENTNR INT);"))
        conn.execute(text("CREATE TABLE dbo.SZCLIENT (CLIENTNR INT, IND_GEZAG INT);"))
        conn.execute(
            text(
                "CREATE TABLE dbo.SZWERKER (KODE_WERKER VARCHAR(50), NAAM VARCHAR(50), KODE_INSTAN VARCHAR(50), E_MAIL VARCHAR(100), IND_GESLACHT VARCHAR(10), TOELICHTING VARCHAR(100), TELEFOON VARCHAR(50));"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE dbo.WVIND_B (BESLUITNR INT, VOLGNR_IND INT, CLIENTNR INT);"
            )
        )
        conn.execute(
            text("CREATE TABLE dbo.WVDOS (BESLUITNR INT, VOLGNR_IND INT, UNIEK INT);")
        )
        conn.execute(
            text(
                "CREATE TABLE dbo.SZUKHIS (UNIEKWVDOS INT, BEDRAG DECIMAL(10,2), VERSLAGNR INT);"
            )
        )

        # Insert sample data
        conn.execute(
            text("INSERT INTO dbo.WVBESL (BESLUITNR, CLIENTNR) VALUES (1, 1001);")
        )
        conn.execute(
            text("INSERT INTO dbo.SZCLIENT (CLIENTNR, IND_GEZAG) VALUES (1001, 1);")
        )
        conn.execute(
            text(
                "INSERT INTO dbo.SZWERKER (KODE_WERKER, NAAM, KODE_INSTAN, E_MAIL, IND_GESLACHT, TOELICHTING, TELEFOON) VALUES ('M1','Doe','F1','a@b.com','M','-','123');"
            )
        )
        conn.execute(
            text(
                "INSERT INTO dbo.WVDOS (BESLUITNR, VOLGNR_IND, UNIEK) VALUES (1, 1, 10);"
            )
        )
        conn.execute(
            text(
                "INSERT INTO dbo.WVIND_B (BESLUITNR, VOLGNR_IND, CLIENTNR) VALUES (1, 1, 1001);"
            )
        )
        conn.execute(
            text(
                "INSERT INTO dbo.SZUKHIS (UNIEKWVDOS, BEDRAG, VERSLAGNR) VALUES (10, 12.34, 1);"
            )
        )

    # Load queries via the same setup path as main.py
    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    cfg.set("settings", "SILVER_TABLE_NAME_CASE", "upper")
    queries = prepare_queries(cfg)

    # BESCHIKKING
    stmt_b = queries["BESCHIKKING"](engine, source_schema="dbo")
    _insert_from_select(
        engine, target_schema="dbo", select_name="BESCHIKKING", select_stmt=stmt_b
    )

    # CLIENT
    stmt_client = queries["CLIENT"](engine, source_schema="dbo")
    _insert_from_select(
        engine, target_schema="dbo", select_name="CLIENT", select_stmt=stmt_client
    )

    # Validate inserted rows
    with engine.connect() as conn:
        cnt_b = conn.execute(text("SELECT COUNT(*) FROM dbo.BESCHIKKING")).scalar_one()
        cnt_client = conn.execute(text("SELECT COUNT(*) FROM dbo.CLIENT")).scalar_one()
    assert cnt_b >= 1
    assert cnt_client >= 1
