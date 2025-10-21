from pathlib import Path

import polars as pl
import pytest
from sqlalchemy import create_engine
from dotenv import load_dotenv

from source_to_staging.functions.download_parquet import download_parquet


load_dotenv("tests/.env")


def _setup_sqlite_db(tmp_path: Path, table_name: str, rows: list[tuple] | None = None):
    """Create a temporary SQLite database file with an optional table and rows.

    Returns:
        engine: SQLAlchemy Engine pointing to the SQLite file
        db_path: Path to the sqlite file
    """
    db_path = tmp_path / "test.sqlite"
    engine = create_engine(f"sqlite+pysqlite:///{db_path}")

    if rows is not None:
        with engine.begin() as conn:
            conn.exec_driver_sql(
                f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, name TEXT)"
            )
            if rows:
                conn.exec_driver_sql(
                    f"INSERT INTO {table_name} (id, name) VALUES (?, ?)",
                    rows,
                )

    return engine, db_path


def _list_parquet_files(out_dir: Path):
    return sorted([p.name for p in out_dir.glob("*.parquet")])


@pytest.mark.sa_dump
def test_download_parquet_chunking_sqlalchemy(tmp_path: Path):
    # Prepare 7 rows and chunk into size 3 -> expect 3 part files: 0,1,2
    rows = [(i, f"name_{i}") for i in range(1, 8)]
    engine, _ = _setup_sqlite_db(tmp_path, table_name="clients", rows=rows)

    out_dir = tmp_path / "out"
    download_parquet(engine, ["clients"], output_dir=str(out_dir), chunk_size=3)

    files = _list_parquet_files(out_dir)
    assert files == [
        "clients_part0000.parquet",
        "clients_part0001.parquet",
        "clients_part0002.parquet",
    ]

    # Verify total row count across files
    total = 0
    for f in files:
        df = pl.read_parquet(out_dir / f)
        total += df.height
        # also check expected columns exist
        assert set(df.columns) == {"id", "name"}
    assert total == 7


@pytest.mark.sa_dump
def test_download_parquet_empty_table_creates_no_files(tmp_path: Path):
    # Create empty table and ensure no parquet files are generated
    engine, _ = _setup_sqlite_db(tmp_path, table_name="empty_table", rows=[])

    out_dir = tmp_path / "out"
    download_parquet(engine, ["empty_table"], output_dir=str(out_dir), chunk_size=5)

    # Directory should exist but contain no parquet files
    assert out_dir.exists() and out_dir.is_dir()
    assert _list_parquet_files(out_dir) == []


@pytest.mark.sa_dump
def test_download_parquet_missing_table_raises(tmp_path: Path):
    # DB without the requested table should raise a RuntimeError during COUNT(*)
    engine, _ = _setup_sqlite_db(tmp_path, table_name="some_table", rows=[(1, "a")])

    out_dir = tmp_path / "out"
    with pytest.raises(RuntimeError) as exc:
        download_parquet(engine, ["does_not_exist"], output_dir=str(out_dir))

    assert "Failed to count rows for does_not_exist" in str(exc.value)
