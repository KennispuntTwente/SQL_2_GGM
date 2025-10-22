# Dit Python-script legt verbinding met een ontwikkel-database die draait in een Docker-container
# De get_connection legt verbindnding met de container; deze functie start de container indien nodig,
#   en als de container voor de eerste keer wordt gestart, worden ook alle SQL-scripts uitgevoerd uit een
#   opgegeven map (deze kunnen de database initialiseren met tabellen naar het GGM, bijv.)

from __future__ import annotations

import os
import socket
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Any

import docker
from docker import errors as docker_errors
import oracledb
import psycopg2
import pyodbc
import pymysql
import re
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from dev_sql_server.preprocess_sql import preprocess_sql


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
    return oracledb.connect(user=cfg["user"], password=cfg["password"], dsn=dsn)


SQL_SERVER_DRIVER = "ODBC Driver 18 for SQL Server"  # Ensure this is installed


def _connect_mssql(cfg: Dict[str, Any]):
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
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["dbname"],
        autocommit=True,
    )


# ────────────────────────────────────────────────────────────────────────────────
# Image settings for the three supported databases
# ────────────────────────────────────────────────────────────────────────────────
SETTINGS = {
    "postgres": dict(
        image="postgres:latest",
        default_port=5432,  # host port default
        container_port=5432,  # container's internal port
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
        container_port=1521,
        # Pass ORACLE_DATABASE so the container will create a PDB with that name
        env=lambda user, password, db_name: {
            "ORACLE_PASSWORD": password,
            "ORACLE_DATABASE": db_name,
            "APP_USER": user,
            "APP_USER_PASSWORD": password,
        },
        connector=_connect_oracle,
    ),
    "mssql": dict(
        image="mcr.microsoft.com/mssql/server:2022-latest",
        default_port=1433,
        container_port=1433,
        env=lambda user, password, db_name: {
            "ACCEPT_EULA": "Y",
            "MSSQL_PID": "Developer",
            "SA_PASSWORD": password,
        },
        connector=_connect_mssql,
    ),
    "mysql": dict(
        image="mysql:8.0",
        # Use a non-standard host port by default to avoid clashing with MariaDB/local MySQL
        default_port=3307,
        container_port=3306,
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
        # Use a non-standard host port to avoid clashing with any local MariaDB service
        default_port=3308,
        container_port=3306,
        env=lambda user, password, db_name: {
            # Use MariaDB-specific environment variables for initialization
            # See: https://hub.docker.com/_/mariadb
            "MARIADB_ROOT_PASSWORD": password,
            "MARIADB_USER": user,
            "MARIADB_PASSWORD": password,
            "MARIADB_DATABASE": db_name,
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
    # Allow running inside containers by honoring DOCKER_HOST if provided
    # (docker.from_env handles DOCKER_HOST/DOCKER_TLS_VERIFY vars automatically)
    client = docker.from_env()

    if force_refresh:
        # blow away everything and start from scratch
        try:
            old = client.containers.get(container_name)
            old.stop()
            old.remove()
        except docker_errors.NotFound:
            pass
        try:
            vol = client.volumes.get(volume_name)
            vol.remove(force=True)
        except docker_errors.NotFound:
            pass

    try:
        container = client.containers.get(container_name)
        # Ensure port mapping matches requested host port; if not, recreate
        try:
            container.reload()
            bindings = container.attrs.get("HostConfig", {}).get("PortBindings", {})
            cport = cfg.get("container_port", cfg["default_port"])
            key = f"{cport}/tcp"
            bound = bindings.get(key)
            bound_host_port = bound[0]["HostPort"] if bound else None
            if str(port) != str(bound_host_port):
                # Recreate with correct port mapping
                container.stop()
                container.remove()
                raise docker_errors.NotFound("Recreate due to port change")
        except Exception:
            # If attrs are missing or structure differs, continue and rely on start
            pass
        if container.status != "running":
            try:
                container.start()
            except Exception as e:
                # If host port is already allocated by something else, recreate with random port
                if "port is already allocated" in str(e).lower():
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass
                    raise docker_errors.NotFound(
                        "Recreate due to port allocation conflict"
                    ) from e
                raise
        was_created = False
    except docker_errors.NotFound:
        print(f"Creating new {db_type} container '{container_name}'…")
        # Before creating, proactively look for any container already binding the requested host port
        # and shut it down if it looks like one of ours (same image or name pattern), to avoid
        # "port is already allocated" errors across test runs.
        try:
            cport = cfg.get("container_port", cfg["default_port"])
            target = f"{cport}/tcp"
            for c in client.containers.list(all=True):
                try:
                    c.reload()
                    ports = c.attrs.get("HostConfig", {}).get("PortBindings", {}) or {}
                    bindings = ports.get(target) or []
                    host_ports = {b.get("HostPort") for b in bindings if b}
                    if str(port) in host_ports:
                        # Only remove if it's likely one of our dev DB containers
                        name_matches = bool(
                            re.match(
                                r"^(mariadb|mysql|postgres|oracle|mssql)-docker-db-\d+$",
                                c.name or "",
                            )
                        )
                        image_matches = False
                        try:
                            image_tags = c.image.tags or []
                            image_matches = any(
                                t.startswith(cfg["image"]) for t in image_tags
                            ) or (
                                c.image.attrs.get("RepoTags")
                                and cfg["image"] in c.image.attrs.get("RepoTags", [])
                            )
                        except Exception:
                            pass
                        if name_matches or image_matches:
                            try:
                                c.stop()
                            except Exception:
                                pass
                            try:
                                c.remove()
                            except Exception:
                                pass
                except Exception:
                    # ignore inspection issues; continue cleanup best-effort
                    continue
        except Exception:
            # Best-effort cleanup; carry on to creation
            pass

        # Try with requested host port first; if it fails due to allocation, fall back to random port
        def _run_with_port_mapping(host_port_mapping):
            return client.containers.run(
                cfg["image"],
                name=container_name,
                environment=cfg["env"](user, password, db_name),
                ports={
                    f"{cfg.get('container_port', cfg['default_port'])}/tcp": host_port_mapping
                },
                volumes={volume_name: {"bind": "/var/lib/data", "mode": "rw"}},
                healthcheck={"test": ["CMD", "healthcheck.sh"]}
                if db_type == "oracle"
                else None,
                detach=True,
            )

        try:
            container = _run_with_port_mapping(port)
        except Exception as e:
            if "port is already allocated" in str(e).lower():
                # Use random host port
                container = _run_with_port_mapping(None)
            else:
                raise
        was_created = True
    # Determine the effective host port by inspecting the container's port bindings
    try:
        container.reload()
        cport = cfg.get("container_port", cfg["default_port"])
        key = f"{cport}/tcp"
        bindings = container.attrs.get("NetworkSettings", {}).get("Ports", {}) or {}
        bd = bindings.get(key)
        if bd and isinstance(bd, list) and bd:
            port_str = bd[0].get("HostPort")
            if port_str:
                port = int(port_str)
    except Exception:
        pass

    return cfg, port, was_created


# ────────────────────────────────────────────────────────────────────────────────
# Generic “wait until DB accepts connections” helper
# ────────────────────────────────────────────────────────────────────────────────


def _wait_for_db_ready(
    connector: Callable,
    connect_cfg: dict,
    max_wait: int,
    print_errors: bool = False,
    force_print_after: int | None = 30,
):
    """Try to connect repeatedly until it succeeds or times out.

    Args:
        connector: A callable that attempts the DB connection using connect_cfg.
        connect_cfg: Connection configuration passed to the connector.
        max_wait: Max time to wait for DB (in seconds).
        print_errors: Whether to print errors during retries.
        force_print_after: Time after which errors are printed regardless of print_errors (in seconds).
    """
    start_time = time.time()
    deadline = start_time + max_wait
    last_exc = None
    printed_wait_banner = False

    while time.time() < deadline:
        try:
            conn = connector(connect_cfg)
            conn.close()
            if printed_wait_banner:
                # Use carriage return so we overwrite any last retry status line.
                print("\r✅ Database is ready")
            return
        except BaseException as exc:
            last_exc = exc
            root = exc
            while True:
                ctx = getattr(root, "__context__", None)
                cause = getattr(root, "__cause__", None)
                if ctx is None and cause is None:
                    break
                root = ctx or cause
            err_msg = f"{type(root).__name__}: {root}"

            if not printed_wait_banner:
                print("Waiting for database to become ready...")
                printed_wait_banner = True

            now = time.time()
            past_force_threshold = (
                force_print_after is not None
                and (now - start_time) >= force_print_after
            )
            if print_errors or past_force_threshold:
                sys.stdout.write(
                    f"\rFeedback from last connection attempt (sometimes errors are OK when DB is not yet ready): {err_msg}".ljust(
                        120
                    )
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
    schema: str | None = None,
):
    # ── 0. (optional) validate schema name ─────────────────
    if schema is not None:
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", schema):
            raise ValueError(f"Invalid schema name: {schema!r}")

    # ── 1. discover files ───────────────────────────────────
    if not sql_folder.exists():
        print(f"⚠️  Folder {sql_folder.resolve()} does not exist – nothing to do.")
        return

    all_sql_files = sorted(sql_folder.glob("*.sql"))
    print(f"📂 Found {len(all_sql_files)} .sql file(s) in {sql_folder.resolve()}")

    db_suffix = f"_{db_type}.sql".lower()
    run_files = [
        f
        for f in all_sql_files
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
        # ── 2a. ensure/use target schema per backend ────────
        if schema:
            if db_type == "postgres":
                cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
                # Make sure unqualified DDL/DML goes into that schema
                cur.execute(f'SET search_path TO "{schema}", public')

            elif db_type == "mssql":
                # Create schema if needed, and set the user's default schema
                cur.execute(
                    f"IF SCHEMA_ID(N'{schema}') IS NULL "
                    f"EXEC('CREATE SCHEMA [{schema}]')"
                )
                cur.execute(
                    f"ALTER USER [{connect_cfg['user']}] WITH DEFAULT_SCHEMA=[{schema}]"
                )

            elif db_type == "oracle":
                print(
                    "⚠️ Oracle: schemas are users. To CREATE objects in a schema named "
                    f"{schema!r}, connect as that user or qualify objects "
                    f"explicitly (e.g., {schema}.table_name). "
                    "ALTER SESSION SET CURRENT_SCHEMA only affects name resolution, "
                    "not the target of CREATE statements."
                )

            elif db_type in ("mysql", "mariadb"):
                print(
                    "⚠️ MySQL/MariaDB: a SCHEMA == a DATABASE. Use a separate database "
                    f"named {schema!r} and pass it as db_name, or qualify objects."
                )

        for file in run_files:
            raw_sql = file.read_text(encoding="utf-8")
            sql = preprocess_sql(raw_sql, db_type)
            try:
                cur.execute(sql)
                conn.commit()
                print(f"✅ {file.name} executed successfully.")
            except Exception as exc:
                conn.rollback()
                print(f"❌ ERROR executing {file.name}: {exc}")
                raise

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
    sql_folder: str
    | Path
    | None = None,  # Map met SQL-scripts die moeten worden uitgevoerd bij de eerste keer starten van de DB
    sql_suffix_filter: bool = True,  # Of alleen de SQL-scripts moeten worden uitgevoerd die eindigen op _<db_type>.sql
    sql_schema: str
    | None = None,  # Schema waarin de SQL-scripts moeten worden uitgevoerd
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
        if db_type == "oracle":
            max_wait_seconds = 600
        elif db_type in ("mysql", "mariadb"):
            max_wait_seconds = 180
        else:
            max_wait_seconds = 120

    # For engines that support multiple databases inside one server instance,
    # avoid recreating the container on subsequent calls. Instead, drop/recreate
    # the specific database when force_refresh=True. This enables spinning up
    # a source and destination DB within the same container (e.g., MySQL/MariaDB/Postgres).
    supports_multi_db = db_type in {"postgres", "mysql", "mariadb"}
    container_force_refresh = False if supports_multi_db else force_refresh

    # start or reuse the container
    cfg, host_port, was_created = _ensure_container_running(
        db_type,
        user,
        password,
        db_name,
        port_effective,
        container_name,
        volume_name,
        container_force_refresh,
    )

    # Prepare configs for master and target DB
    # When running inside Docker, localhost refers to the container itself.
    # Prefer host.docker.internal; if not resolvable on Linux, fall back to Docker bridge gateway.
    if os.getenv("IN_DOCKER", "0") == "1":
        host_addr = "host.docker.internal"
        try:
            socket.gethostbyname(host_addr)
        except Exception:
            host_addr = os.getenv("HOST_GATEWAY_IP", "172.17.0.1")
    else:
        host_addr = "localhost"

    # Choose appropriate admin DB/user per backend
    if db_type == "postgres":
        master_db = "postgres"
        admin_user = user  # superuser as provided
        admin_password = password
    elif db_type in ("mysql", "mariadb"):
        master_db = "mysql"
        admin_user = "root"  # root is configured via image env
        admin_password = password
    else:
        master_db = "master"
        admin_user = user
        admin_password = password

    master_cfg = {
        "dbname": master_db,
        "user": admin_user,
        "password": admin_password,
        "host": host_addr,
        "port": host_port,
    }
    target_cfg = {
        "dbname": db_name,
        "user": user,
        "password": password,
        "host": host_addr,
        "port": host_port,
    }

    if db_type == "mssql":
        # Wait until SQL Server is up (using master)
        _wait_for_db_ready(cfg["connector"], master_cfg, max_wait_seconds)

        # 2) On first init, auto-create the target DB
        if was_created:
            conn = cfg["connector"](master_cfg)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"IF DB_ID(N'{db_name}') IS NULL CREATE DATABASE [{db_name}]")
            cur.close()
            conn.close()

        # 3) Wait until the new DB is ready
        _wait_for_db_ready(cfg["connector"], target_cfg, max_wait_seconds)
    else:
        # For Oracle wait on target DB; for Postgres/MySQL/MariaDB wait on admin DB first
        if db_type in ("postgres", "mysql", "mariadb"):
            _wait_for_db_ready(cfg["connector"], master_cfg, max_wait_seconds)
        else:
            _wait_for_db_ready(cfg["connector"], target_cfg, max_wait_seconds)

        # Ensure target database exists and is clean if requested (multi-DB servers)
        if db_type in ("postgres", "mysql", "mariadb"):
            # Connect using admin to manage databases
            if db_type == "postgres":
                admin_conn = cfg["connector"](master_cfg)
                try:
                    # Ensure autocommit/isolation for DROP/CREATE DATABASE
                    try:
                        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT  # type: ignore

                        admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore[attr-defined]
                    except Exception:
                        # Fallback to attribute if available
                        try:
                            admin_conn.autocommit = True
                        except Exception:
                            pass
                    with admin_conn.cursor() as cur:
                        if force_refresh and not was_created:
                            cur.execute(
                                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s",
                                (db_name,),
                            )
                            cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
                        # create if missing
                        cur.execute(
                            "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
                        )
                        if cur.fetchone() is None:
                            cur.execute(f'CREATE DATABASE "{db_name}"')
                finally:
                    try:
                        admin_conn.close()
                    except Exception:
                        pass
            else:
                with cfg["connector"](master_cfg) as admin_conn:
                    with admin_conn.cursor() as cur:
                        # MySQL/MariaDB
                        if force_refresh and not was_created:
                            cur.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
                            admin_conn.commit()
                        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
                        # Ensure user has privileges on the target DB
                        # If user doesn't exist, this will fail; however the image creates it on first init.
                        # Granting again is harmless.
                        cur.execute(
                            f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{user}'@'%' "
                        )
                        cur.execute("FLUSH PRIVILEGES")
                        admin_conn.commit()

        # Finally wait for target DB to be ready (connections, privilege propagation)
        _wait_for_db_ready(cfg["connector"], target_cfg, max_wait_seconds)

    # Run initial SQL scripts if provided
    # For single-DB servers (Oracle/MSSQL), run once when the container was created.
    # For multi-DB servers (Postgres/MySQL/MariaDB), also run when the database was
    # explicitly dropped/recreated via force_refresh.
    should_bootstrap_sql = was_created or (
        sql_folder is not None
        and db_type in {"postgres", "mysql", "mariadb"}
        and force_refresh
    )
    if sql_folder is not None and should_bootstrap_sql:
        _run_sql_scripts(
            sql_folder=Path(sql_folder),
            connector=cfg["connector"],
            connect_cfg=target_cfg,
            db_type=db_type,  # bv. "postgres"
            suffix_filter=sql_suffix_filter,  # alleen *_postgres.sql,
            schema=sql_schema,  # uitvoeren in schema sql_schema
        )

    # Build SQLAlchemy URL
    if db_type == "oracle":
        url = URL.create(
            drivername="oracle+oracledb",
            username=user,
            password=password,
            host=host_addr,
            port=host_port,
            query={"service_name": db_name},
        )
    elif db_type == "mssql":
        url = URL.create(
            drivername="mssql+pyodbc",
            username=user,
            password=password,
            host=host_addr,
            port=host_port,
            database=db_name,
            query={"driver": SQL_SERVER_DRIVER, "TrustServerCertificate": "yes"},
        )
    elif db_type == "postgres":
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host=host_addr,
            port=host_port,
            database=db_name,
        )
    elif db_type in ("mysql", "mariadb"):
        url = URL.create(
            drivername="mysql+pymysql",
            username=user,
            password=password,
            host=host_addr,
            port=host_port,
            database=db_name,
        )
    else:
        raise ValueError(f"Unsupported db_type: {db_type}")

    engine = create_engine(url, echo=False, future=True)

    if print_tables:
        with engine.connect() as conn:
            if db_type == "postgres":
                # Als schema is opgegeven: gebruik dat; anders: current_schema() (eerste in search_path)
                if sql_schema:
                    stmt = text("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = :schema AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """).bindparams(schema=sql_schema)
                else:
                    stmt = text("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = current_schema() AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """)

            elif db_type == "mssql":
                # Val terug op dbo als er geen schema is opgegeven
                schema = sql_schema or "dbo"
                stmt = text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = :schema AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """).bindparams(schema=schema)

            elif db_type in ("mysql", "mariadb"):
                # In MySQL/MariaDB == "database". Zonder schema: gebruik de huidige database (DATABASE()).
                if sql_schema:
                    stmt = text("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = :schema
                        ORDER BY table_name
                    """).bindparams(schema=sql_schema)
                else:
                    stmt = text("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = DATABASE()
                        ORDER BY table_name
                    """)

            elif db_type == "oracle":
                # Zonder schema: user_tables (huidige gebruiker). Met schema: filter op eigenaar.
                if sql_schema:
                    stmt = text("""
                        SELECT table_name
                        FROM all_tables
                        WHERE owner = UPPER(:owner)
                        ORDER BY table_name
                    """).bindparams(owner=sql_schema)
                else:
                    stmt = text("""
                        SELECT table_name
                        FROM user_tables
                        ORDER BY table_name
                    """)
            else:
                raise ValueError(
                    f"Unsupported db_type for printing tables: {db_type!r}"
                )

            rows = conn.execute(stmt).fetchall()
            print("Tables:", [r[0] for r in rows])

    return engine


# ────────────────────────────────────────────────────────────────────────────────
# Demo
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Try Postgres
    conn_postgres = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="sa",
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
    #     # sql_folder="./dev_sql_server/sql/selectie",
    #     force_refresh=True,
    #     port=3706,  # Custom port for MariaDB to avoid conflict with MySQL
    # )

    # # Try MySQL
    # conn_mysql = get_connection(
    #     db_type="mysql",
    #     db_name="ggm",
    #     user="sa",
    #     password="SecureP@ss1!24323482349",
    #     # sql_folder="./dev_sql_server/sql/selectie",
    #     force_refresh=True,
    # )

    # # Try Oracle
    # conn_oracle = get_connection(
    #     db_type="oracle",
    #     db_name="ggm",
    #     user="sa",
    #     password="SecureP@ss1!24323482349",
    #     # sql_folder="./dev_sql_server/sql/selectie",
    #     force_refresh=True,
    # )

    # # Try Microsoft SQL Server
    # conn_mssql = get_connection(
    #     db_type="mssql",
    #     db_name="ggm",
    #     user="sa",
    #     password="SecureP@ss1!24323482349",
    #     # sql_folder="./dev_sql_server/sql/selectie",
    #     force_refresh=True,
    # )
