# Tests for sql_to_staging main entry point with SQLite databases
# Focuses on end-to-end execution via subprocess with INI configuration
# This ensures the main module works correctly for fast local testing without Docker

import subprocess
from pathlib import Path
import os
import sys

from sqlalchemy import create_engine, text


def test_main_sql_to_staging_sqlite(tmp_path):
    # Prepare source and destination SQLite files
    src_db = tmp_path / "src.db"
    dst_db = tmp_path / "dst.db"

    # Create a simple source table with a few rows
    src_engine = create_engine(f"sqlite+pysqlite:///{src_db}")
    with src_engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE Demotable (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO Demotable (name, value) VALUES ('a', 1), ('b', 2), ('c', 3)"
            )
        )

    # Write a temporary INI consumed by main.py
    cfg_path = tmp_path / "sql_to_staging.ini"
    cfg_path.write_text(
        f"""
[database-source]
SRC_DRIVER=sqlite
SRC_DB={src_db.as_posix()}

[database-destination]
DST_DRIVER=sqlite
DST_DB={dst_db.as_posix()}

[settings]
TRANSFER_MODE=SQLALCHEMY_DIRECT
SRC_TABLES=Demotable
ASK_PASSWORD_IN_CLI=False
SRC_CHUNK_SIZE=1000
""".strip()
    )

    # Run the main module as a subprocess to exercise CLI + loaders exactly
    # Ensure env vars don't inject incompatible defaults (e.g., DST_SCHEMA)
    env = os.environ.copy()
    env.update(
        {
            "DST_SCHEMA": "",
            "SRC_USERNAME": "",
            "DST_USERNAME": "",
            "SRC_HOST": "",
            "DST_HOST": "",
            "SRC_PORT": "",
            "DST_PORT": "",
            "SRC_ORACLE_CLIENT_PATH": "",
            "DST_ORACLE_CLIENT_PATH": "",
        }
    )

    proc = subprocess.run(
        [sys.executable, "-m", "sql_to_staging.main", "--config", str(cfg_path)],
        cwd=str(Path.cwd()),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"sql_to_staging.main failed: {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    # Verify rows were copied
    dst_engine = create_engine(f"sqlite+pysqlite:///{dst_db}")
    with dst_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Demotable")).scalar_one()
    assert count >= 3
