# Integration tests for ensure_database_and_schema helper via Docker
# Focuses on verifying database and schema auto-creation for Postgres, MSSQL, and other dialects
# This ensures the shared helper works correctly in CI/CD pipelines with real containers

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection
from utils.database.ensure_db import ensure_database_and_schema
from tests.integration_utils import (
    ports_dest,
    docker_running,
    slow_tests_enabled,
    cleanup_db_containers,
)


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.postgres
def test_ensure_db_creates_postgres_database_and_schema():
    """Ensure that a missing Postgres database + schema can be created.

    We ask dev_sql_server.get_connection for a db_name that does not
    yet exist; ensure_database_and_schema should create it via the
    admin hop, and we validate that a table can be created in the
    requested schema.
    """

    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    db_type = "postgres"
    db_name = "test_ensure_db_postgres"
    schema = "ggm_test_schema"

    engine = get_connection(
        db_type=db_type,
        db_name=db_name,
        user=username,
        password=password,
        port=ports_dest[db_type],
        force_refresh=True,
        print_tables=False,
    )

    try:
        ensure_database_and_schema(
            engine, schema, admin_database=os.getenv("PG_ADMIN_DB") or None
        )

        with engine.begin() as conn:
            conn.execute(
                text(f"CREATE TABLE IF NOT EXISTS {schema}.tbl (id INT PRIMARY KEY)")
            )
            conn.execute(text(f"INSERT INTO {schema}.tbl (id) VALUES (1)"))

        with engine.connect() as conn:
            value = conn.execute(text(f"SELECT id FROM {schema}.tbl"))
            rows = [r[0] for r in value]
        assert rows == [1]
    finally:
        cleanup_db_containers(db_type)


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.mssql
def test_ensure_db_creates_mssql_database_and_schema():
    """Ensure that a missing MSSQL database + schema can be created."""

    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    db_type = "mssql"
    db_name = "test_ensure_db_mssql"
    schema = "ggm_test_schema"

    engine = get_connection(
        db_type=db_type,
        db_name=db_name,
        user=username,
        password=password,
        port=ports_dest[db_type],
        force_refresh=True,
        print_tables=False,
    )

    try:
        ensure_database_and_schema(
            engine, schema, admin_database=os.getenv("MSSQL_ADMIN_DB") or None
        )

        with engine.begin() as conn:
            conn.execute(
                text(
                    f"IF OBJECT_ID(N'{schema}.tbl', N'U') IS NULL CREATE TABLE {schema}.tbl (id INT PRIMARY KEY)"
                )
            )
            conn.execute(text(f"INSERT INTO {schema}.tbl (id) VALUES (1)"))

        with engine.connect() as conn:
            value = conn.execute(text(f"SELECT id FROM {schema}.tbl"))
            rows = [r[0] for r in value]
        assert rows == [1]
    finally:
        cleanup_db_containers(db_type)
