from pathlib import Path

import polars as pl
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from source_to_staging.functions.upload_parquet import upload_parquet


load_dotenv("tests/.env")


def _make_parquet(path: Path, data: dict):
    df = pl.DataFrame(data)
    df.write_parquet(path)


def _count(conn, table: str) -> int:
    return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()


def test_upload_parquet_append_and_cleanup(tmp_path: Path):
    # Arrange: create temp SQLite database file
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path/'db.sqlite'}")

    # Create input parquet files with mixed-case columns to test lowercasing
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    _make_parquet(in_dir / "clients_part0000.parquet", {"ID": [1, 2, 3], "Name": ["a", "b", "c"]})
    _make_parquet(in_dir / "clients_part0001.parquet", {"ID": [4, 5], "Name": ["d", "e"]})
    _make_parquet(in_dir / "orders.parquet", {"ORDER_ID": [10, 11], "AMOUNT": [100.0, 50.5]})

    # Act
    upload_parquet(engine, input_dir=str(in_dir), cleanup=True)

    # Assert: tables exist, counts correct, column names lowercased
    with engine.connect() as conn:
        assert _count(conn, "clients") == 5
        assert _count(conn, "orders") == 2

        # Verify column names are lowercase
        df_clients = pl.read_database("SELECT * FROM clients ORDER BY id", connection=conn)
        assert set(df_clients.columns) == {"id", "name"}
        assert df_clients.height == 5

        df_orders = pl.read_database("SELECT * FROM orders ORDER BY order_id", connection=conn)
        assert set(df_orders.columns) == {"order_id", "amount"}

    # Parquet files should be removed due to cleanup=True
    assert list(in_dir.glob("*.parquet")) == []


def test_upload_parquet_no_cleanup_keeps_files(tmp_path: Path):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path/'db.sqlite'}")
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    files = [
        in_dir / "clients_part0000.parquet",
        in_dir / "clients_part0001.parquet",
    ]
    _make_parquet(files[0], {"ID": [1], "Name": ["x"]})
    _make_parquet(files[1], {"ID": [2], "Name": ["y"]})

    upload_parquet(engine, input_dir=str(in_dir), cleanup=False)

    # Files should remain
    remaining = sorted(p.name for p in in_dir.glob("*.parquet"))
    assert remaining == [f.name for f in files]

    # Data should be appended
    with engine.connect() as conn:
        assert _count(conn, "clients") == 2


def test_upload_parquet_ignores_non_parquet_files(tmp_path: Path):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path/'db.sqlite'}")
    in_dir = tmp_path / "in"
    in_dir.mkdir()

    # Create a valid parquet and a non-parquet file
    _make_parquet(in_dir / "tbl.parquet", {"A": [1, 2]})
    (in_dir / "ignore.txt").write_text("not parquet")

    upload_parquet(engine, input_dir=str(in_dir), cleanup=True)

    with engine.connect() as conn:
        assert _count(conn, "tbl") == 2
    # Only parquet should have been removed
    assert sorted(p.name for p in in_dir.iterdir()) == ["ignore.txt"]
