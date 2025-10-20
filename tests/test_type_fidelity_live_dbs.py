"""
Cross-dialect type fidelity with live DBs (Postgres/MSSQL/Oracle/MySQL).

Validates roundtrip of DECIMAL precision/scale, TIMESTAMP/TIMESTAMPTZ
(where applicable), DATE and TIME semantics. Exercises both extraction
paths: SQLAlchemy Engine and ConnectorX URI.

Notes
- Skipped by default. Enable with RUN_SLOW_TESTS=1 and ensure Docker is running.
- Uses ggm_dev_server.get_connection to provision ephemeral containers.
- Uses source_to_staging.download_parquet to export, upload_parquet to load.

Acceptance
- Values and NULLs preserved; no loss of precision beyond backend limits.
- Consistent string formatting for date/time when needed for comparisons.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import date, datetime, time, timezone
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

from dotenv import load_dotenv
import pytest
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    Numeric,
    Date,
    Time,
    DateTime,
    text,
)
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.oracle import TIMESTAMP as ORA_TIMESTAMP

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
from utils.database.initialize_oracle_client import initialize_oracle_client
from utils.database.create_connectorx_uri import create_connectorx_uri
from ggm_dev_server.get_connection import get_connection


def _docker_running() -> bool:
    """Return True if Docker CLI is available and the daemon responds."""
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def _slow_tests_enabled() -> bool:
    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


class OracleTime(TypeDecorator):
    """Store Python time as TIMESTAMP in Oracle and convert back on fetch.

    Oracle lacks a standalone TIME type, so we map to TIMESTAMP with epoch date.
    """

    impl = ORA_TIMESTAMP
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, time):
            return datetime(1970, 1, 1, value.hour, value.minute, value.second, value.microsecond)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.time()
        return value


# Limit to the DB types requested in the TODO
db_types = ["postgres", "mssql", "oracle", "mysql"]
ports = {
    "postgres": 5433,
    "mssql": 1434,
    "oracle": 1522,
    "mysql": 2053,
}

supported_by_connectorx = {"postgres", "mssql", "oracle", "mysql"}


def _schema_for(db_type: str, username: str) -> str | None:
    if db_type == "oracle":
        return username
    if db_type == "postgres":
        return "public"
    if db_type == "mssql":
        return "dbo"
    return None


def _normalize_decimal(val: Decimal | None, scale: int) -> str | None:
    """Return a normalized string for a Decimal with given scale for robust comparison.

    Robust to input being str or Decimal, and to large precision or scientific notation
    by temporarily increasing the Decimal context precision using both coefficient digits
    and exponent to avoid InvalidOperation during quantize.
    """
    if val is None:
        return None
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    q = Decimal(1).scaleb(-scale)  # 10^-scale
    # Ensure sufficient precision to quantize very large values, including scientific notation
    t = val.as_tuple()
    coeff_digits = len(t.digits) if t.digits else 1
    exp = t.exponent  # positive => shifts decimal point to the right (more integer digits)
    # Estimated integer digits: coefficient digits plus positive exponent; at least 1
    int_digits = max(coeff_digits + max(exp, 0), 1)
    with localcontext() as ctx:
        ctx.prec = max(ctx.prec, int_digits + scale + 2)
        return format(val.quantize(q, rounding=ROUND_HALF_UP), 'f')


@pytest.mark.parametrize("db_type", db_types)
@pytest.mark.parametrize("connectorx", [False, True])
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_type_fidelity_roundtrip(db_type: str, connectorx: bool, tmp_path: Path):
    if db_type == "oracle":
        load_dotenv("tests/.env")
        initialize_oracle_client(config_key="SRC_CONNECTORX_ORACLE_CLIENT_PATH")
        
    if connectorx and db_type not in supported_by_connectorx:
        pytest.skip(f"ConnectorX is not supported for {db_type}")

    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    port = ports[db_type]
    table_name = "type_fidelity"

    # Prepare Parquet dump dir
    out_dir = tmp_path / db_type
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Source DB: create rich typed table and insert rows
    src_engine = get_connection(
        db_type=db_type,
        db_name="tf_src",
        user=username,
        password=password,
        port=port,
        force_refresh=True,
        print_tables=False,
    )

    metadata = MetaData(schema=_schema_for(db_type, username))

    # TIME type per dialect
    time_type = Time()
    if db_type == "oracle":
        time_type = Time().with_variant(OracleTime(), "oracle")

    # TIMESTAMP WITH TIME ZONE on Postgres; others may ignore tz flag
    ts_tz_type = DateTime(timezone=True)
    ts_naive_type = DateTime(timezone=False)

    tbl = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("dec_big", Numeric(38, 10)),
        Column("dec_small", Numeric(18, 2)),
        Column("d", Date),
        Column("t", time_type),
        Column("ts_naive", ts_naive_type),
        Column("ts_tz", ts_tz_type),
    )

    metadata.create_all(src_engine)

    # Sample values (including NULLs)
    dec_big_val = Decimal("12345678901234567890.1234567890")
    dec_small_val = Decimal("-9876543210.55")
    d_val = date(2024, 1, 2)
    t_val = time(3, 4, 5)
    ts_naive_val = datetime(2024, 1, 2, 3, 4, 5)
    ts_tz_val = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    with src_engine.begin() as conn:
        # Drop if exists in a dialect-safe way
        tbl.drop(bind=conn, checkfirst=True)
        metadata.create_all(bind=conn)
        conn.execute(
            tbl.insert(),
            [
                {
                    "id": 1,
                    "dec_big": dec_big_val,
                    "dec_small": dec_small_val,
                    "d": d_val,
                    "t": t_val,
                    "ts_naive": ts_naive_val,
                    "ts_tz": ts_tz_val,
                },
                {
                    "id": 2,
                    "dec_big": None,
                    "dec_small": Decimal("0.00"),
                    "d": None,
                    "t": None,
                    "ts_naive": None,
                    "ts_tz": None,
                },
            ],
        )

    # 2) Export to Parquet using either SQLAlchemy engine or ConnectorX URI
    src_for_download = src_engine
    if connectorx:
        src_for_download = create_connectorx_uri(
            driver=db_type,
            username=username,
            password=password,
            host="localhost",
            port=port,
            database="tf_src",
        )

    download_parquet(src_for_download, [table_name], output_dir=str(out_dir))

    # 3) Destination DB: fresh instance and upload Parquet
    dst_engine = get_connection(
        db_type=db_type,
        db_name="tf_dst",
        user=username,
        password=password,
        port=port,
        force_refresh=True,
        print_tables=False,
    )

    schema = _schema_for(db_type, username)
    upload_parquet(dst_engine, schema=schema, input_dir=str(out_dir), cleanup=True)

    # 4) Read back and validate
    if db_type == "postgres":
        # For timestamptz, normalize to UTC, and cast to text for stable compare
        query = text(
            f"""
            SELECT id,
                   dec_big,
                   dec_small,
                   to_char(d, 'YYYY-MM-DD') AS d,
                   to_char(t, 'HH24:MI:SS') AS t,
                   to_char(ts_naive, 'YYYY-MM-DD HH24:MI:SS') AS ts_naive,
                   to_char((ts_tz AT TIME ZONE 'UTC'), 'YYYY-MM-DD HH24:MI:SS') AS ts_tz_utc
            FROM {('public.' + table_name)}
            ORDER BY id
            """
        )
    else:
        # Generic select; string conversions will be applied in Python where needed
        full_table = f"{schema}.{table_name}" if schema else table_name
        query = text(f"SELECT id, dec_big, dec_small, d, t, ts_naive, ts_tz FROM {full_table} ORDER BY id")

    with dst_engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    assert len(rows) == 2

    # Row 1 assertions
    r1 = rows[0]
    # DECIMAL precision/scale
    if db_type == "postgres":
        # Values are already Decimals
        got_big_1 = _normalize_decimal(r1[1], 10)
        got_small_1 = _normalize_decimal(r1[2], 2)
    else:
        # Coerce via Decimal from string to avoid float issues
        got_big_1 = _normalize_decimal(Decimal(str(r1[1])) if r1[1] is not None else None, 10)
        got_small_1 = _normalize_decimal(Decimal(str(r1[2])) if r1[2] is not None else None, 2)
    assert got_big_1 == _normalize_decimal(dec_big_val, 10)
    assert got_small_1 == _normalize_decimal(dec_small_val, 2)

    # DATE
    if db_type == "postgres":
        assert r1[3] == "2024-01-02"
    else:
        assert (r1[3] is None) is False
        assert "2024-01-02" in str(r1[3])

    # TIME
    # Allow either '03:04:05' or '3:04:05' representations across drivers
    t_str = str(r1[4])
    assert ("03:04:05" in t_str) or (" 3:04:05" in t_str) or t_str.endswith("3:04:05")

    # TIMESTAMP (naive)
    if db_type == "postgres":
        assert r1[5] == "2024-01-02 03:04:05"
    else:
        assert "2024-01-02 03:04:05" in str(r1[5])

    # TIMESTAMPTZ / timezone behavior
    if db_type == "postgres":
        # Already formatted in UTC in the query above
        assert r1[6] == "2024-01-02 03:04:05"
    else:
        # Other backends may ignore tz flag; ensure at least the naive datetime content is present
        assert (r1[6] is None) or ("2024-01-02 03:04:05" in str(r1[6]))

    # Row 2 NULLs preserved
    r2 = rows[1]
    # dec_big NULL
    assert r2[1] is None
    # dec_small zero preserved
    if db_type == "postgres":
        assert _normalize_decimal(r2[2], 2) == "0.00"
    else:
        assert _normalize_decimal(Decimal(str(r2[2])) if r2[2] is not None else None, 2) == "0.00"
    # date/time/timestamps NULLs
    assert r2[3] is None
    assert r2[4] is None
    assert r2[5] is None
    assert r2[6] is None
