# Integration tests for Declaratieregel query mapping on Postgres
# Focuses on verifying correct data flow from staging to silver for declaration rules
# This ensures complex GGM queries with joins and transformations work correctly

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


def _insert_from_select(engine, target_schema: str, select_name: str, select_stmt):
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
@pytest.mark.postgres
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker not available/running; required for this integration test.",
)
def test_declaratieregel_postgres_insertion(tmp_path):
    """Validate DECLARATIEREGEL mapping now projects a deterministic PK and inserts rows."""
    engine = get_connection(
        db_type="postgres",
        db_name="ggm_declaratieregel",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=5433,
        force_refresh=True,
        sql_folder="./ggm_selectie/cssd",
        sql_suffix_filter=True,
        sql_schema="silver",
        print_tables=False,
    )

    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "staging"'))
        conn.execute(text("DROP TABLE IF EXISTS staging.wvind_b CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS staging.wvdos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS staging.szukhis CASCADE;"))
        conn.execute(
            text(
                "CREATE TABLE staging.wvind_b (besluitnr VARCHAR(50), volgnr_ind VARCHAR(50), clientnr VARCHAR(50));"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE staging.wvdos (besluitnr VARCHAR(50), volgnr_ind VARCHAR(50), uniek VARCHAR(50));"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE staging.szukhis (uniekwvdos VARCHAR(50), bedrag DECIMAL(10,2), verslagnr INT);"
            )
        )
        # Insert matching rows so joins hit
        conn.execute(text("INSERT INTO staging.wvind_b VALUES ('B001','01','C1');"))
        conn.execute(
            text("INSERT INTO staging.wvdos VALUES ('B001','01','DOSB00101');")
        )
        conn.execute(text("INSERT INTO staging.szukhis VALUES ('DOSB00101',12.34,1);"))

    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    cfg.set("settings", "SILVER_TABLE_NAME_CASE", "upper")
    queries = prepare_queries(cfg)

    stmt = queries["DECLARATIEREGEL"](engine, source_schema="staging")
    _insert_from_select(
        engine, target_schema="silver", select_name="DECLARATIEREGEL", select_stmt=stmt
    )

    with engine.connect() as conn:
        cnt = conn.execute(
            text("SELECT COUNT(*) FROM silver.declaratieregel")
        ).scalar_one()
        # Ensure PK was projected deterministically (matching wvdos.uniek)
        pk = conn.execute(
            text("SELECT declaratieregel_id FROM silver.declaratieregel LIMIT 1")
        ).scalar_one()
    assert cnt >= 1
    assert pk == "DOSB00101"
