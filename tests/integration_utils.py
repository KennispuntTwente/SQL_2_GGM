"""
Shared utilities and fixtures for DB-backed integration tests.

Centralizes:
- Port mappings and container cleanup
- Docker/slow-test guards
- Schema resolution per dialect
- Sample table DDL + data insertion
- Row fetching and normalization for cross-dialect equality
- Reusable Oracle engines with minimal startups
"""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import date, datetime, time
from typing import Iterable

import pytest
import docker
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection


# Explicit host ports used by integration tests for consistency across files
ports = {
    "mariadb": 3307,
    "mysql": 2053,
    "postgres": 5433,
    "oracle": 1522,
    "mssql": 1434,
}

ports_dest = {
    "mariadb": 3309,
    "mysql": 2054,
    "postgres": 5434,
    "oracle": 1523,
    "mssql": 1435,
}


def docker_running() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def slow_tests_enabled() -> bool:
    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


def cleanup_db_containers(db_type: str):
    """Stop and remove the containers and volumes created by tests for a db_type.

    Tests name containers like "{db}-docker-db-{port}".
    """
    client = docker.from_env()
    names = [f"{db_type}-docker-db-{ports[db_type]}", f"{db_type}-docker-db-{ports_dest[db_type]}"]
    for name in names:
        try:
            c = client.containers.get(name)
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
        # Remove volume as well
        vol_name = f"{name}_data"
        try:
            v = client.volumes.get(vol_name)
            v.remove(force=True)
        except Exception:
            pass


def cleanup_many(db_types: Iterable[str]):
    for t in db_types:
        cleanup_db_containers(t)


def schemas_for(db_type: str):
    if db_type == "oracle":
        return None, "sa"  # source_schema, dest_schema
    if db_type == "postgres":
        return None, "public"
    if db_type == "mssql":
        return None, "dbo"
    return None, None  # mysql/mariadb


