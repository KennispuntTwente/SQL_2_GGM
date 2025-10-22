# Tests source_to_staging direct_transfer integration; Oracle -> all; all -> Oracle; Postgres -> MSSQL
# Focuses on correct transfer of various data types between different types of SQL databases
# This ensures end-to-end functionality of direct_transfer with type fidelity

import pytest
from dotenv import load_dotenv
from utils.database.initialize_oracle_client import try_init_oracle_client

from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.direct_transfer import direct_transfer
from .integration_utils import (
    ports,
    ports_dest,
    docker_running,
    slow_tests_enabled,
    cleanup_db_containers,
    schemas_for,
    create_table_and_data,
    fetch_all,
    normalize_rows,
)


load_dotenv("tests/.env")
initialized_oracle = try_init_oracle_client()


@pytest.mark.slow
@pytest.mark.sa_direct
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not initialized_oracle,
    reason="Oracle Instant Client not initialized; required for Oracle tests.",
)
@pytest.mark.sa_direct
@pytest.mark.parametrize(
    "db_type",
    [
        pytest.param("postgres", marks=pytest.mark.postgres, id="oracle-to-postgres"),
        pytest.param("mssql", marks=pytest.mark.mssql, id="oracle-to-mssql"),
        pytest.param("mysql", marks=pytest.mark.mysql, id="oracle-to-mysql"),
        pytest.param("mariadb", marks=pytest.mark.mariadb, id="oracle-to-mariadb"),
    ],
)
def test_direct_transfer_oracle_to_all(oracle_source_engine, db_type):
    """Oracle -> one destination (parametrized by db_type). Oracle container starts once per session."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = f"typetest_{db_type}"

    # Create/replace source table + data (in Oracle) for this case
    with oracle_source_engine.begin() as sconn:
        create_table_and_data(sconn, "oracle", table)

    # Start destination engine
    dst_engine = get_connection(
        db_type=db_type,
        db_name=f"test_dest_{db_type}",
        user=username,
        password=password,
        port=ports_dest[db_type],
        force_refresh=True,
        print_tables=False,
    )

    src_schema, _ = schemas_for("oracle")
    _, dst_schema = schemas_for(db_type)

    direct_transfer(
        source_engine=oracle_source_engine,
        dest_engine=dst_engine,
        tables=[table],
        source_schema=src_schema,
        dest_schema=dst_schema,
        chunk_size=2,
        lowercase_columns=True,
        write_mode="replace",
    )

    with oracle_source_engine.connect() as sconn, dst_engine.connect() as dconn:
        src_rows = fetch_all(sconn, "oracle", table)
        dst_rows = fetch_all(dconn, db_type, table)
    assert normalize_rows(src_rows) == normalize_rows(dst_rows)
    # Clean only the destination we started in this case
    cleanup_db_containers(db_type)


@pytest.mark.slow
@pytest.mark.sa_direct
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_direct_transfer_postgres_to_mssql():
    """Transfer from Postgres (source) to MSSQL (destination) and validate contents."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = "typetest"

    # Ensure a clean slate before starting
    cleanup_db_containers("postgres")
    cleanup_db_containers("mssql")

    try:
        # Spin up Postgres source
        src_engine = get_connection(
            db_type="postgres",
            db_name="test_source_pg",
            user=username,
            password=password,
            port=ports["postgres"],
            force_refresh=True,
            print_tables=False,
        )

        # Create source table + data
        with src_engine.begin() as sconn:
            create_table_and_data(sconn, "postgres", table)

        # Spin up MSSQL destination
        dst_engine = get_connection(
            db_type="mssql",
            db_name="test_dest_ms",
            user=username,
            password=password,
            port=ports_dest["mssql"],
            force_refresh=True,
            print_tables=False,
        )

        src_schema, _ = schemas_for("postgres")
        _, dst_schema = schemas_for("mssql")

        # Run direct transfer with small chunks
        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_engine,
            tables=[table],
            source_schema=src_schema,
            dest_schema=dst_schema,
            chunk_size=2,
            lowercase_columns=True,
            write_mode="replace",
        )

        # Compare
        with src_engine.connect() as sconn, dst_engine.connect() as dconn:
            src_rows = fetch_all(sconn, "postgres", table)
            dst_rows = fetch_all(dconn, "mssql", table)

        assert normalize_rows(src_rows) == normalize_rows(dst_rows)
    finally:
        # Always clean up containers/volumes after test
        cleanup_db_containers("postgres")
        cleanup_db_containers("mssql")


@pytest.mark.slow
@pytest.mark.sa_direct
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not initialized_oracle,
    reason="Oracle Instant Client not initialized; required for Oracle tests.",
)
@pytest.mark.sa_direct
@pytest.mark.parametrize(
    "db_type",
    [
        pytest.param("postgres", marks=pytest.mark.postgres, id="postgres-to-oracle"),
        pytest.param("mssql", marks=pytest.mark.mssql, id="mssql-to-oracle"),
        pytest.param("mysql", marks=pytest.mark.mysql, id="mysql-to-oracle"),
        pytest.param("mariadb", marks=pytest.mark.mariadb, id="mariadb-to-oracle"),
    ],
)
def test_direct_transfer_all_to_oracle(oracle_dest_engine, db_type):
    """One source (parametrized) -> Oracle destination. Oracle starts once per session."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"

    # Spin up source for this case
    src_engine = get_connection(
        db_type=db_type,
        db_name=f"test_source_{db_type}",
        user=username,
        password=password,
        port=ports[db_type],
        force_refresh=True,
        print_tables=False,
    )
    src_schema, _ = schemas_for(db_type)
    _, dst_schema_oracle = schemas_for("oracle")

    table = f"typetest_{db_type}src"
    with src_engine.begin() as sconn:
        create_table_and_data(sconn, db_type, table)

    # Transfer to Oracle
    direct_transfer(
        source_engine=src_engine,
        dest_engine=oracle_dest_engine,
        tables=[table],
        source_schema=src_schema,
        dest_schema=dst_schema_oracle,
        chunk_size=2,
        lowercase_columns=True,
        write_mode="replace",
    )

    # Compare
    with src_engine.connect() as sconn, oracle_dest_engine.connect() as dconn:
        src_rows = fetch_all(sconn, db_type, table)
        dst_rows = fetch_all(dconn, "oracle", table)
    assert normalize_rows(src_rows) == normalize_rows(dst_rows)
    cleanup_db_containers(db_type)
