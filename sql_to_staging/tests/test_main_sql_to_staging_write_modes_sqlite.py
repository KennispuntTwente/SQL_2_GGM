import subprocess
from pathlib import Path
import os
import sys

from sqlalchemy import create_engine, text


def _run_main_with_ini(cfg_path: Path):
    env = os.environ.copy()
    # Ensure environment doesn't override schema/hosts etc. for sqlite test
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


def test_sqlalchemy_direct_write_mode_append(tmp_path):
    # Prepare source and destination SQLite files
    src_db = tmp_path / "src.db"
    dst_db = tmp_path / "dst.db"

    # Create source table with 3 rows
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

    # Pre-create destination table with a non-conflicting row (id=100)
    dst_engine = create_engine(f"sqlite+pysqlite:///{dst_db}")
    with dst_engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE Demotable (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)"
            )
        )
        conn.execute(
            text("INSERT INTO Demotable (id, name, value) VALUES (100, 'pre', 999)")
        )

    # Write INI with WRITE_MODE=append
    cfg_path = tmp_path / "sql_to_staging_append.ini"
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
WRITE_MODE=append
SRC_TABLES=Demotable
ASK_PASSWORD_IN_CLI=False
SRC_CHUNK_SIZE=1000
""".strip()
    )

    _run_main_with_ini(cfg_path)

    # Expect 4 rows total (existing + 3 new)
    with dst_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Demotable")).scalar_one()
    assert count == 4


def test_sqlalchemy_direct_write_mode_truncate(tmp_path):
    src_db = tmp_path / "src.db"
    dst_db = tmp_path / "dst.db"

    # Source with 3 rows
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

    # Destination pre-filled with 2 rows (to be truncated)
    dst_engine = create_engine(f"sqlite+pysqlite:///{dst_db}")
    with dst_engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE Demotable (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO Demotable (id, name, value) VALUES (100, 'pre1', 999), (101, 'pre2', 998)"
            )
        )

    cfg_path = tmp_path / "sql_to_staging_truncate.ini"
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
WRITE_MODE=truncate
SRC_TABLES=Demotable
ASK_PASSWORD_IN_CLI=False
SRC_CHUNK_SIZE=1000
""".strip()
    )

    _run_main_with_ini(cfg_path)

    # Only the 3 source rows should remain
    with dst_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Demotable")).scalar_one()
    assert count == 3
