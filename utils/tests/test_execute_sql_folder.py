# Tests for execute_sql_folder with SQLite in-memory database
# Focuses on suffix filtering behavior and drop_schema_objects cleanup
# This ensures SQL folder execution honors dialect-specific file suffixes and can reset schema state

from pathlib import Path

from sqlalchemy import create_engine, text

from utils.database.execute_sql_folder import execute_sql_folder, drop_schema_objects


def _tmp_sql_dir(tmp_path: Path) -> Path:
    d = tmp_path / "sql"
    d.mkdir()
    return d


def test_execute_sql_folder_suffix_filter_sqlite(tmp_path):
    folder = _tmp_sql_dir(tmp_path)

    # Generic file (no suffix)
    (folder / "01_generic.sql").write_text("""
    CREATE TABLE t_default(x INTEGER);
    """, encoding="utf-8")

    # SQLite-specific file
    (folder / "02_schema_sqlite.sql").write_text("""
    CREATE TABLE t_sqlite(y INTEGER);
    """, encoding="utf-8")

    eng = create_engine("sqlite:///:memory:")

    # With suffix_filter=True (default), only *_sqlite.sql should run
    execute_sql_folder(eng, folder, suffix_filter=True)

    with eng.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        ).fetchall()
        table_names = [r[0] for r in tables]
        assert "t_sqlite" in table_names
        assert "t_default" not in table_names


def test_execute_sql_folder_no_filter_runs_all(tmp_path):
    folder = _tmp_sql_dir(tmp_path)
    (folder / "01_generic.sql").write_text("CREATE TABLE t_default(x INTEGER);", encoding="utf-8")
    (folder / "02_schema_sqlite.sql").write_text("CREATE TABLE t_sqlite(y INTEGER);", encoding="utf-8")

    eng = create_engine("sqlite:///:memory:")
    execute_sql_folder(eng, folder, suffix_filter=False)

    with eng.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        ).fetchall()
        table_names = [r[0] for r in tables]
        assert {"t_default", "t_sqlite"}.issubset(set(table_names))


def test_drop_schema_objects_sqlite(tmp_path):
    folder = _tmp_sql_dir(tmp_path)
    (folder / "01_generic.sql").write_text("CREATE TABLE t1(x INTEGER);", encoding="utf-8")

    eng = create_engine("sqlite:///:memory:")
    execute_sql_folder(eng, folder, suffix_filter=False)

    # Ensure table exists
    with eng.connect() as conn:
        count_before = conn.execute(
            text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='t1'")
        ).scalar_one()
        assert count_before == 1

    # Drop all objects (sqlite: no schema required)
    drop_schema_objects(eng, schema=None)

    with eng.connect() as conn:
        count_after = conn.execute(
            text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='t1'")
        ).scalar_one()
        assert count_after == 0
