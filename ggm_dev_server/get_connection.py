# Dit Python-script legt verbinding met een ontwikkel-database die draait in een Docker-container
# De get_connection legt verbindnding met de container; deze functie start de container indien nodig,
#   en als de container voor de eerste keer wordt gestart, worden ook alle SQL-scripts uitgevoerd uit een 
#   opgegeven map (deze kunnen de database initialiseren met tabellen naar het GGM, bijv.)

from __future__ import annotations

import os
import time
import docker
from pathlib import Path
from typing import Callable, Dict, Any

# ------- driver‑specific helpers ------------------------------------------------

def _connect_postgres(cfg: Dict[str, Any]):
    import psycopg2
    return psycopg2.connect(**cfg)

def _connect_oracle(cfg: Dict[str, Any]):
    import cx_Oracle
    dsn = cx_Oracle.makedsn(cfg["host"], cfg["port"], service_name="XEPDB1")
    return cx_Oracle.connect(cfg["user"], cfg["password"], dsn)

def _connect_sqlserver(cfg: Dict[str, Any]):
    import pyodbc
    conn_str = (
        "DRIVER={SQL Server};"  # Use installed driver
        f"SERVER={cfg['host']},{cfg['port']};"
        f"UID={cfg['user']};PWD={cfg['password']};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

# Shared configuration
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
        image="gvenzl/oracle-xe:21.3.0-slim",
        default_port=1521,
        env=lambda user, password, db_name: {
            "ORACLE_PASSWORD": password,
            "APP_USER": user,
            "APP_USER_PASSWORD": password,
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
}

def _ensure_container_running(db_type: str, user: str, password: str, db_name: str, port: int | None) -> tuple[dict, int, bool]:
    cfg = SETTINGS[db_type]
    port = port or cfg["default_port"]
    container_name = f"{db_type}-docker-db"
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
        if container.status != "running":
            container.start()
            print(f"Started existing {db_type} container.")
        else:
            print(f"{db_type} container already running.")
        return cfg, port, False
    except docker.errors.NotFound:
        print(f"Creating new {db_type} container...")
        client.containers.run(
            cfg["image"],
            name=container_name,
            environment=cfg["env"](user, password, db_name),
            ports={f"{cfg['default_port']}/tcp": port},
            volumes={f"{db_type}_data": {"bind": "/var/lib/data", "mode": "rw"}},
            detach=True,
        )
        return cfg, port, True

def _run_sql_scripts(sql_folder: str | Path, connector: Callable, connect_cfg: dict):
    sql_folder = Path(sql_folder).expanduser().resolve()
    if not sql_folder.is_dir():
        raise FileNotFoundError(sql_folder)

    conn = connector(connect_cfg)
    cur = conn.cursor()

    for sql_file in sorted(sql_folder.glob("*.sql")):
        print(f"Running {sql_file.name} …")
        with sql_file.open("r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()
    print("All SQL scripts executed successfully.")

def _wait_for_db_ready(connector: Callable, connect_cfg: dict, max_wait_seconds: int):
    deadline = time.time() + max_wait_seconds
    while time.time() < deadline:
        try:
            conn = connector(connect_cfg)
            conn.close()
            print("DB is ready.")
            return
        except Exception:
            print("Waiting for DB to be ready...")
            time.sleep(3)
    raise TimeoutError("Database did not become ready in time.")

def get_connection(
    db_type: str = "postgres",
    db_name: str = "mydb",
    user: str = "admin",
    password: str = "ChangeMe123!",
    port: int | None = None,
    max_wait_seconds: int = 120,
    sql_folder: str | Path | None = None,
    print_tables: bool = True,
):
    db_type = db_type.lower()
    if db_type not in SETTINGS:
        raise ValueError(f"Unsupported db_type: {db_type}")

    cfg, port, was_created = _ensure_container_running(db_type, user, password, db_name, port)

    connect_cfg = dict(
        dbname=db_name,
        user=user,
        password=password,
        host="localhost",
        port=port,
    )
    _wait_for_db_ready(cfg["connector"], connect_cfg, max_wait_seconds)

    # only run SQL initialization if container was just created and sql_folder was provided
    if was_created and sql_folder is not None:
        _run_sql_scripts(sql_folder, cfg["connector"], connect_cfg)

    if print_tables:
    # Print tables in the database
        conn = cfg["connector"](connect_cfg)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        print("Tables in the database:", [table[0] for table in tables])
        cur.close()
        conn.close()

    return cfg["connector"](connect_cfg)


def run_container_and_execute_sql(
    db_type: str = "postgres",
    db_name: str = "mydb",
    user: str = "admin",
    password: str = "ChangeMe123!",
    port: int | None = None,
    volume_name: str | None = None,
    sql_folder: str | Path = "./sql",
    max_wait_seconds: int = 120,
) -> None:
    db_type = db_type.lower()
    sql_folder = Path(sql_folder).expanduser().resolve()
    if not sql_folder.is_dir():
        raise FileNotFoundError(sql_folder)

    if db_type not in SETTINGS:
        raise ValueError(f"Unsupported db_type: {db_type}")

    cfg, port = _ensure_container_running(db_type, user, password, db_name, port)

    connect_cfg = dict(
        dbname=db_name,
        user=user,
        password=password,
        host="localhost",
        port=port,
    )
    _wait_for_db_ready(cfg["connector"], connect_cfg, max_wait_seconds)

    conn = cfg["connector"](connect_cfg)
    cur = conn.cursor()

    for sql_file in sorted(sql_folder.glob("*.sql")):
        print(f"Running {sql_file.name} …")
        with sql_file.open("r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()
    print("All SQL scripts executed successfully.")

# Demonstration
if __name__ == "__main__":
    conn = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="sa",
        password="SecureP@ss1!24323482349",
        sql_folder="./ggm_db/sql/selectie"
    )