def create_table_and_data(conn, db_type: str, table: str):
    """Create a representative mixed-type table and insert sample rows.

    The DDL matches across tests; values exercise nullables, unicode, binary,
    numerics, booleans, and timestamps.
    """
    if db_type == "postgres":
        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        ddl = f"""
        CREATE TABLE {table} (
            id INTEGER PRIMARY KEY,
            i32 INTEGER,
            smi SMALLINT,
            bigi BIGINT,
            s VARCHAR(50),
            n18_5 NUMERIC(18,5),
            f32 REAL,
            f64 DOUBLE PRECISION,
            t TEXT,
            u TEXT,
            bin BYTEA,
            d DATE,
            ts TIMESTAMP,
            dt_str TEXT,
            b BOOLEAN
        )
        """
    elif db_type == "mssql":
        conn.execute(text(f"IF OBJECT_ID(N'{table}', N'U') IS NOT NULL DROP TABLE {table}"))
        ddl = f"""
        CREATE TABLE {table} (
            id INT PRIMARY KEY,
            i32 INT,
            smi SMALLINT,
            bigi BIGINT,
            s VARCHAR(50),
            n18_5 DECIMAL(18,5),
            f32 REAL,
            f64 FLOAT(53),
            t NVARCHAR(MAX),
            u NVARCHAR(200),
            bin VARBINARY(MAX),
            d DATE,
            ts DATETIME2,
            dt_str NVARCHAR(MAX),
            b BIT
        )
        """
    elif db_type in ("mysql", "mariadb"):
        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        ddl = f"""
        CREATE TABLE {table} (
            id INT PRIMARY KEY,
            i32 INT,
            smi SMALLINT,
            bigi BIGINT,
            s VARCHAR(50),
            n18_5 DECIMAL(18,5),
            f32 FLOAT,
            f64 DOUBLE,
            t TEXT,
            u TEXT,
            bin BLOB,
            d DATE,
            ts DATETIME(6),
            dt_str TEXT,
            b TINYINT(1)
        )
        """
    elif db_type == "oracle":
        try:
            conn.execute(text(f"DROP TABLE {table}"))
        except Exception:
            pass
        ddl = f"""
        CREATE TABLE {table} (
            id NUMBER(10) PRIMARY KEY,
            i32 NUMBER(10),
            smi NUMBER(5),
            bigi NUMBER(19),
            s VARCHAR2(50),
            n18_5 NUMBER(18,5),
            f32 BINARY_FLOAT,
            f64 BINARY_DOUBLE,
            t CLOB,
            u CLOB,
            bin BLOB,
            d DATE,
            ts TIMESTAMP,
            dt_str CLOB,
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
            smi=-12,
            bigi=2_147_483_648,  # > INT
            s="alpha",
            n18_5=10.50000,
            f32=1.5,
            f64=1.23456789,
            t="lorem ipsum dolor sit amet",
            u="café 🚀",
            bin=b"\x00\x01A\xff",
            d=date(2024, 1, 2),
            ts=datetime(2024, 1, 2, 3, 4, 5, 123456),
            dt_str="2024-01-02T03:04:05.123456",
            b=True,
        ),
        dict(
            id=2,
            i32=None,
            smi=0,
            bigi=0,
            s="beta",
            n18_5=0,
            f32=0.0,
            f64=-2.5,
            t="",
            u="βeta-Δ",
            bin=b"",
            d=date(1999, 12, 31),
            ts=datetime(2000, 1, 1, 0, 0, 0),
            dt_str="31/12/1999",
            b=False,
        ),
        dict(
            id=3,
            i32=-1,
            smi=None,
            bigi=None,
            s=None,
            n18_5=99.99000,
            f32=None,
            f64=None,
            t=None,
            u=None,
            bin=None,
            d=None,
            ts=None,
            dt_str=None,
            b=None,
        ),
    ]

    # Normalize booleans for dialects that store as 0/1
    if db_type in ("mysql", "mariadb", "mssql"):
        for r in rows:
            if r["b"] is True:
                r["b"] = 1
            elif r["b"] is False:
                r["b"] = 0

    ins = text(
        f"INSERT INTO {table} (id, i32, s, n18_5, d, ts, dt_str, b) "
        f"VALUES (:id, :i32, :s, :n18_5, :d, :ts, :dt_str, :b)"
    )
    for r in rows:
        conn.execute(ins, r)


def fetch_all(conn, db_type: str, table: str):
    rs = conn.execute(
        text(
            f"SELECT id, i32, smi, bigi, s, n18_5, f32, f64, t, u, bin, d, ts, dt_str, b FROM {table} ORDER BY id"
        )
    ).fetchall()
    return [tuple(row) for row in rs]


def _to_millis(dt: datetime) -> str:
    # Truncate to millisecond precision for cross‑engine consistency
    micros = dt.microsecond // 1000  # 0..999
    base = dt.replace(microsecond=0).isoformat()
    return f"{base}.{micros:03d}"


def normalize_rows(rows):
    def norm(v):
        import decimal
        import datetime as _dt

        if v is None:
            return None
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, (int,)):
            return v
        if isinstance(v, float):
            # Represent floats as fixed 5‑decimal strings for stable equality
            return f"{v:.5f}"
        if isinstance(v, decimal.Decimal):
            q = decimal.Decimal("0.00001")
            return str(v.quantize(q, rounding=decimal.ROUND_HALF_UP))
        if isinstance(v, (bytes, bytearray)):
            return v.hex()
        try:
            if isinstance(v, memoryview):
                return bytes(v).hex()
        except Exception:
            pass
        if isinstance(v, _dt.datetime):
            try:
                # Some drivers return DATE when time is midnight; normalize that
                if v.time() == _dt.time(0, 0, 0):
                    return v.date().isoformat()
                return _to_millis(v)
            except Exception:
                return str(v)
        if isinstance(v, _dt.time):
            try:
                # Drop microseconds or reduce to milliseconds for uniformity
                if v.microsecond:
                    s = time(v.hour, v.minute, v.second).isoformat()
                    ms = v.microsecond // 1000
                    return f"{s}.{ms:03d}"
                return v.isoformat()
            except Exception:
                return str(v)
        if isinstance(v, _dt.date):
            try:
                return v.isoformat()
            except Exception:
                return str(v)
        return str(v)

    return [tuple(norm(x) for x in row) for row in rows]


def host_for_docker() -> str:
    return "host.docker.internal" if os.getenv("IN_DOCKER", "0") == "1" else "localhost"


@pytest.fixture(scope="session")
def oracle_source_engine():
    """Session-scoped Oracle source engine (starts container once)."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    engine = get_connection(
        db_type="oracle",
        db_name="test_source",
        user=username,
        password=password,
        port=ports["oracle"],
        force_refresh=True,
        print_tables=False,
    )
    yield engine
    # Do not auto-cleanup here; final cleanup is explicit in tests or global teardown.


@pytest.fixture(scope="session")
def oracle_dest_engine():
    """Session-scoped Oracle destination engine (starts container once)."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    engine = get_connection(
        db_type="oracle",
        db_name="test_dest_oracle",
        user=username,
        password=password,
        port=ports_dest["oracle"],
        force_refresh=True,
        print_tables=False,
    )
    yield engine
    # Do not auto-cleanup here; final cleanup is explicit in tests or global teardown.
