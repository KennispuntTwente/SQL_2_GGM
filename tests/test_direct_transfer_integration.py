import os
import shutil
import subprocess
from datetime import date, datetime

import pytest
from sqlalchemy import text

from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.direct_transfer import direct_transfer


def _docker_running() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def _slow_tests_enabled() -> bool:
    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


db_types = ["mariadb", "mysql", "postgres", "oracle", "mssql"]

# Use the same explicit host ports as tests/test_source_to_staging.py to avoid clashes
ports = {
    "mariadb": 3307,
    "mysql": 2053,
    "postgres": 5433,
    "oracle": 1522,
    "mssql": 1434,
}

# Destination containers use different ports to ensure two separate containers per db_type
ports_dest = {
    "mariadb": 3309,
    "mysql": 2054,
    "postgres": 5434,
    "oracle": 1523,
    "mssql": 1435,
}


def _schemas_for(db_type: str):
    if db_type == "oracle":
        return None, "sa"  # source_schema, dest_schema
    if db_type == "postgres":
        return None, "public"
    if db_type == "mssql":
        return None, "dbo"
    return None, None  # mysql/mariadb


def _create_table_and_data(conn, db_type: str, table: str):
    # Drop if exists
    if db_type == "postgres":
        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        ddl = f"""
        CREATE TABLE {table} (
            id INTEGER PRIMARY KEY,
            i32 INTEGER,
            s VARCHAR(50),
            n18_5 NUMERIC(18,5),
            d DATE,
            ts TIMESTAMP,
            b BOOLEAN
        )
        """
    elif db_type == "mssql":
        conn.execute(text(f"IF OBJECT_ID(N'{table}', N'U') IS NOT NULL DROP TABLE {table}"))
        ddl = f"""
        CREATE TABLE {table} (
            id INT PRIMARY KEY,
            i32 INT,
            s VARCHAR(50),
            n18_5 DECIMAL(18,5),
            d DATE,
            ts DATETIME2,
            b BIT
        )
        """
    elif db_type in ("mysql", "mariadb"):
        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        ddl = f"""
        CREATE TABLE {table} (
            id INT PRIMARY KEY,
            i32 INT,
            s VARCHAR(50),
            n18_5 DECIMAL(18,5),
            d DATE,
            ts DATETIME,
            b TINYINT(1)
        )
        """
    elif db_type == "oracle":
        # Oracle: use NUMBER types and DATE/TIMESTAMP
        try:
            conn.execute(text(f"DROP TABLE {table}"))
        except Exception:
            pass
        ddl = f"""
        CREATE TABLE {table} (
            id NUMBER(10) PRIMARY KEY,
            i32 NUMBER(10),
            s VARCHAR2(50),
            n18_5 NUMBER(18,5),
            d DATE,
            ts TIMESTAMP,
            b NUMBER(1)
        )
        """
    else:
        raise ValueError(db_type)

    conn.execute(text(ddl))

    rows = [
        dict(
            id=1,
            i32=123,
            s="alpha",
            n18_5=10.50000,
            d=date(2024, 1, 2),
            ts=datetime(2024, 1, 2, 3, 4, 5),
            b=True,
        ),
        dict(
            id=2,
            i32=None,
            s="beta",
            n18_5=0,
            d=date(1999, 12, 31),
            ts=datetime(2000, 1, 1, 0, 0, 0),
            b=False,
        ),
        dict(
            id=3,
            i32=-1,
            s=None,
            n18_5=99.99000,
            d=None,
            ts=None,
            b=None,
        ),
    ]

    if db_type in ("mysql", "mariadb"):
        # Convert booleans to tinyint
        for r in rows:
            if r["b"] is True:
                r["b"] = 1
            elif r["b"] is False:
                r["b"] = 0

    if db_type == "mssql":
        # BIT expects 0/1
        for r in rows:
            if r["b"] is True:
                r["b"] = 1
            elif r["b"] is False:
                r["b"] = 0

    # Parameterized insert to handle dates/timestamps cleanly
    ins = text(
        f"INSERT INTO {table} (id, i32, s, n18_5, d, ts, b) "
        f"VALUES (:id, :i32, :s, :n18_5, :d, :ts, :b)"
    )
    for r in rows:
        conn.execute(ins, r)


def _fetch_all(conn, db_type: str, table: str):
    # Normalize selection across DBs; sort by id
    rs = conn.execute(text(f"SELECT id, i32, s, n18_5, d, ts, b FROM {table} ORDER BY id")).fetchall()
    return [tuple(row) for row in rs]


def _normalize_rows(rows):
    def norm(v):
        import decimal

        if v is None:
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, (int,)):
            return v
        if isinstance(v, float):
            return round(v, 5)
        if isinstance(v, decimal.Decimal):
            # Normalize to string with up to 5 decimals to compare reliably across drivers
            q = decimal.Decimal("0.00001")
            return str(v.quantize(q, rounding=decimal.ROUND_HALF_UP))
        if hasattr(v, "isoformat"):
            # date or datetime
            try:
                return v.isoformat()
            except Exception:
                return str(v)
        return str(v)

    return [tuple(norm(x) for x in row) for row in rows]


@pytest.mark.parametrize("db_type", db_types)
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_direct_transfer_roundtrip(db_type):
    username = "sa"
    password = "S3cureP@ssw0rd!23243"

    # Spin up source
    port = ports[db_type]
    src_engine = get_connection(
        db_type=db_type,
        db_name="test_source",
        user=username,
        password=password,
        port=port,
        force_refresh=True,
        print_tables=False,
    )

    # Create source table + data
    table = "typetest"
    with src_engine.begin() as sconn:
        _create_table_and_data(sconn, db_type, table)

    # Spin up destination
    dst_engine = get_connection(
        db_type=db_type,
        db_name="test_dest",
        user=username,
        password=password,
        port=ports_dest[db_type],
        force_refresh=True,
        print_tables=False,
    )

    src_schema, dst_schema = _schemas_for(db_type)

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
        src_rows = _fetch_all(sconn, db_type, table)
        dst_rows = _fetch_all(dconn, db_type, table)

    assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)
