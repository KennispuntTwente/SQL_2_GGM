import subprocess
from pathlib import Path
import os
import sys

from sqlalchemy import create_engine, text


def _run_main_expect_failure(cfg_path: Path):
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
    # Ensure no environment fallback overrides SRC_TABLES from INI
    env["SRC_TABLES"] = ""
    proc = subprocess.run(
        [sys.executable, "-m", "sql_to_staging.main", "--config", str(cfg_path)],
        cwd=str(Path.cwd()),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc


def test_src_tables_empty_string_raises(tmp_path):
    src_db = tmp_path / "src.db"
    dst_db = tmp_path / "dst.db"

    # Create empty sqlite files to satisfy engine initialization
    create_engine(f"sqlite+pysqlite:///{src_db}")
    create_engine(f"sqlite+pysqlite:///{dst_db}")

    cfg_path = tmp_path / "sql_to_staging_empty_tables.ini"
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
SRC_TABLES=   
ASK_PASSWORD_IN_CLI=False
SRC_CHUNK_SIZE=1000
""".strip()
    )

    proc = _run_main_expect_failure(cfg_path)
    assert proc.returncode != 0
    assert "SRC_TABLES" in proc.stderr
    assert "non-empty" in proc.stderr or "non-empty" in proc.stdout


def test_src_tables_contains_blank_entry_raises(tmp_path):
    src_db = tmp_path / "src.db"
    dst_db = tmp_path / "dst.db"

    # Create a simple table so engines are valid (should fail before use)
    src_engine = create_engine(f"sqlite+pysqlite:///{src_db}")
    with src_engine.begin() as conn:
        conn.execute(text("CREATE TABLE Demotable (id INTEGER PRIMARY KEY, name TEXT)"))

    cfg_path = tmp_path / "sql_to_staging_blank_entry.ini"
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
SRC_TABLES=Demotable,   ,Another
ASK_PASSWORD_IN_CLI=False
SRC_CHUNK_SIZE=1000
""".strip()
    )

    proc = _run_main_expect_failure(cfg_path)
    assert proc.returncode != 0
    assert "SRC_TABLES" in proc.stderr
    assert "non-empty" in proc.stderr or "non-empty" in proc.stdout
