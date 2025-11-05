import pytest
from sqlalchemy import text
from dotenv import load_dotenv

from dev_sql_server.get_connection import get_connection
from source_to_staging.functions.direct_transfer import direct_transfer
from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
from .integration_utils import (
    ports,
    ports_dest,
    docker_running,
    slow_tests_enabled,
    cleanup_db_containers,
    schemas_for,
)


load_dotenv("tests/.env")


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
def test_write_modes_direct_transfer_postgres(tmp_path):
    """Validate append and truncate behaviors for direct transfer on Postgres using Dockerized DBs."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = "wmtest_direct"

    # Clean slate for this db type
    cleanup_db_containers("postgres")

    try:
        # Spin up source and destination
        src_engine = get_connection(
            db_type="postgres",
            db_name="wm_src_pg",
            user=username,
            password=password,
            port=ports["postgres"],
            force_refresh=True,
            print_tables=False,
        )
        dst_engine = get_connection(
            db_type="postgres",
            db_name="wm_dst_pg",
            user=username,
            password=password,
            port=ports_dest["postgres"],
            force_refresh=True,
            print_tables=False,
        )
        src_schema, dst_schema = schemas_for("postgres")

        # Source: create small table with 3 rows
        with src_engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            conn.execute(text(f"CREATE TABLE {table} (id INT PRIMARY KEY, name TEXT)"))
            conn.execute(text(f"INSERT INTO {table} VALUES (1,'a'),(2,'b'),(3,'c')"))

        # Destination: pre-create table with 1 row to test append
        with dst_engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            conn.execute(text(f"CREATE TABLE {table} (id INT PRIMARY KEY, name TEXT)"))
            conn.execute(text(f"INSERT INTO {table} VALUES (100,'pre')"))

        # Append case: expect 4 rows after transfer
        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_engine,
            tables=[table],
            source_schema=src_schema,
            dest_schema=dst_schema,
            chunk_size=2,
            lowercase_columns=True,
            write_mode="append",
        )
        with dst_engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
        assert count == 4

        # Truncate case: prefill again, then truncate and load
        with dst_engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            conn.execute(text(f"INSERT INTO {table} VALUES (200,'pre1'),(201,'pre2')"))

        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_engine,
            tables=[table],
            source_schema=src_schema,
            dest_schema=dst_schema,
            chunk_size=2,
            lowercase_columns=True,
            write_mode="truncate",
        )
        with dst_engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
        assert count == 3
    finally:
        cleanup_db_containers("postgres")


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
def test_write_modes_parquet_postgres(tmp_path):
    """Validate append and truncate behaviors for Parquet upload on Postgres using Dockerized DBs."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = "wmtest_parquet"

    # Clean slate for this db type
    cleanup_db_containers("postgres")

    try:
        # Spin up source and destination
        src_engine = get_connection(
            db_type="postgres",
            db_name="wm_src_pg2",
            user=username,
            password=password,
            port=ports["postgres"],
            force_refresh=True,
            print_tables=False,
        )
        dst_engine = get_connection(
            db_type="postgres",
            db_name="wm_dst_pg2",
            user=username,
            password=password,
            port=ports_dest["postgres"],
            force_refresh=True,
            print_tables=False,
        )
        src_schema, dst_schema = schemas_for("postgres")

        # Source: create small table with 3 rows
        with src_engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            conn.execute(text(f"CREATE TABLE {table} (id INT PRIMARY KEY, name TEXT)"))
            conn.execute(text(f"INSERT INTO {table} VALUES (1,'a'),(2,'b'),(3,'c')"))

        # Dump to Parquet (2-row chunks)
        out_dir = tmp_path / "parquet"
        out_dir.mkdir(parents=True, exist_ok=True)
        download_parquet(
            connection=src_engine,
            tables=[table],
            output_dir=str(out_dir),
            chunk_size=2,
            schema=src_schema,
        )

        # Destination: pre-create with 1 row to test append
        with dst_engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            conn.execute(text(f"CREATE TABLE {table} (id INT PRIMARY KEY, name TEXT)"))
            conn.execute(text(f"INSERT INTO {table} VALUES (100,'pre')"))

        # Append case: expect 4 rows after upload
        upload_parquet(
            engine=dst_engine,
            schema=dst_schema,
            input_dir=str(out_dir),
            cleanup=False,
            write_mode="append",
        )
        with dst_engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
        assert count == 4

        # Truncate case: prefill again, then truncate behavior should clear and load 3
        with dst_engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            conn.execute(text(f"INSERT INTO {table} VALUES (200,'pre1'),(201,'pre2')"))

        upload_parquet(
            engine=dst_engine,
            schema=dst_schema,
            input_dir=str(out_dir),
            cleanup=False,
            write_mode="truncate",
        )
        with dst_engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
        assert count == 3
    finally:
        cleanup_db_containers("postgres")
