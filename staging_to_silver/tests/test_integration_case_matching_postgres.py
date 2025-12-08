import os
import configparser

import pytest
from sqlalchemy import MetaData, Table, text

from dev_sql_server.get_connection import get_connection
from staging_to_silver.functions.queries_setup import prepare_queries
from tests.integration_utils import (
    ports,
    docker_running,
    slow_tests_enabled,
    cleanup_db_containers,
)


@pytest.mark.slow
@pytest.mark.postgres
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_postgres_case_matching_auto_vs_strict(tmp_path):
    # Ensure environment is clean for staging name/column matching
    os.environ.pop("STAGING_NAME_MATCHING", None)
    os.environ.pop("STAGING_TABLE_NAME_CASE", None)
    os.environ.pop("STAGING_COLUMN_NAME_CASE", None)

    # Clean up any stale containers before starting to ensure fresh state
    cleanup_db_containers("postgres")

    try:
        # Start Postgres and initialize silver schema from GGM DDL
        engine = get_connection(
            db_type="postgres",
            db_name="ggm_case_matching",
            user="sa",
            password="S3cureP@ssw0rd!23243",
            port=ports["postgres"],
            force_refresh=True,
            sql_folder="./ggm_selectie/cssd",
            sql_suffix_filter=True,
            sql_schema="silver",
            print_tables=False,
        )

        # Prepare staging tables: uppercase-quoted WVBESL for testing column case and name matching
        with engine.begin() as conn:
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS "staging"'))
            conn.execute(text('DROP TABLE IF EXISTS staging."WVBESL" CASCADE;'))
            conn.execute(
                text(
                    'CREATE TABLE staging."WVBESL" ("BESLUITNR" VARCHAR(50), "CLIENTNR" VARCHAR(50));'
                )
            )
            conn.execute(
                text(
                    'INSERT INTO staging."WVBESL" ("BESLUITNR", "CLIENTNR") VALUES (\'B100\', \'C100\');'
                )
            )

        # Load queries with default SILVER_TABLE_NAME_CASE=upper (prepare_queries does this by default)
        cfg = configparser.ConfigParser()
        cfg.add_section("settings")
        cfg.set("settings", "SILVER_TABLE_NAME_CASE", "upper")
        queries = prepare_queries(cfg)

        # Helper to insert select results into silver schema with case-insensitive column order match
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
            # Use PostgreSQL upsert semantics to avoid duplicate key errors when re-inserting
            from sqlalchemy.dialects.postgresql import insert as pg_insert  # type: ignore

            pk_cols = [c.name for c in dest.primary_key.columns] or None
            insert_stmt = pg_insert(dest).from_select(ordered, select_stmt)
            if pk_cols:
                insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=pk_cols)
            with engine.begin() as conn:
                conn.execute(insert_stmt)

        # Case A: auto mode (case-insensitive) should match uppercase columns without STAGING_COLUMN_NAME_CASE
        os.environ["STAGING_NAME_MATCHING"] = "auto"
        os.environ.pop("STAGING_COLUMN_NAME_CASE", None)
        stmt_auto = queries["BESCHIKKING"](engine, source_schema="staging")
        _insert_from_select("BESCHIKKING", stmt_auto)

        # Verify row inserted
        with engine.connect() as conn:
            cnt_auto = conn.execute(
                text("SELECT COUNT(*) FROM silver.beschikking")
            ).scalar_one()
        assert cnt_auto >= 1

        # Case B: strict mode requires correct column name preference; set to UPPER to match quoted cols
        os.environ["STAGING_NAME_MATCHING"] = "strict"
        os.environ["STAGING_COLUMN_NAME_CASE"] = "upper"
        # Insert another row in source and run again
        with engine.begin() as conn:
            conn.execute(
                text(
                    'INSERT INTO staging."WVBESL" ("BESLUITNR", "CLIENTNR") VALUES (\'B101\', \'C101\');'
                )
            )
        stmt_strict = queries["BESCHIKKING"](engine, source_schema="staging")
        _insert_from_select("BESCHIKKING", stmt_strict)

        with engine.connect() as conn:
            cnt_strict = conn.execute(
                text("SELECT COUNT(*) FROM silver.beschikking")
            ).scalar_one()
        assert cnt_strict >= cnt_auto + 1
    finally:
        cleanup_db_containers("postgres")
