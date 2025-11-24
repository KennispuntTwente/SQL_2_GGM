# Tests for download_parquet function using ConnectorX with mocked database responses
# Focuses on chunking behavior, empty batches, and schema-qualified table names
# This ensures correct Parquet file generation from ConnectorX data sources

from pathlib import Path

import pyarrow as pa
import polars as pl
import pytest
from dotenv import load_dotenv


from sql_to_staging.functions.download_parquet import download_parquet


load_dotenv("tests/.env")


def _make_batch(start: int, count: int) -> pa.RecordBatch:
    ids = pa.array(list(range(start, start + count)), type=pa.int64())
    names = pa.array([f"name_{i}" for i in range(start, start + count)])
    return pa.record_batch([ids, names], names=["id", "name"])


def _list_parquet_files(out_dir: Path):
    return sorted([p.name for p in out_dir.glob("*.parquet")])


@pytest.mark.cx_dump
def test_download_parquet_connectorx_iterable_batches(tmp_path, monkeypatch):
    # Mock connectorx.read_sql to return an iterable of RecordBatch
    captured = {}

    def fake_read_sql(conn, query, *, return_type, batch_size, **kwargs):
        captured["args"] = (conn, query)
        captured["kwargs"] = {"return_type": return_type, "batch_size": batch_size}
        return [_make_batch(1, 3), _make_batch(4, 3), _make_batch(7, 1)]

    monkeypatch.setattr(
        "sql_to_staging.functions.download_parquet.cx.read_sql", fake_read_sql
    )

    uri = "postgresql://user:pass@host/db"
    out_dir = tmp_path / "out"
    download_parquet(uri, ["clients"], output_dir=str(out_dir), chunk_size=3)

    files = _list_parquet_files(out_dir)
    assert files == [
        "clients_part0000.parquet",
        "clients_part0001.parquet",
        "clients_part0002.parquet",
    ]

    total = sum(pl.read_parquet(out_dir / f).height for f in files)
    assert total == 7

    # Ensure we requested arrow_stream with the same batch size as chunk_size
    assert captured["kwargs"]["return_type"] == "arrow_stream"
    assert captured["kwargs"]["batch_size"] == 3


@pytest.mark.cx_dump
def test_download_parquet_connectorx_recordbatchreader(tmp_path, monkeypatch):
    # Mock connectorx.read_sql to return an object with .read_next_batch()
    class FakeReader:
        def __init__(self, batches):
            self._it = iter(batches)

        def read_next_batch(self):
            try:
                return next(self._it)
            except StopIteration:
                return None

    empty_batch = pa.record_batch(
        [pa.array([], type=pa.int64()), pa.array([], type=pa.string())],
        names=["id", "name"],
    )

    def fake_read_sql(conn, query, *, return_type, batch_size, **kwargs):
        return FakeReader([_make_batch(1, 2), empty_batch, _make_batch(3, 1)])

    monkeypatch.setattr(
        "sql_to_staging.functions.download_parquet.cx.read_sql", fake_read_sql
    )

    uri = "oracle://ignored"
    out_dir = tmp_path / "out"
    download_parquet(uri, ["tbl"], output_dir=str(out_dir), chunk_size=5)

    files = _list_parquet_files(out_dir)
    # Should skip empty batch and produce two parts
    assert files == ["tbl_part0000.parquet", "tbl_part0001.parquet"]
    total = sum(pl.read_parquet(out_dir / f).height for f in files)
    assert total == 3


@pytest.mark.cx_dump
def test_download_parquet_connectorx_empty_yields_no_files(tmp_path, monkeypatch):
    # When no batches are produced, ensure no files are written
    def fake_read_sql(conn, query, *, return_type, batch_size, **kwargs):
        return []

    monkeypatch.setattr(
        "sql_to_staging.functions.download_parquet.cx.read_sql", fake_read_sql
    )

    uri = "postgresql://user:pass@host/db"
    out_dir = tmp_path / "out"
    download_parquet(uri, ["any_table"], output_dir=str(out_dir), chunk_size=10)

    assert out_dir.exists() and out_dir.is_dir()
    assert _list_parquet_files(out_dir) == []


@pytest.mark.cx_dump
def test_download_parquet_connectorx_schema_qualification(tmp_path, monkeypatch):
    # Ensure the query passed to ConnectorX includes the provided schema
    captured = {}

    def fake_read_sql(conn, query, *, return_type, batch_size, **kwargs):
        captured["conn"] = conn
        captured["query"] = query
        captured["return_type"] = return_type
        captured["batch_size"] = batch_size
        # Return a single small batch so one file is written
        return [_make_batch(10, 2)]

    monkeypatch.setattr(
        "sql_to_staging.functions.download_parquet.cx.read_sql", fake_read_sql
    )

    uri = "postgresql://user:pass@host/db"
    out_dir = tmp_path / "out"
    download_parquet(
        uri, ["tbl"], output_dir=str(out_dir), chunk_size=100, schema="myschema"
    )

    # Verify schema-qualified query was constructed
    assert captured["query"].strip() == "SELECT * FROM myschema.tbl"
    assert captured["return_type"] == "arrow_stream"
    assert captured["batch_size"] == 100

    # And a single parquet file was written
    files = _list_parquet_files(out_dir)
    assert files == ["tbl_part0000.parquet"]
    df = pl.read_parquet(out_dir / files[0])
    assert df.height == 2 and set(df.columns) == {"id", "name"}


@pytest.mark.cx_dump
def test_download_parquet_connectorx_row_limit_with_driver_suffix_postgres(
    tmp_path, monkeypatch
):
    # Ensure URI with driver suffix (postgresql+psycopg2) applies LIMIT correctly
    captured = {}

    def fake_read_sql(conn, query, *, return_type, batch_size, **kwargs):
        captured["query"] = query
        # Return one small batch
        return [_make_batch(1, 2)]

    monkeypatch.setattr(
        "sql_to_staging.functions.download_parquet.cx.read_sql", fake_read_sql
    )

    uri = "postgresql+psycopg2://user:pass@host/db"
    out_dir = tmp_path / "out"
    download_parquet(
        uri,
        ["clients"],
        output_dir=str(out_dir),
        chunk_size=10,
        schema="myschema",
        row_limit=5,
    )

    q = captured["query"].strip().lower()
    # Expect LIMIT clause and proper FROM target retained
    assert q.endswith("limit 5")
    assert "from" in q and "myschema" in q and "clients" in q


@pytest.mark.cx_dump
def test_download_parquet_connectorx_row_limit_with_driver_suffix_mssql(
    tmp_path, monkeypatch
):
    # Ensure URI with driver suffix (mssql+pyodbc) applies TOP correctly
    captured = {}

    def fake_read_sql(conn, query, *, return_type, batch_size, **kwargs):
        captured["query"] = query
        return [_make_batch(1, 1)]

    monkeypatch.setattr(
        "sql_to_staging.functions.download_parquet.cx.read_sql", fake_read_sql
    )

    uri = "mssql+pyodbc://user:pass@host/db"
    out_dir = tmp_path / "out"
    download_parquet(
        uri,
        ["orders"],
        output_dir=str(out_dir),
        chunk_size=10,
        schema="dbo",
        row_limit=5,
    )

    q = captured["query"].strip().lower()
    # Expect TOP syntax at the start and proper target
    assert q.startswith("select top (5) * from")
    assert "dbo" in q and "orders" in q
