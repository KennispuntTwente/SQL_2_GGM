import configparser
import pytest
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection
from staging_to_silver.functions.queries_setup import prepare_queries
from tests.integration_utils import (
    docker_running,
    insert_from_select_case_insensitive,
    ports,
    slow_tests_enabled,
)


@pytest.mark.slow
@pytest.mark.postgres
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker not available/running; required for this integration test.",
)
def test_declaratieregel_postgres_insertion(tmp_path):
    """Validate DECLARATIEREGEL mapping now projects a deterministic PK and inserts rows."""
    engine = get_connection(
        db_type="postgres",
        db_name="ggm_declaratieregel",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=ports["postgres"],
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
    insert_from_select_case_insensitive(
        engine,
        target_schema="silver",
        dest_table_name="DECLARATIEREGEL",
        select_stmt=stmt,
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
