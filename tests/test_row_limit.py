from pathlib import Path

import polars as pl
import pytest
from sqlalchemy import create_engine, text

from source_to_staging.functions.direct_transfer import direct_transfer
from source_to_staging.functions.download_parquet import download_parquet


def _mk_sqlite_engine(tmp_path: Path, name: str):
    db = tmp_path / f"{name}.sqlite"
    return create_engine(f"sqlite+pysqlite:///{db}")


@pytest.mark.sa_direct
def test_direct_transfer_row_limit_sqlite(tmp_path: Path):
    src = _mk_sqlite_engine(tmp_path, "src_limit")
    dst = _mk_sqlite_engine(tmp_path, "dst_limit")

    # Prepare source with more rows than we'll allow
    with src.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS items"))
        conn.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)"))
        for i in range(1, 51):
            conn.execute(text("INSERT INTO items (id, name) VALUES (:id, :name)"), {"id": i, "name": f"n{i}"})

    # Copy with a row limit smaller than total
    direct_transfer(
        source_engine=src,
        dest_engine=dst,
        tables=["items"],
        source_schema=None,
        dest_schema=None,
        chunk_size=7,
        lowercase_columns=True,
        write_mode="replace",
        row_limit=10,
    )

    # Verify only limited rows were copied
    with dst.connect() as conn:
        cnt = conn.execute(text("SELECT COUNT(*) FROM items")).scalar_one()
    assert cnt == 10


@pytest.mark.sa_dump
def test_download_parquet_row_limit_sqlalchemy(tmp_path: Path):
    # Build SQLite table with 25 rows, but limit export to 7
    engine = _mk_sqlite_engine(tmp_path, "dump_limit")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS clients"))
        conn.execute(text("CREATE TABLE clients (id INTEGER PRIMARY KEY, name TEXT)"))
        for i in range(1, 26):
            conn.execute(text("INSERT INTO clients (id, name) VALUES (:i, :n)"), {"i": i, "n": f"c{i}"})

    out_dir = tmp_path / "out"
    download_parquet(
        engine,
        ["clients"],
        output_dir=str(out_dir),
        chunk_size=3,
        row_limit=7,
    )

    # Sum rows across all parts; should equal the limit
    total = 0
    for p in sorted(out_dir.glob("*.parquet")):
        df = pl.read_parquet(p)
        total += df.height
        assert set(df.columns) == {"id", "name"}
    assert total == 7
