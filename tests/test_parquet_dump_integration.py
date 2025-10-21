import os
import shutil
import subprocess
from datetime import date, datetime
from dotenv import load_dotenv

import pytest
from sqlalchemy import text
import docker

from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
from utils.database.create_connectorx_uri import create_connectorx_uri
from utils.database.initialize_oracle_client import initialize_oracle_client
from utils.config.get_config_value import get_config_value

# load_dotenv werkt mogelijk niet binnen pytes;
# Stel indien nodig SRC_CONNECTORX_ORACLE_CLIENT_PATH in je user/system environment variabelen in
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


# Use the same explicit host ports as tests/test_direct_transfer_integration.py
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
    """Stop and remove the source/dest containers and volumes created by these tests."""
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
    # Drop if exists and create a table with diverse types, mirroring direct transfer tests
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

    if db_type in ("mysql", "mariadb"):
        for r in rows:
            if r["b"] is True:
                r["b"] = 1
            elif r["b"] is False:
                r["b"] = 0

    if db_type == "mssql":
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


def _fetch_all(conn, table: str):
    rs = conn.execute(
        text(
            f"SELECT id, i32, smi, bigi, s, n18_5, f32, f64, t, u, bin, d, ts, dt_str, b FROM {table} ORDER BY id"
        )
    ).fetchall()
    return [tuple(row) for row in rs]


def _normalize_rows(rows):
    def norm(v):
        import decimal
        import datetime as _dt
        import re

        if v is None:
            return None
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, (int,)):
            return v
        if isinstance(v, float):
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
                if v.time() == _dt.time(0, 0, 0):
                    return v.date().isoformat()
                return v.isoformat()
            except Exception:
                return str(v)
        if isinstance(v, _dt.time):
            try:
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
        # If it's a numeric-looking string, normalize to 5 decimals
        if isinstance(v, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", v):
            try:
                d = decimal.Decimal(v)
                q = decimal.Decimal("0.00001")
                return str(d.quantize(q, rounding=decimal.ROUND_HALF_UP))
            except Exception:
                return v
        return str(v)

    return [tuple(norm(x) for x in row) for row in rows]


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


def _host_for_docker() -> str:
    return "host.docker.internal" if os.getenv("IN_DOCKER", "0") == "1" else "localhost"


def _maybe_init_oracle_client() -> bool:
    # Only initialize if a path is configured; otherwise no-op
    client_path = get_config_value("SRC_CONNECTORX_ORACLE_CLIENT_PATH")
    if not client_path:
        return False
    try:
        initialize_oracle_client("SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=None)
        print("Oracle Instant Client initialized successfully.")
        return True
    except Exception:
        print("Failed to initialize Oracle Instant Client for ConnectorX.")
        return False


initialized_oracle = _maybe_init_oracle_client()


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
    src_schema, _ = _schemas_for(src_db_type)
    _, dst_schema = _schemas_for(dst_db_type)

    outdir = os.path.join(tmp_dir, f"dump_{src_db_type}_to_{dst_db_type}")
    os.makedirs(outdir, exist_ok=True)

    if use_connectorx:
        # Build a ConnectorX URI to read from the source
        host = _host_for_docker()
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
@pytest.mark.parametrize(
    "use_connectorx", [True, False], ids=["connectorx", "sqlalchemy"]
)
def test_parquet_dump_oracle_to_postgres_and_mssql_and_mysql_variants(
    tmp_path, use_connectorx
):
    """
    For both ConnectorX and SQLAlchemy dump modes: launch Oracle once, create sample table and data,
    then export to Parquet and upload into Postgres, MSSQL, MySQL, and MariaDB, validating content.
    """
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    table = "typetest_dump"

    # Clean any leftovers first
    for t in ["oracle", "postgres", "mssql", "mysql", "mariadb"]:
        _cleanup_db_containers(t)

    try:
        # Start Oracle source ONCE
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

        # Prepare destinations
        dest_confs = [
            ("postgres", ports_dest["postgres"]),
            ("mssql", ports_dest["mssql"]),
            ("mysql", ports_dest["mysql"]),
            ("mariadb", ports_dest["mariadb"]),
        ]

        for dst_type, dst_port in dest_confs:
            dst_engine = get_connection(
                db_type=dst_type,
                db_name=f"test_dest_{dst_type}",
                user=username,
                password=password,
                port=dst_port,
                force_refresh=True,
                print_tables=False,
            )

            _two_step_parquet_transfer(
                src_engine,
                "oracle",
                dst_engine,
                dst_type,
                table,
                str(tmp_path),
                use_connectorx=use_connectorx,
                chunk_size=2,
            )

            with src_engine.connect() as sconn, dst_engine.connect() as dconn:
                src_rows = _fetch_all(sconn, table)
                dst_rows = _fetch_all(dconn, table)
            assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)
    finally:
        for t in ["oracle", "postgres", "mssql", "mysql", "mariadb"]:
            _cleanup_db_containers(t)


@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.parametrize(
    "use_connectorx", [True, False], ids=["connectorx", "sqlalchemy"]
)
def test_parquet_dump_all_to_oracle(tmp_path, use_connectorx):
    """
    For both ConnectorX and SQLAlchemy dump modes: transfer from Postgres, MSSQL, MySQL, MariaDB to Oracle.
    """
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

        sources = [
            ("postgres", ports["postgres"]),
            ("mssql", ports["mssql"]),
            ("mysql", ports["mysql"]),
            ("mariadb", ports["mariadb"]),
        ]

        for src_type, src_port in sources:
            table = f"typetest_{src_type}src_dump"
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

            # Create source table + data
            with src_engine.begin() as sconn:
                _create_table_and_data(sconn, src_type, table)

            _two_step_parquet_transfer(
                src_engine,
                src_type,
                dst_oracle_engine,
                "oracle",
                table,
                str(tmp_path),
                use_connectorx=use_connectorx,
                chunk_size=2,
            )

            with src_engine.connect() as sconn, dst_oracle_engine.connect() as dconn:
                src_rows = _fetch_all(sconn, table)
                dst_rows = _fetch_all(dconn, table)
            assert _normalize_rows(src_rows) == _normalize_rows(dst_rows)
    finally:
        for t in ["oracle", "postgres", "mssql", "mysql", "mariadb"]:
            _cleanup_db_containers(t)
