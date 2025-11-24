# Integration test for MSSQL DATETIME2 mapping in upload_parquet
# Ensures datetime-like columns are created as DATETIME2(6), support pre-1753 dates,
# and preserve microseconds

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import polars as pl
import pytest
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection
from utils.parquet.upload_parquet import upload_parquet


def _docker_running() -> bool:
    import subprocess

    try:
        res = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=5
        )
        return res.returncode == 0
    except Exception:
        return False


def _slow_tests_enabled() -> bool:
    import os

    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


def _mssql_driver_available() -> bool:
    try:
        import pyodbc  # noqa: F401

        return any("ODBC Driver 18 for SQL Server" in d for d in pyodbc.drivers())
    except Exception:
        return False


@pytest.mark.slow
@pytest.mark.mssql
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not _mssql_driver_available(),
    reason="ODBC Driver 18 for SQL Server not installed; required for MSSQL test.",
)
def test_upload_parquet_mssql_uses_datetime2(tmp_path: Path):
    # Spin up MSSQL test DB
    engine = get_connection(
        db_type="mssql",
        db_name="ggm_upload_parquet_dt2",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=1436,  # use a distinct port to avoid clashes with other tests
        force_refresh=True,
        sql_folder=None,
        sql_suffix_filter=True,
        sql_schema=None,
        print_tables=False,
    )

    # Build a Parquet file with datetime values including an out-of-DATETIME range and microseconds
    df = pl.DataFrame(
        {
            "id": pl.Series("id", [1, 2, 3], dtype=pl.Int64),
            # Pre-1753 date (would fail for DATETIME, but should be fine for DATETIME2)
            "dt": pl.Series(
                "dt",
                [
                    datetime(1500, 1, 1, 0, 0, 0),
                    datetime(
                        2024, 1, 2, 3, 4, 5, 123456
                    ),  # microseconds to test precision
                    None,
                ],
                dtype=pl.Datetime(time_unit="us"),
            ),
        }
    )

    in_dir = tmp_path / "parquet"
    in_dir.mkdir()
    (in_dir / "events.parquet").write_bytes(b"")  # ensure directory exists
    pq_path = in_dir / "events.parquet"
    df.write_parquet(pq_path)

    # Upload to MSSQL (default schema for sa is dbo). Columns are lowercased by upload_parquet.
    upload_parquet(engine, input_dir=str(in_dir), cleanup=False)

    # Validate the column type is DATETIME2 and precision is 6 (scale)
    with engine.connect() as conn:
        # Check metadata
        meta = conn.execute(
            text(
                """
                SELECT ty.name AS type_name, c.scale
                FROM sys.tables t
                JOIN sys.columns c ON c.object_id = t.object_id
                JOIN sys.types ty ON ty.user_type_id = c.user_type_id
                WHERE t.schema_id = SCHEMA_ID('dbo') AND t.name = 'events' AND c.name = 'dt'
                """
            )
        ).fetchone()
        assert meta is not None, "events.dt not found in MSSQL metadata"
        type_name, scale = meta
        assert type_name.lower() == "datetime2"
        # Expect DATETIME2(6)
        assert scale == 6

        # Fetch back values to verify roundtrip
        rows = conn.execute(
            text("SELECT id, dt FROM dbo.events ORDER BY id")
        ).fetchall()

    assert rows[0][1] == datetime(1500, 1, 1, 0, 0, 0)
    # Microseconds preserved
    assert rows[1][1] == datetime(2024, 1, 2, 3, 4, 5, 123456)
    # NULL preserved
    assert rows[2][1] is None
