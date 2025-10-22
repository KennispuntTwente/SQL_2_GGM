# Tests source_to_staging parquet dump integration; Oracle -> all; all -> Oracle
# Tests both ConnectorX and SQLAlchemy dump modes
# Focuses on correct dump/upload of various data types between different types of SQL databases
# This ensures end-to-end functionality of parquet dump/upload with type fidelity

import os
from dotenv import load_dotenv

import pytest

from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
from utils.database.create_connectorx_uri import create_connectorx_uri
from utils.database.initialize_oracle_client import try_init_oracle_client
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
    host_for_docker,
)


load_dotenv("tests/.env")
initialized_oracle = try_init_oracle_client()


def _connectorx_uri_for(
    db_type: str, username: str, password: str, host: str, port: int, db_name: str
) -> str:
    if db_type == "postgres":
        return create_connectorx_uri(
            "postgres", username, password, host, port, db_name
        )
    if db_type == "mssql":
        return create_connectorx_uri("mssql", username, password, host, port, db_name)
    if db_type in ("mysql", "mariadb"):
        # MariaDB uses mysql scheme for ConnectorX
        return create_connectorx_uri("mysql", username, password, host, port, db_name)
    if db_type == "oracle":
        return create_connectorx_uri("oracle", username, password, host, port, db_name)
    raise ValueError(db_type)


def _two_step_parquet_transfer(
    src_engine,
    src_db_type: str,
    dst_engine,
    dst_db_type: str,
    table: str,
    tmp_dir: str,
    *,
    use_connectorx: bool,
    chunk_size: int = 2,
):
    src_schema, _ = schemas_for(src_db_type)
    _, dst_schema = schemas_for(dst_db_type)

    outdir = os.path.join(tmp_dir, f"dump_{src_db_type}_to_{dst_db_type}")
    os.makedirs(outdir, exist_ok=True)

    if use_connectorx:
        # Build a ConnectorX URI to read from the source
        host = host_for_docker()
        port = ports[src_db_type]
        # For Oracle, SQLAlchemy URL uses service_name in query; database attribute may be empty.
        # Ensure we pass the correct service name to ConnectorX, otherwise login may hit the wrong service.
        dbname = src_engine.url.database
        if src_db_type == "oracle":
            try:
                dbname = src_engine.url.query.get("service_name") or dbname
            except Exception:
                pass
        uri = _connectorx_uri_for(
            src_db_type,
            "sa",
            "S3cureP@ssw0rd!23243",
            host,
            port,
            dbname,
        )
        download_parquet(
            connection=uri,
            tables=[table],
            output_dir=outdir,
            chunk_size=chunk_size,
            schema=src_schema,
        )
    else:
        download_parquet(
            connection=src_engine,
            tables=[table],
            output_dir=outdir,
            chunk_size=chunk_size,
            schema=src_schema,
        )

    # Upload into destination
    upload_parquet(engine=dst_engine, schema=dst_schema, input_dir=outdir, cleanup=True)


@pytest.mark.slow
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
@pytest.mark.parametrize(
    "use_connectorx",
    [
        pytest.param(True, marks=pytest.mark.cx_dump, id="connectorx"),
        pytest.param(False, marks=pytest.mark.sa_dump, id="sqlalchemy"),
    ],
)
@pytest.mark.parametrize(
    "db_type",
    [
        pytest.param("postgres", marks=pytest.mark.postgres, id="oracle-to-postgres"),
        pytest.param("mssql", marks=pytest.mark.mssql, id="oracle-to-mssql"),
        pytest.param("mysql", marks=pytest.mark.mysql, id="oracle-to-mysql"),
        pytest.param("mariadb", marks=pytest.mark.mariadb, id="oracle-to-mariadb"),
    ],
)
def test_parquet_dump_oracle_to_all(
    tmp_path, use_connectorx, oracle_source_engine, db_type
):
    """
    For both ConnectorX and SQLAlchemy dump modes: launch Oracle once, create sample table and data,
    then export to Parquet and upload into Postgres, MSSQL, MySQL, and MariaDB, validating content.
    """
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = f"typetest_dump_{db_type}"

    # Create source table + data (in Oracle)
    with oracle_source_engine.begin() as sconn:
        create_table_and_data(sconn, "oracle", table)

    # Start destination engine for this param
    dst_engine = get_connection(
        db_type=db_type,
        db_name=f"test_dest_{db_type}",
        user=username,
        password=password,
        port=ports_dest[db_type],
        force_refresh=True,
        print_tables=False,
    )

    _two_step_parquet_transfer(
        oracle_source_engine,
        "oracle",
        dst_engine,
        db_type,
        table,
        str(tmp_path),
        use_connectorx=use_connectorx,
        chunk_size=2,
    )

    with oracle_source_engine.connect() as sconn, dst_engine.connect() as dconn:
        src_rows = fetch_all(sconn, "oracle", table)
        dst_rows = fetch_all(dconn, db_type, table)
    assert normalize_rows(src_rows) == normalize_rows(dst_rows)
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
@pytest.mark.parametrize(
    "use_connectorx",
    [
        pytest.param(True, marks=pytest.mark.cx_dump, id="connectorx"),
        pytest.param(False, marks=pytest.mark.sa_dump, id="sqlalchemy"),
    ],
)
@pytest.mark.skipif(
    not initialized_oracle,
    reason="Oracle Instant Client not initialized; required for Oracle tests.",
)
@pytest.mark.parametrize(
    "db_type",
    [
        pytest.param("postgres", marks=pytest.mark.postgres, id="postgres-to-oracle"),
        pytest.param("mssql", marks=pytest.mark.mssql, id="mssql-to-oracle"),
        pytest.param("mysql", marks=pytest.mark.mysql, id="mysql-to-oracle"),
        pytest.param("mariadb", marks=pytest.mark.mariadb, id="mariadb-to-oracle"),
    ],
)
def test_parquet_dump_all_to_oracle(tmp_path, use_connectorx, oracle_dest_engine, db_type):
    """
    For both ConnectorX and SQLAlchemy dump modes: transfer from Postgres, MSSQL, MySQL, MariaDB to Oracle.
    """
    username = "sa"
    password = "S3cureP@ssw0rd!23243"

    table = f"typetest_{db_type}src_dump"

    # Spin up source
    src_engine = get_connection(
        db_type=db_type,
        db_name=f"test_source_{db_type}",
        user=username,
        password=password,
        port=ports[db_type],
        force_refresh=True,
        print_tables=False,
    )

    # Create source table + data
    with src_engine.begin() as sconn:
        create_table_and_data(sconn, db_type, table)

    _two_step_parquet_transfer(
        src_engine,
        db_type,
        oracle_dest_engine,
        "oracle",
        table,
        str(tmp_path),
        use_connectorx=use_connectorx,
        chunk_size=2,
    )

    with src_engine.connect() as sconn, oracle_dest_engine.connect() as dconn:
        src_rows = fetch_all(sconn, db_type, table)
        dst_rows = fetch_all(dconn, "oracle", table)
    assert normalize_rows(src_rows) == normalize_rows(dst_rows)
    cleanup_db_containers(db_type)
