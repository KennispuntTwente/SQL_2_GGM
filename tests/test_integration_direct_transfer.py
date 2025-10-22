# Tests source_to_staging direct_transfer integration; Oracle -> all; all -> Oracle; Postgres -> MSSQL
# Focuses on correct transfer of various data types between different types of SQL databases
# This ensures end-to-end functionality of direct_transfer with type fidelity

import os
import shutil
import subprocess
from datetime import date, datetime, time

import pytest
from sqlalchemy import text
import docker
from dotenv import load_dotenv
from utils.database.initialize_oracle_client import try_init_oracle_client

from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.direct_transfer import direct_transfer


load_dotenv("tests/.env")
initialized_oracle = try_init_oracle_client()


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


# Use the same explicit host ports as tests/test_source_to_staging.py to avoid clashes.
# We'll use the "ports" mapping for source DBs and the "ports_dest" mapping for destination DBs.
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


def _cleanup_db_containers(db_type: str):
    """Stop and remove the source/dest containers and volumes created by this test."""
    client = docker.from_env()
    names = [
        f"{db_type}-docker-db-{ports[db_type]}",
        f"{db_type}-docker-db-{ports_dest[db_type]}",
    ]
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
        # remove volume as well
        vol_name = f"{name}_data"
        try:
            v = client.volumes.get(vol_name)
            v.remove(force=True)
        except Exception:
            pass


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
        conn.execute(
            text(f"IF OBJECT_ID(N'{table}', N'U') IS NOT NULL DROP TABLE {table}")
        )
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
        # Oracle: use NUMBER types and DATE/TIMESTAMP
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
            # diverse date string formats for text passthrough
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
            u="βeta-Δ",  # greek chars
            bin=b"",
            d=date(1999, 12, 31),
            ts=datetime(2000, 1, 1, 0, 0, 0),
            dt_str="31/12/1999",  # dd/mm/yyyy
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
        f"INSERT INTO {table} (id, i32, s, n18_5, d, ts, dt_str, b) "
        f"VALUES (:id, :i32, :s, :n18_5, :d, :ts, :dt_str, :b)"
    )
    for r in rows:
        conn.execute(ins, r)


def _fetch_all(conn, db_type: str, table: str):
    # Normalize selection across DBs; sort by id
    rs = conn.execute(
        text(
            f"SELECT id, i32, smi, bigi, s, n18_5, f32, f64, t, u, bin, d, ts, dt_str, b FROM {table} ORDER BY id"
        )
    ).fetchall()
    return [tuple(row) for row in rs]


def _normalize_rows(rows):
    def norm(v):
        import decimal

        if v is None:
            return None
        if isinstance(v, bool):
            # Normalize booleans to 0/1 for cross‑DB consistency
            return 1 if v else 0
        if isinstance(v, (int,)):
            return v
        if isinstance(v, float):
            return round(v, 5)
        if isinstance(v, decimal.Decimal):
            # Normalize to string with up to 5 decimals to compare reliably across drivers
            q = decimal.Decimal("0.00001")
            return str(v.quantize(q, rounding=decimal.ROUND_HALF_UP))
        # Binary may come back as bytes or memoryview depending on driver
        if isinstance(v, (bytes, bytearray)):
            return v.hex()
        try:
            # some drivers return memoryview
            if isinstance(v, memoryview):
                return bytes(v).hex()
        except Exception:
            pass
        # Dates/datetimes: check concrete types instead of hasattr to avoid false positives
        import datetime as _dt

        if isinstance(v, _dt.datetime):
            # If midnight, normalize to date string to match drivers returning DATE
            try:
                if v.time() == _dt.time(0, 0, 0):
                    return v.date().isoformat()
                return v.isoformat()
            except Exception:
                return str(v)
        if isinstance(v, _dt.time):
            try:
                # Normalize to ISO, drop trailing microseconds if zero for consistency
                iso = v.isoformat()
                if iso.endswith(".000000"):
                    iso = iso[:-7]
                return iso
            except Exception:
                return str(v)
        if isinstance(v, _dt.date):
            try:
                return v.isoformat()
            except Exception:
                return str(v)
        return str(v)

    return [tuple(norm(x) for x in row) for row in rows]


