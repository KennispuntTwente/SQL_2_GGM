# Integration tests for Postgres staging table name case preferences
# Focuses on choosing between quoted UPPER and unquoted lower table variants
# This ensures staging_to_silver respects STAGING_TABLE_NAME_CASE configuration

import os
import subprocess
import configparser

import pytest
from sqlalchemy import MetaData, Table, text

from dev_sql_server.get_connection import get_connection
from staging_to_silver.functions.queries_setup import prepare_queries


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


@pytest.mark.slow
@pytest.mark.postgres
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_postgres_staging_table_name_case_preference(tmp_path):
    # Clean env for staging matching knobs
    for k in [
        "STAGING_NAME_MATCHING",
        "STAGING_TABLE_NAME_CASE",
        "STAGING_COLUMN_NAME_CASE",
    ]:
        os.environ.pop(k, None)

    # Start Postgres and initialize silver schema
    engine = get_connection(
        db_type="postgres",
        db_name="ggm_case_pref",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=5434,
        force_refresh=True,
        sql_folder="./ggm_selectie/cssd",
        sql_suffix_filter=True,
        sql_schema="silver",
        print_tables=False,
    )

    # Prepare staging schema with two variants: quoted UPPER and unquoted lower
    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "staging"'))
        # UPPER quoted variant
        conn.execute(text('DROP TABLE IF EXISTS staging."WVBESL" CASCADE;'))
        conn.execute(
            text(
                'CREATE TABLE staging."WVBESL" ("BESLUITNR" VARCHAR(50), "CLIENTNR" VARCHAR(50));'
            )
        )
        conn.execute(
            text(
                'INSERT INTO staging."WVBESL" ("BESLUITNR", "CLIENTNR") VALUES (\'U100\', \'UCLIENT\');'
            )
        )
        # lower (unquoted) variant
        conn.execute(text("DROP TABLE IF EXISTS staging.wvbesl CASCADE;"))
        conn.execute(
            text(
                "CREATE TABLE staging.wvbesl (besluitnr VARCHAR(50), clientnr VARCHAR(50));"
            )
        )
        conn.execute(
            text(
                "INSERT INTO staging.wvbesl (besluitnr, clientnr) VALUES ('l100', 'lclient');"
            )
        )

    # Load queries with default SILVER_TABLE_NAME_CASE=upper
    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    cfg.set("settings", "SILVER_TABLE_NAME_CASE", "upper")
    queries = prepare_queries(cfg)

    # Helper to insert into silver honoring column order and SILVER_NAME_MATCHING default (auto)
    def _insert_from_select(select_name, select_stmt):
        md = MetaData()
        try:
            dest = Table(
                select_name,
                md,
                schema="silver",
                autoload_with=engine,
                extend_existing=True,
            )
        except Exception:
            dest = Table(
                select_name.lower(),
                md,
                schema="silver",
                autoload_with=engine,
                extend_existing=True,
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
        from sqlalchemy.dialects.postgresql import insert as pg_insert  # type: ignore

        pk_cols = [c.name for c in dest.primary_key.columns] or None
        insert_stmt = pg_insert(dest).from_select(ordered, select_stmt)
        if pk_cols:
            insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=pk_cols)
        with engine.begin() as conn:
            conn.execute(insert_stmt)

    # Case 1: prefer UPPER variant
    os.environ["STAGING_NAME_MATCHING"] = "auto"
    os.environ["STAGING_TABLE_NAME_CASE"] = "upper"
    os.environ.pop("STAGING_COLUMN_NAME_CASE", None)

    stmt_upper_pref = queries["BESCHIKKING"](engine, source_schema="staging")
    _insert_from_select("BESCHIKKING", stmt_upper_pref)

    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT CLIENT_ID FROM silver.beschikking ORDER BY CLIENT_ID")
        ).fetchall()
    # Should include only the row from the UPPER table variant
    assert ("UCLIENT",) in rows
    assert ("lclient",) not in rows

    # Cleanup destination
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM silver.beschikking"))

    # Case 2: prefer lower variant
    os.environ["STAGING_TABLE_NAME_CASE"] = "lower"
    stmt_lower_pref = queries["BESCHIKKING"](engine, source_schema="staging")
    _insert_from_select("BESCHIKKING", stmt_lower_pref)

    with engine.connect() as conn:
        rows2 = conn.execute(
            text("SELECT CLIENT_ID FROM silver.beschikking ORDER BY CLIENT_ID")
        ).fetchall()
    assert ("lclient",) in rows2
    assert ("UCLIENT",) not in rows2
