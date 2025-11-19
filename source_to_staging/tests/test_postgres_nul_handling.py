import pytest
import polars as pl
from sqlalchemy import text
from dotenv import load_dotenv

from dev_sql_server.get_connection import get_connection
from source_to_staging.functions.upload_parquet import upload_parquet
from source_to_staging.functions.direct_transfer import direct_transfer
from tests.integration_utils import (
    ports_dest,
    docker_running,
    slow_tests_enabled,
    cleanup_db_containers,
)

load_dotenv("tests/.env")

@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.postgres
@pytest.mark.skipif(not docker_running(), reason="Docker/DB required")
def test_upload_parquet_sanitizes_nul_postgres(tmp_path):
    """
    Verifies that upload_parquet automatically strips NUL (0x00) characters
    from string columns when uploading to PostgreSQL, preventing ValueError.
    """
    # 1. Create a Parquet file with NUL characters
    # Postgres text fields cannot contain 0x00.
    df = pl.DataFrame({
        "id": [1, 2],
        "text_col": ["normal", "contains\x00nul"],
        "other_col": ["ok", "also\x00bad"]
    })
    
    parquet_dir = tmp_path / "data"
    parquet_dir.mkdir()
    # Table name will be derived from filename: 'nul_test'
    file_path = parquet_dir / "nul_test.parquet"
    df.write_parquet(file_path)
    
    # 2. Ensure clean containers and spin up destination engine like other tests
    cleanup_db_containers("postgres")
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    engine = get_connection(
        db_type="postgres",
        db_name="nul_dst_pg",
        user=username,
        password=password,
        port=ports_dest["postgres"],
        force_refresh=True,
        print_tables=False,
    )

    # 3. Upload
    schema = "test_nul_handling"
    
    try:
        upload_parquet(
            engine=engine,
            schema=schema,
            input_dir=str(parquet_dir),
            cleanup=False,
            write_mode="replace",
        )
        
        # 4. Verify data in DB
        with engine.connect() as conn:
            # Check row 2
            rows = conn.execute(text(f"SELECT text_col, other_col FROM {schema}.nul_test WHERE id = 2")).fetchone()
            assert rows is not None
            text_val, other_val = rows
            
            # NULs should be stripped
            assert text_val == "containsnul", f"Expected 'containsnul', got {text_val!r}"
            assert other_val == "alsobad", f"Expected 'alsobad', got {other_val!r}"
            
    finally:
        # Cleanup schema and associated Docker containers
        try:
            with engine.begin() as conn:
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        except Exception:
            pass

        # Ensure Postgres test containers + volumes are removed like other tests
        try:
            cleanup_db_containers("postgres")
        except Exception:
            pass


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.postgres
@pytest.mark.skipif(not docker_running(), reason="Docker/DB required")
def test_direct_transfer_sanitizes_nul_postgres(tmp_path):
    """
    Verifies that direct_transfer automatically strips NUL (0x00) characters
    from string values when inserting into PostgreSQL.
    Source is SQLite (which allows embedded NULs in TEXT), destination is Postgres.
    """
    # 1) Build SQLite source with NUL bytes in TEXT
    from sqlalchemy import create_engine, text as sqla_text

    src_engine = create_engine("sqlite:///:memory:")
    with src_engine.begin() as conn:
        conn.execute(sqla_text("DROP TABLE IF EXISTS nul_src"))
        conn.execute(
            sqla_text(
                """
                CREATE TABLE nul_src (
                    id INTEGER PRIMARY KEY,
                    text_col TEXT,
                    other_col TEXT
                )
                """
            )
        )
        conn.execute(
            sqla_text(
                "INSERT INTO nul_src (id, text_col, other_col) VALUES (1, :t1, :o1)"
            ),
            {"t1": "normal", "o1": "ok"},
        )
        conn.execute(
            sqla_text(
                "INSERT INTO nul_src (id, text_col, other_col) VALUES (2, :t2, :o2)"
            ),
            {"t2": "contains\x00nul", "o2": "also\x00bad"},
        )

    # 2) Start a clean Postgres destination
    cleanup_db_containers("postgres")
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    dst_engine = get_connection(
        db_type="postgres",
        db_name="nul_dst_pg3",
        user=username,
        password=password,
        port=ports_dest["postgres"],
        force_refresh=True,
        print_tables=False,
    )

    schema = "test_nul_handling_direct"

    try:
        # 3) Transfer from SQLite -> Postgres
        direct_transfer(
            source_engine=src_engine,
            dest_engine=dst_engine,
            tables=["nul_src"],
            source_schema=None,
            dest_schema=schema,
            write_mode="replace",
            chunk_size=10,
            lowercase_columns=True,
        )

        # 4) Verify NULs were stripped on the Postgres side
        with dst_engine.connect() as conn:
            row = conn.execute(
                text(f"SELECT text_col, other_col FROM {schema}.nul_src WHERE id = 2")
            ).fetchone()
            assert row is not None
            text_val, other_val = row
            assert text_val == "containsnul"
            assert other_val == "alsobad"
    finally:
        try:
            with dst_engine.begin() as conn:
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        except Exception:
            pass
        try:
            cleanup_db_containers("postgres")
        except Exception:
            pass


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.postgres
@pytest.mark.skipif(not docker_running(), reason="Docker/DB required")
def test_upload_parquet_without_sanitizing_nul_postgres_raises(tmp_path):
    """Reproduce the original PostgreSQL NUL-byte error with sanitization disabled."""

    df = pl.DataFrame({
        "id": [1, 2],
        "text_col": ["normal", "contains\x00nul"],
    })

    parquet_dir = tmp_path / "data"
    parquet_dir.mkdir()
    file_path = parquet_dir / "nul_test.parquet"
    df.write_parquet(file_path)

    # Fresh destination for this repro as well
    cleanup_db_containers("postgres")
    username = "sa"
    password = "S3cureP@ssw0rd!23243"
    engine = get_connection(
        db_type="postgres",
        db_name="nul_dst_pg2",
        user=username,
        password=password,
        port=ports_dest["postgres"],
        force_refresh=True,
        print_tables=False,
    )
    schema = "test_nul_handling_no_sanitize"

    # Preflight: ensure the destination Postgres is accepting connections to avoid
    # unrelated OperationalError flakes masking the intended NUL-byte reproduction.
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).scalar()
    except Exception as e:
        pytest.skip(f"Postgres not ready/healthy for repro: {e}")

    try:
        # Instead of upload_parquet (which always sanitizes), directly reproduce
        # the NUL-byte error by attempting a raw insert with a NUL in text.
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.execute(text(f"DROP TABLE IF EXISTS {schema}.nul_test"))
            conn.execute(text(f"CREATE TABLE {schema}.nul_test (id INT PRIMARY KEY, text_col TEXT)"))

        with engine.connect() as conn:
            with pytest.raises(
                ValueError,
                match=r"A string literal cannot contain NUL \(0x00\) characters",
            ):
                conn.execute(
                    text(f"INSERT INTO {schema}.nul_test (id, text_col) VALUES (:id, :txt)"),
                    dict(id=2, txt="contains\x00nul"),
                )
    finally:
        try:
            with engine.begin() as conn:
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        except Exception:
            pass

        try:
            cleanup_db_containers("postgres")
        except Exception:
            pass
