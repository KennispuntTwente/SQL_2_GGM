from pathlib import Path
from sqlalchemy import create_engine, text

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet


def _prepare_source_sqlite(tmp_path: Path):
    src_db = tmp_path / "src.sqlite"
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
    return src_engine


def test_upload_parquet_append_sqlite(tmp_path: Path):
    src_engine = _prepare_source_sqlite(tmp_path)
    out_dir = tmp_path / "parquet"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Dump in small chunks to exercise chunking paths
    download_parquet(src_engine, ["Demotable"], output_dir=str(out_dir), chunk_size=2)

    dst_db = tmp_path / "dst.sqlite"
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

    # Append should keep pre-existing row and add 3
    upload_parquet(
        dst_engine, input_dir=str(out_dir), cleanup=False, write_mode="append"
    )

    with dst_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Demotable")).scalar_one()
    assert count == 4


def test_upload_parquet_truncate_sqlite(tmp_path: Path):
    src_engine = _prepare_source_sqlite(tmp_path)
    out_dir = tmp_path / "parquet2"
    out_dir.mkdir(parents=True, exist_ok=True)

    download_parquet(src_engine, ["Demotable"], output_dir=str(out_dir), chunk_size=2)

    dst_db = tmp_path / "dst2.sqlite"
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

    # Truncate should remove pre-existing rows, then load 3
    upload_parquet(
        dst_engine, input_dir=str(out_dir), cleanup=False, write_mode="truncate"
    )

    with dst_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Demotable")).scalar_one()
    assert count == 3
