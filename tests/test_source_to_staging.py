# Test migration functions across multiple database types using the demo logic
# Run `pytest -v tests/test_source_to_staging.py` to execute this test

import shutil
from pathlib import Path
import pytest
from sqlalchemy import text

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.create_connectorx_uri import create_connectorx_uri

import oracledb

oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_18")

# Configuration for different database types and ports
db_types = ["mariadb", "mysql", "postgres", "oracle", "mssql"]
ports = {
    "mariadb": 3307,
    "mysql": 2053,
    "postgres": 5433,
    "oracle": 1522,
    "mssql": 1434,
}

# Temporary dump directory
base_dump_dir = Path("./tmp_dump")

# Table definition and sample data
table_name = "demotable"
create_sql = f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, val VARCHAR(50))"
insert_sql = f"INSERT INTO {table_name} (id, val) VALUES (1, 'foo'), (2, 'bar')"

# Make fake credentials which meets SQL server requirements
username = "sa"
password = "S3cureP@ssw0rd!23243"


# Define procedure
def run_migration_for_db_type(
    db_type: str,
    connectorx: bool = False,
):
    print()
    print(f"\n--- DEMO for {db_type.upper()} ---")
    port = ports[db_type]

    # Prepare dump directory
    dump_dir = base_dump_dir / db_type
    if dump_dir.exists():
        shutil.rmtree(dump_dir)
    dump_dir.mkdir(parents=True)

    # Start source container & get engine
    source_engine = get_connection(
        db_type=db_type,
        db_name="test_source",
        user=username,
        password=password,
        port=port,
        force_refresh=True,
        sql_folder=None,
        print_tables=False,
    )

    # Create table and insert data in source
    with source_engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        conn.execute(text(create_sql))
        conn.execute(text(insert_sql))
    print("Source table created and data inserted")

    if connectorx:
        # Set ConnectorX URI (instead of current SQLAlchemy engine)
        source_engine = create_connectorx_uri(
            driver=db_type,
            username=username,
            password=password,
            host="localhost",
            port=port,
            database="test_source",
        )

    # Dump to Parquet
    download_parquet(source_engine, [table_name], output_dir=str(dump_dir))
    print(f"Dumped table to parquet under {dump_dir}")

    # Start destination container & get engine
    dest_engine = get_connection(
        db_type=db_type,
        db_name="test_dest",
        user=username,
        password=password,
        port=port,
        force_refresh=True,
        sql_folder=None,
        print_tables=False,
    )

    # Choose schema based on db_type
    if db_type == "oracle":
        schema = username
    elif db_type == "postgres":
        schema = "public"
    elif db_type == "mssql":
        schema = "dbo"
    else:
        schema = None  # MySQL and others don't typically use named schemas

    # Upload Parquet to destination
    upload_parquet(dest_engine, schema=schema, input_dir=str(dump_dir))
    print("Uploaded parquet data into destination database")

    # Verify results
    with dest_engine.connect() as conn:
        rows = conn.execute(
            text(f"SELECT id, val FROM {table_name} ORDER BY id")
        ).fetchall()

    assert rows == [(1, "foo"), (2, "bar")]


# Define test which runs procedure for each db_type and for both with/without ConnectorX
# ConnectorX support varies by driver; exclude those it doesn't support.
supported_by_connectorx = {"mariadb", "mysql", "postgres", "mssql", "oracle"}


@pytest.mark.parametrize("db_type", db_types)
@pytest.mark.parametrize("connectorx", [False, True])
def test_migration_roundtrip(db_type, connectorx, tmp_path):
    if connectorx and db_type not in supported_by_connectorx:
        pytest.skip(f"ConnectorX is not supported for {db_type}")
    run_migration_for_db_type(db_type, connectorx=connectorx)