@pytest.mark.slow
@pytest.mark.sa_direct
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not initialized_oracle,
    reason="Oracle Instant Client not initialized; required for Oracle tests.",
)
def test_direct_transfer_oracle_to_all():
    """
    Launch Oracle once, create sample table and data there, then transfer to Postgres
    and MSSQL in sequence, validating roundtrip content each time.
    """
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = "typetest"

    # Clean any leftovers first
    _cleanup_db_containers("oracle")
    _cleanup_db_containers("postgres")
    _cleanup_db_containers("mssql")
    _cleanup_db_containers("mysql")
    _cleanup_db_containers("mariadb")

    try:
        # 1) Start Oracle source ONCE
        src_engine = get_connection(
            db_type="oracle",
            db_name="test_source",
            user=username,
            password=password,
            port=ports["oracle"],
            force_refresh=True,
            print_tables=False,
        )

        # Create source table + data (in Oracle)
        with src_engine.begin() as sconn:
            _create_table_and_data(sconn, "oracle", table)

        # 2) Transfer Oracle -> Postgres
        dst_pg_engine = get_connection(
            db_type="postgres",
            db_name="test_dest_pg",
            user=username,
            password=password,
            port=ports_dest["postgres"],
            force_refresh=True,
            print_tables=False,
        )

        src_schema, _ = _schemas_for("oracle")
        _, dst_schema_pg = _schemas_for("postgres")

        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_pg_engine,
            tables=[table],
            source_schema=src_schema,
            dest_schema=dst_schema_pg,
            chunk_size=2,
            lowercase_columns=True,
            write_mode="replace",
        )

        with src_engine.connect() as sconn, dst_pg_engine.connect() as dconn:
            src_rows = _fetch_all(sconn, "oracle", table)
            dst_rows = _fetch_all(dconn, "postgres", table)
        assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)

        # 3) Transfer Oracle -> MSSQL (reusing the same Oracle source)
        dst_ms_engine = get_connection(
            db_type="mssql",
            db_name="test_dest_ms",
            user=username,
            password=password,
            port=ports_dest["mssql"],
            force_refresh=True,
            print_tables=False,
        )
        _, dst_schema_ms = _schemas_for("mssql")

        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_ms_engine,
            tables=[table],
            source_schema=src_schema,
            dest_schema=dst_schema_ms,
            chunk_size=2,
            lowercase_columns=True,
            write_mode="replace",
        )

        with src_engine.connect() as sconn, dst_ms_engine.connect() as dconn:
            src_rows = _fetch_all(sconn, "oracle", table)
            dst_rows = _fetch_all(dconn, "mssql", table)
        assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)

        # 4) Transfer Oracle -> MySQL
        dst_my_engine = get_connection(
            db_type="mysql",
            db_name="test_dest_my",
            user=username,
            password=password,
            port=ports_dest["mysql"],
            force_refresh=True,
            print_tables=False,
        )
        _, dst_schema_my = _schemas_for("mysql")
        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_my_engine,
            tables=[table],
            source_schema=src_schema,
            dest_schema=dst_schema_my,
            chunk_size=2,
            lowercase_columns=True,
            write_mode="replace",
        )
        with src_engine.connect() as sconn, dst_my_engine.connect() as dconn:
            src_rows = _fetch_all(sconn, "oracle", table)
            dst_rows = _fetch_all(dconn, "mysql", table)
        assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)

        # 5) Transfer Oracle -> MariaDB
        dst_maria_engine = get_connection(
            db_type="mariadb",
            db_name="test_dest_maria",
            user=username,
            password=password,
            port=ports_dest["mariadb"],
            force_refresh=True,
            print_tables=False,
        )
        _, dst_schema_maria = _schemas_for("mariadb")
        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_maria_engine,
            tables=[table],
            source_schema=src_schema,
            dest_schema=dst_schema_maria,
            chunk_size=2,
            lowercase_columns=True,
            write_mode="replace",
        )
        with src_engine.connect() as sconn, dst_maria_engine.connect() as dconn:
            src_rows = _fetch_all(sconn, "oracle", table)
            dst_rows = _fetch_all(dconn, "mariadb", table)
        assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)
    finally:
        # Clean all involved containers/volumes after the test
        _cleanup_db_containers("oracle")
        _cleanup_db_containers("postgres")
    _cleanup_db_containers("mssql")
    _cleanup_db_containers("mysql")
    _cleanup_db_containers("mariadb")


