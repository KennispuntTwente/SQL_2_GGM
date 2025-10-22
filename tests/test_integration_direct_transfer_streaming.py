# Tests streaming direct_transfer with small chunk sizes between Postgres source and Postgres dest
# Focus on just the streaming behavior with chunking
# This ensures that data is transferred in chunks and all rows arrive correctly

import logging
import os
import shutil
import subprocess
import re

import pytest
import docker
from sqlalchemy import text
from dotenv import load_dotenv

from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.direct_transfer import direct_transfer


load_dotenv("tests/.env")


def _docker_running() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=5
        )
        return res.returncode == 0
    except Exception:
        return False


def _slow_tests_enabled() -> bool:
    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


# Use explicit ports consistent with other integration tests
SRC_PORT = 5433
DST_PORT = 5434


def _cleanup_db_containers(name: str, port: int):
    """Stop and remove the container/volume our get_connection uses for a db/port pair."""
    client = docker.from_env()
    cname = f"{name}-docker-db-{port}"
    try:
        c = client.containers.get(cname)
        try:
            c.stop()
        except Exception:
            pass
        try:
            c.remove()
        except Exception:
            pass
    except Exception:
        pass
    # remove associated volume
    vname = f"{cname}_data"
    try:
        v = client.volumes.get(vname)
        v.remove(force=True)
    except Exception:
        pass


@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.parametrize(
    "total_rows,chunk_size,expected_batches",
    [
        (23, 5, [(5, 5), (5, 10), (5, 15), (5, 20), (3, 23)]),
        (10, 3, [(3, 3), (3, 6), (3, 9), (1, 10)]),
    ],
)
def test_direct_transfer_streams_in_chunks_postgres(
    caplog, total_rows, chunk_size, expected_batches
):
    """
    End-to-end: Postgres -> Postgres copy using direct_transfer with small chunk_size.
    Validates that multiple insert batches occur (from logs) and all rows arrive.
    """
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = "stream_check"

    # Ensure a clean slate before starting
    _cleanup_db_containers("postgres", SRC_PORT)
    _cleanup_db_containers("postgres", DST_PORT)

    try:
        # Start Postgres source and create table with many rows
        src_engine = get_connection(
            db_type="postgres",
            db_name="test_source_pg_stream",
            user=username,
            password=password,
            port=SRC_PORT,
            force_refresh=True,
            print_tables=False,
        )
        with src_engine.begin() as sconn:
            sconn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            sconn.execute(
                text(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, txt TEXT)")
            )
            # Insert total_rows rows
            ins = text(f"INSERT INTO {table} (id, txt) VALUES (:id, :txt)")
            for i in range(1, total_rows + 1):
                sconn.execute(ins, {"id": i, "txt": f"row-{i}"})

        # Start Postgres destination
        dst_engine = get_connection(
            db_type="postgres",
            db_name="test_dest_pg_stream",
            user=username,
            password=password,
            port=DST_PORT,
            force_refresh=True,
            print_tables=False,
        )

        # Capture info logs from direct_transfer
        caplog.set_level(logging.INFO, logger="source_to_staging.direct_transfer")

        # Transfer with small chunk size to force multiple batches
        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_engine,
            tables=[table],
            source_schema=None,
            dest_schema="public",
            chunk_size=chunk_size,
            lowercase_columns=True,
            write_mode="replace",
        )

        # Validate destination row count
        with dst_engine.connect() as dconn:
            count = dconn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            rows = dconn.execute(
                text(f"SELECT id, txt FROM {table} ORDER BY id")
            ).fetchall()
        assert count == total_rows
        assert len(rows) == total_rows
        assert rows[0] == (1, "row-1")
        assert rows[-1] == (total_rows, f"row-{total_rows}")

        # Validate batched insert logs
        pattern = re.compile(r"inserted (\d+) rows \(total (\d+)\)")
        inserts = []
        for rec in caplog.records:
            if rec.name == "source_to_staging.direct_transfer":
                m = pattern.search(rec.getMessage())
                if m:
                    inserts.append((int(m.group(1)), int(m.group(2))))
        assert inserts == expected_batches
    finally:
        _cleanup_db_containers("postgres", SRC_PORT)
        _cleanup_db_containers("postgres", DST_PORT)
