# Tests for end-to-end roundtrip of data types via Parquet using SQLite backend
# Focuses on preserving values and NULLs through download and upload processes
# This ensures fidelity of various data types including integers, floats, booleans, text, dates, and datetimes

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import polars as pl
import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet


load_dotenv("tests/.env")


def _rows(conn, table: str):
    return conn.execute(text(f"SELECT * FROM {table} ORDER BY 1")).fetchall()


@pytest.mark.sa_dump
def test_end_to_end_roundtrip_values_sqlite(tmp_path: Path):
    """
    Create a SQLite source table with a mix of types and NULLs, dump to Parquet in chunks,
    then upload into a fresh SQLite destination and verify values survived unchanged
    (allowing for SQLite's dynamic typing of booleans/datetimes).
    """
    # Source DB with mixed columns; SQLite stores types dynamically, so we focus on value fidelity
    src_engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'src.sqlite'}")
    with src_engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE fact (
              id INTEGER PRIMARY KEY,
              big_int INTEGER,
              amount REAL,
              flag INTEGER,
              txt TEXT,
              d TEXT,
              dt TEXT
            )
            """
        )
        # Insert rows including NULLs and edge-ish values
        rows = [
            (
                1,
                9_223_372_036_854_775_000,  # near int64 max but safe
                1234.5678,
                1,
                "hello",
                "2024-01-02",
                "2024-01-02 03:04:05",
            ),
            (
                2,
                None,
                -0.0001,
                0,
                None,
                None,
                None,
            ),
            (
                3,
                -9_223_372_036_854_775_000,
                1.5,
                None,
                "",
                "1999-12-31",
                "2000-01-01 00:00:00",
            ),
        ]
        conn.exec_driver_sql(
            "INSERT INTO fact (id, big_int, amount, flag, txt, d, dt) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )

    # Dump to Parquet (in two chunks to exercise chunking)
    out_dir = tmp_path / "parquet"
    download_parquet(src_engine, ["fact"], output_dir=str(out_dir), chunk_size=2)

    # Upload into destination DB
    dst_engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'dst.sqlite'}")
    upload_parquet(dst_engine, input_dir=str(out_dir), cleanup=False)

    # Verify uploaded values match originals
    with dst_engine.connect() as conn:
        got = _rows(conn, "fact")

    # SQLite may store flag as 0/1 integers; this is acceptable
    # Compare row-by-row except float with tolerance
    assert len(got) == 3

    def approx(a: float, b: float, tol: float = 1e-9) -> bool:
        if a is None or b is None:
            return a is b is None
        return abs(a - b) <= tol

    exp = rows
    for (gid, gbig, gamt, gflag, gtxt, gd, gdt), (
        eid,
        ebig,
        eamt,
        eflag,
        etxt,
        ed,
        edt,
    ) in zip(got, exp):
        assert gid == eid
        assert gbig == ebig
        assert approx(gamt, eamt)
        assert (gflag == eflag) or (
            gflag in (0, 1) and eflag in (0, 1) and gflag == eflag
        )
        assert gtxt == etxt
        assert gd == ed
        assert gdt == edt


def test_upload_parquet_preserves_nulls_and_values(tmp_path: Path):
    """
    Build Parquet from a typed Polars DataFrame (including NULLs) and ensure after upload
    the values (and NULL counts) are preserved. Types may be adapted by SQLite, so we
    normalize for comparison where needed.
    """
    # Construct a DataFrame with explicit dtypes and NULLs
    df = pl.DataFrame(
        {
            "i64": pl.Series("i64", [1, None, 3], dtype=pl.Int64),
            "f64": pl.Series("f64", [1.5, None, -2.25], dtype=pl.Float64),
            "bool": pl.Series("bool", [True, None, False], dtype=pl.Boolean),
            "text": pl.Series("text", ["a", None, ""], dtype=pl.Utf8),
            "date": pl.Series(
                "date", [date(2024, 1, 1), None, date(1999, 12, 31)], dtype=pl.Date
            ),
            # Timezone-naive datetime to avoid backend-specific TZ coercions
            "dt": pl.Series(
                "dt",
                [datetime(2024, 1, 1, 12, 0, 0), None, datetime(2000, 1, 1, 0, 0, 0)],
                dtype=pl.Datetime(time_unit="us"),
            ),
        }
    )

    in_dir = tmp_path / "in"
    in_dir.mkdir()
    pq = in_dir / "mixed.parquet"
    df.write_parquet(pq)

    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'db.sqlite'}")
    upload_parquet(engine, input_dir=str(in_dir), cleanup=False)

    # Read back and compare null counts and value equivalence (after normalization)
    with engine.connect() as conn:
        back = pl.read_database(
            "SELECT rowid, * FROM mixed ORDER BY rowid", connection=conn
        )
    # Drop SQLite rowid helper
    back = back.drop("rowid")

    # Column presence (lower-cased) and sizes
    assert set(back.columns) == {"i64", "f64", "bool", "text", "date", "dt"}
    assert back.height == 3

    # NULL counts preserved
    for col in ["i64", "f64", "bool", "text", "date", "dt"]:
        assert back[col].null_count() == df[col].null_count()

    # Normalize and compare values
    # booleans may be stored as 0/1; cast both to Int64 for comparison
    exp_bool = df["bool"].cast(pl.Int64, strict=False)
    got_bool = back["bool"].cast(pl.Int64, strict=False)
    assert got_bool.to_list() == exp_bool.to_list()

    # dates/datetimes likely serialized as text by SQLite; convert expected to string
    exp_date_str = df["date"].dt.strftime("%Y-%m-%d").to_list()
    got_date_str = back["date"].cast(pl.Utf8, strict=False).to_list()
    assert got_date_str == exp_date_str

    exp_dt_str = df["dt"].dt.strftime("%Y-%m-%d %H:%M:%S").to_list()
    got_dt_str = (
        back["dt"].str.slice(0, 19).to_list()
    )  # drop fractional seconds if present
    assert got_dt_str == exp_dt_str

    # numeric and text exact checks (floats with tolerance)
    assert back["i64"].to_list() == df["i64"].to_list()
    exp_f = df["f64"].to_list()
    got_f = back["f64"].to_list()
    for a, b in zip(exp_f, got_f):
        if a is None or b is None:
            assert a is b is None
        else:
            assert abs(a - b) <= 1e-12


@pytest.mark.cx_dump
def test_connectorx_download_then_upload_roundtrip(tmp_path: Path, monkeypatch):
    """
    Simulate ConnectorX arrow_stream batches, write Parquet via download_parquet,
    then upload and verify data values in SQLite. Focus on int/float/bool/text.
    """
    import pyarrow as pa

    def _batch(ids, amts, flags, names):
        return pa.record_batch(
            [
                pa.array(ids, type=pa.int64()),
                pa.array(amts, type=pa.float64()),
                pa.array(flags, type=pa.bool_()),
                pa.array(names, type=pa.string()),
            ],
            names=["id", "amount", "flag", "name"],
        )

    batches = [
        _batch([1, 2], [1.25, -3.5], [True, None], ["a", None]),
        _batch([3], [0.0], [False], [""]),
    ]

    def fake_read_sql(conn, query, *, return_type, batch_size, **kwargs):
        assert return_type == "arrow_stream"
        return batches

    monkeypatch.setattr(
        "source_to_staging.functions.download_parquet.cx.read_sql", fake_read_sql
    )

    uri = "postgresql://user:pass@host/db"
    out_dir = tmp_path / "out"
    download_parquet(uri, ["sales"], output_dir=str(out_dir), chunk_size=10)

    # Upload to a fresh SQLite db
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'cx_roundtrip.sqlite'}")
    upload_parquet(engine, input_dir=str(out_dir), cleanup=False)

    # Validate
    with engine.connect() as conn:
        back = pl.read_database(
            "SELECT id, amount, flag, name FROM sales ORDER BY id", connection=conn
        )

    # Column names are lowercased by upload
    assert back.columns == ["id", "amount", "flag", "name"]
    assert back.height == 3

    # id
    assert back["id"].to_list() == [1, 2, 3]
    # amount (floats) with tolerance
    for got, exp in zip(back["amount"].to_list(), [1.25, -3.5, 0.0]):
        assert (got is None and exp is None) or (abs(got - exp) <= 1e-12)
    # flag may be stored as 0/1
    assert back["flag"].cast(pl.Int64, strict=False).to_list() == [1, None, 0]
    # name strings
    assert back["name"].to_list() == ["a", None, ""]
