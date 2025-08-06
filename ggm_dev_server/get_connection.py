# Dit Python-script legt verbinding met een ontwikkel-database die draait in een Docker-container
# De get_connection legt verbindnding met de container; deze functie start de container indien nodig,
#   en als de container voor de eerste keer wordt gestart, worden ook alle SQL-scripts uitgevoerd uit een 
#   opgegeven map (deze kunnen de database initialiseren met tabellen naar het GGM, bijv.)

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Callable, Dict, Any

import docker
import oracledb
import psycopg2
import pyodbc
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from ggm_dev_server.preprocess_sql import preprocess_sql


# ────────────────────────────────────────────────────────────────────────────────
# Driver‑specific helpers
# ────────────────────────────────────────────────────────────────────────────────
def _connect_postgres(cfg: Dict[str, Any]):
    return psycopg2.connect(**cfg)

def _connect_oracle(cfg: Dict[str, Any]):
    """Connect to the PDB named in cfg['dbname']."""
    oracledb.defaults.fetch_lobs = False
    # Use the dynamic service_name instead of the fixed FREEPDB1
    dsn = f"{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    return oracledb.connect(
        user=cfg["user"],
        password=cfg["password"],
        dsn=dsn
    )

SQL_SERVER_DRIVER = "ODBC Driver 18 for SQL Server"  # Ensure this is installed
def _connect_sqlserver(cfg: Dict[str, Any]):
    conn_str = (
        f"DRIVER={{{SQL_SERVER_DRIVER}}};"
        f"SERVER={cfg['host']},{cfg['port']};"
        f"DATABASE={cfg['dbname']};"
        f"UID={cfg['user']};PWD={cfg['password']};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def _connect_mysql(cfg: Dict[str, Any]):
    """Connect to MySQL."""
    return pymysql.connect(
        host=cfg['host'],
        port=cfg['port'],
        user=cfg['user'],
        password=cfg['password'],
        database=cfg['dbname'],
        autocommit=True
    )


# ────────────────────────────────────────────────────────────────────────────────
# Image settings for the three supported databases
# ────────────────────────────────────────────────────────────────────────────────
SETTINGS = {
    "postgres": dict(
        image="postgres:latest",
        default_port=5432,
        env=lambda user, password, db_name: {
            "POSTGRES_USER": user,
            "POSTGRES_PASSWORD": password,
            "POSTGRES_DB": db_name,
        },
        connector=_connect_postgres,
    ),
    "oracle": dict(
        image="gvenzl/oracle-free:latest-faststart",
        default_port=1521,
        # Pass ORACLE_DATABASE so the container will create a PDB with that name
        env=lambda user, password, db_name: {
            "ORACLE_PASSWORD":    password,
            "ORACLE_DATABASE":    db_name, 
            "APP_USER":           user,
            "APP_USER_PASSWORD":  password,
        },
        connector=_connect_oracle,
    ),
    "sqlserver": dict(
        image="mcr.microsoft.com/mssql/server:2022-latest",
        default_port=1433,
        env=lambda user, password, db_name: {
            "ACCEPT_EULA": "Y",
            "MSSQL_PID": "Developer",
            "SA_PASSWORD": password,
        },
        connector=_connect_sqlserver,
    ),
    "mysql": dict(
        image="mysql:8.0",
        default_port=3306,
        env=lambda user, password, db_name: {
            "MYSQL_ROOT_PASSWORD": password,
            "MYSQL_USER": user,
            "MYSQL_PASSWORD": password,
            "MYSQL_DATABASE": db_name,
        },
        connector=_connect_mysql,
    ),
    "mariadb": dict(             
        image="mariadb:latest",
        default_port=3306,
        env=lambda user, password, db_name: {
            # MariaDB uses the same env vars as MySQL
            "MYSQL_ROOT_PASSWORD": password,
            "MYSQL_USER": user,
            "MYSQL_PASSWORD": password,
            "MYSQL_DATABASE": db_name,
        },
        connector=_connect_mysql,
    ),
}


# ────────────────────────────────────────────────────────────────────────────────
# Docker helpers
# ────────────────────────────────────────────────────────────────────────────────

def _ensure_container_running(
    db_type: str,
    user: str,
    password: str,
    db_name: str,
    port: int,
    container_name: str,
    volume_name: str,
    force_refresh: bool,
) -> tuple[dict, int, bool]:
    """
    Start (or restart) the requested DB container if necessary.

    Returns:
        cfg           – settings entry for the db_type
        port          – effective host port
        was_created   – True if a *new* container was created
    """
    cfg = SETTINGS[db_type]
    client = docker.from_env()

    if force_refresh:
        # blow away everything and start from scratch
        try:
            old = client.containers.get(container_name)
            old.stop(); old.remove()
        except docker.errors.NotFound:
            pass
        try:
            vol = client.volumes.get(volume_name)
            vol.remove(force=True)
        except docker.errors.NotFound:
            pass

    try:
        container = client.containers.get(container_name)
        if container.status != "running":
            container.start()
        was_created = False
    except docker.errors.NotFound:
        print(f"Creating new {db_type} container '{container_name}'…")
        client.containers.run(
            cfg["image"],
            name=container_name,
            environment=cfg["env"](user, password, db_name),
            ports={f"{cfg['default_port']}/tcp": port},
            volumes={volume_name: {"bind": "/var/lib/data", "mode": "rw"}},
            healthcheck={"test": ["CMD", "healthcheck.sh"]} if db_type == "oracle" else None,
            detach=True,
        )
        was_created = True

    return cfg, port, was_created


# ────────────────────────────────────────────────────────────────────────────────
# Generic “wait until DB accepts connections” helper
# ────────────────────────────────────────────────────────────────────────────────

def _wait_for_db_ready(
    connector: Callable,
    connect_cfg: dict,
    max_wait: int,
    print_errors: bool = False,
    force_print_after: Optional[int] = 30,
):
    """Try to connect repeatedly until it succeeds or times out.

    Args:
        connector: A callable that attempts the DB connection using connect_cfg.
        connect_cfg: Connection configuration passed to the connector.
        max_wait: Max time to wait for DB (in seconds).
        print_errors: Whether to print errors during retries.
        force_print_after: Time after which errors are printed regardless of print_errors (in seconds).
    """
    print("Waiting for database to become ready...")
    start_time = time.time()
    deadline = start_time + max_wait
    last_exc = None

    while time.time() < deadline:
        try:
            conn = connector(connect_cfg)
            conn.close()
            print("✅ Database is ready")
            return
        except BaseException as exc:
            last_exc = exc
            root = exc
            while root.__context__ or root.__cause__:
                root = root.__context__ or root.__cause__
            err_msg = f"{type(root).__name__}: {root}"

            now = time.time()
            past_force_threshold = (
                force_print_after is not None and (now - start_time) >= force_print_after
            )
            if print_errors or past_force_threshold:
                sys.stdout.write(
                    f"\rLast connection attempt (errors are normal when DB is not yet ready, but sometimes may indicate a problem): {err_msg}".ljust(120)
                )
                sys.stdout.flush()

            time.sleep(3)

    raise TimeoutError(f"DB not ready after {max_wait}s; last error: {last_exc}")


# ────────────────────────────────────────────────────────────────────────────────
# Optional SQL bootstrap (extra-verbose: totals + filtered list)
# ────────────────────────────────────────────────────────────────────────────────
def _run_sql_scripts(
    sql_folder: Path,
    connector: Callable[[Dict[str, Any]], Any],
    connect_cfg: Dict[str, Any],
    db_type: str,
    suffix_filter: bool = True,
):
    # ── 1. discover files ───────────────────────────────────
    if not sql_folder.exists():
        print(f"⚠️  Folder {sql_folder.resolve()} does not exist – nothing to do.")
        return

    all_sql_files = sorted(sql_folder.glob("*.sql"))
    print(f"📂 Found {len(all_sql_files)} .sql file(s) in {sql_folder.resolve()}")

    db_suffix = f"_{db_type}.sql".lower()
    run_files = [
        f for f in all_sql_files
        if not suffix_filter or f.name.lower().endswith(db_suffix)
    ]

    print(f"🗂️  {len(run_files)} file(s) remain after filtering:")
    for f in run_files:
        print(f"   • {f.name}")
    if not run_files:
        print("⏭️  Nothing to execute after filtering.")
        return

    # ── 2. open one connection and cursor ───────────────────
    with connector(connect_cfg) as conn, conn.cursor() as cur:
        for file in run_files:
            raw_sql = file.read_text(encoding="utf-8")
            sql     = preprocess_sql(raw_sql, db_type)

            try:
                cur.execute(sql)
                conn.commit()
                print(f"✅ {file.name} executed successfully.")
            except Exception as exc:
                conn.rollback()
                print(f"❌ ERROR executing {file.name}: {exc}")
                raise  # or `continue` if you’d rather skip the rest

    print("🏁 SQL boot-strap finished.\n")
    
# ────────────────────────────────────────────────────────────────────────────────
# Public helpers
# ────────────────────────────────────────────────────────────────────────────────
def get_connection(
    db_type: str = "postgres",
    db_name: str = "mydb",
    user: str = "admin",
    password: str = "ChangeMe123!",
    port: int | None = None,
    max_wait_seconds: int | None = None,
    sql_folder: str | Path | None = None, # Map met SQL-scripts die moeten worden uitgevoerd bij de eerste keer starten van de DB
    sql_suffix_filter: bool = True, # Of alleen de SQL-scripts moeten worden uitgevoerd die eindigen op _<db_type>.sql
    print_tables: bool = True,
    *,
    container_name: str | None = None,
    volume_name: str | None = None,
    force_refresh: bool = False,
):
    print()
    db_type = db_type.lower()
    if db_type not in SETTINGS:
        raise ValueError(f"Unsupported db_type: {db_type}")

    cfg = SETTINGS[db_type]
    port_effective = port or cfg["default_port"]
    container_name = container_name or f"{db_type}-docker-db-{port_effective}"
    volume_name = volume_name or f"{container_name}_data"

    if max_wait_seconds is None:
        max_wait_seconds = 600 if db_type == "oracle" else 120

    # start or reuse the container
    cfg, host_port, was_created = _ensure_container_running(
        db_type, user, password, db_name, port_effective,
        container_name, volume_name, force_refresh
    )

    # Prepare configs for master and target DB
    master_cfg = {
        "dbname":   "master",
        "user":      user,
        "password":  password,
        "host":      "localhost",
        "port":      host_port,
    }
    target_cfg = {
        "dbname":    db_name,
        "user":      user,
        "password":  password,
        "host":      "localhost",
        "port":      host_port,
    }

    if db_type == "sqlserver":
        # Wait until SQL Server is up (using master)
        _wait_for_db_ready(cfg["connector"], master_cfg, max_wait_seconds)

        # 2) On first init, auto-create the target DB
        if was_created:
            conn = cfg["connector"](master_cfg)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"IF DB_ID(N'{db_name}') IS NULL CREATE DATABASE [{db_name}]")
            cur.close(); conn.close()

        # 3) Wait until the new DB is ready
        _wait_for_db_ready(cfg["connector"], target_cfg, max_wait_seconds)
    else:
        # For Oracle/Postgres/MySQL/MariaDB, wait normally against the target DB
        _wait_for_db_ready(cfg["connector"], target_cfg, max_wait_seconds)

    # Run initial SQL scripts if provided
    if was_created and sql_folder is not None:
        _run_sql_scripts(
            sql_folder=Path(sql_folder),
            connector=cfg["connector"],
            connect_cfg=target_cfg,
            db_type=db_type, # bv. "postgres"
            suffix_filter=sql_suffix_filter # alleen *_postgres.sql
        )

    # Build SQLAlchemy URL
    if db_type == "oracle":
        url = URL.create(
            drivername="oracle+oracledb",
            username=user,
            password=password,
            host="localhost",
            port=host_port,
            query={"service_name": db_name},
        )
    elif db_type == "sqlserver":
        url = URL.create(
            drivername="mssql+pyodbc",
            username=user,
            password=password,
            host="localhost",
            port=host_port,
            database=db_name,
            query={
                "driver": SQL_SERVER_DRIVER,
                "TrustServerCertificate": "yes"
            },
        )
    elif db_type == "postgres":
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host="localhost",
            port=host_port,
            database=db_name,
        )
    elif db_type in ("mysql", "mariadb"):
        url = URL.create(
            drivername="mysql+pymysql",
            username=user,
            password=password,
            host="localhost",
            port=host_port,
            database=db_name,
        )    
    else:
        raise ValueError(f"Unsupported db_type: {db_type}")

    engine = create_engine(url, echo=False, future=True)

    if print_tables:
        with engine.connect() as conn:
            if db_type == "oracle":
                query = "SELECT table_name FROM user_tables"
            elif db_type == "postgres":
                query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            elif db_type in ("mysql", "mariadb"):
                # MariaDB uses the same information_schema layout as MySQL
                query = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db_name}'"
            elif db_type == "sqlserver":
                query = "SELECT table_name FROM information_schema.tables WHERE table_schema='dbo'"
            else:
                # unlikely to happen since you validated db_type at the top
                raise ValueError(f"Unsupported db_type for printing tables: {db_type!r}")
            result = conn.execute(text(query))
            print("Tables:", [r[0] for r in result.fetchall()])

    return engine