@pytest.mark.slow
@pytest.mark.sa_direct
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_direct_transfer_postgres_to_mssql():
    """Transfer from Postgres (source) to MSSQL (destination) and validate contents."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = "typetest"

    # Ensure a clean slate before starting
    _cleanup_db_containers("postgres")
    _cleanup_db_containers("mssql")

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
            _create_table_and_data(sconn, "postgres", table)

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

        src_schema, _ = _schemas_for("postgres")
        _, dst_schema = _schemas_for("mssql")

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
            src_rows = _fetch_all(sconn, "postgres", table)
            dst_rows = _fetch_all(dconn, "mssql", table)

        assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)
    finally:
        # Always clean up containers/volumes after test
        _cleanup_db_containers("postgres")
        _cleanup_db_containers("mssql")


@pytest.mark.slow
@pytest.mark.sa_direct
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not initialized_oracle,
    reason="Oracle Instant Client not initialized; required for Oracle tests.",
)
def test_direct_transfer_all_to_oracle():
    """Transfer from Postgres, MSSQL, MySQL, MariaDB to Oracle and validate contents."""
    username = "sa"
    password = "S3cureP@ssw0rd!23243"

    # Ensure a clean slate before starting
    for t in ["oracle", "postgres", "mssql", "mysql", "mariadb"]:
        _cleanup_db_containers(t)

    try:
        # Start Oracle destination ONCE
        dst_oracle_engine = get_connection(
            db_type="oracle",
            db_name="test_dest_oracle",
            user=username,
            password=password,
            port=ports_dest["oracle"],
            force_refresh=True,
            print_tables=False,
        )
        _, dst_schema_oracle = _schemas_for("oracle")

        sources = [
            ("postgres", ports["postgres"]),
            ("mssql", ports["mssql"]),
            ("mysql", ports["mysql"]),
            ("mariadb", ports["mariadb"]),
        ]

        for src_type, src_port in sources:
            table = f"typetest_{src_type}src"
            # Spin up source
            src_engine = get_connection(
                db_type=src_type,
                db_name=f"test_source_{src_type}",
                user=username,
                password=password,
                port=src_port,
                force_refresh=True,
                print_tables=False,
            )
            src_schema, _ = _schemas_for(src_type)

            # Create source table + data
            with src_engine.begin() as sconn:
                _create_table_and_data(sconn, src_type, table)

            # Transfer to Oracle
            direct_transfer(
                source_engine=src_engine,
                dest_engine=dst_oracle_engine,
                tables=[table],
                source_schema=src_schema,
                dest_schema=dst_schema_oracle,
                chunk_size=2,
                lowercase_columns=True,
                write_mode="replace",
            )

            # Compare
            with src_engine.connect() as sconn, dst_oracle_engine.connect() as dconn:
                src_rows = _fetch_all(sconn, src_type, table)
                dst_rows = _fetch_all(dconn, "oracle", table)
            assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)
    finally:
        for t in ["oracle", "postgres", "mssql", "mysql", "mariadb"]:
            _cleanup_db_containers(t)