# ────────────────────────────────────────────────────────────────────────────────
# Demo
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Try Postgres
    conn_postgres = get_connection(
        db_type="postgres",
        db_name="ggm",
        user ="sa",
        password="SecureP@ss1!24323482349",
        sql_folder="./ggm_selectie",
        sql_suffix_filter=True,
        force_refresh=True,        
    )

    # # Try MariaDB
    # conn_mariadb = get_connection(
    #     db_type="mariadb",
    #     db_name="ggm",
    #     user="sa",
    #     password="SecureP@ss1!24323482349",
    #     # sql_folder="./ggm_dev_server/sql/selectie",
    #     force_refresh=True,
    #     port=3706,  # Custom port for MariaDB to avoid conflict with MySQL
    # )

    # # Try MySQL
    # conn_mysql = get_connection(
    #     db_type="mysql",
    #     db_name="ggm",
    #     user="sa",
    #     password="SecureP@ss1!24323482349",
    #     # sql_folder="./ggm_dev_server/sql/selectie",
    #     force_refresh=True,
    # )

    # # Try Oracle
    # conn_oracle = get_connection(
    #     db_type="oracle",
    #     db_name="ggm",
    #     user="sa",
    #     password="SecureP@ss1!24323482349",
    #     # sql_folder="./ggm_dev_server/sql/selectie",
    #     force_refresh=True,
    # )

    # # Try SQL Server
    # conn_sqlserver = get_connection(
    #     db_type="sqlserver",
    #     db_name="ggm",
    #     user="sa",
    #     password="SecureP@ss1!24323482349",
    #     # sql_folder="./ggm_dev_server/sql/selectie",
    #     force_refresh=True,
    # )
