"""
Oracle → Parquet → Postgres roundtrip (opt-in integration test)

This test provisions ephemeral Oracle and Postgres containers via
`ggm_dev_server.get_connection`, creates a set of tables (including edge types),
exports to Parquet, loads into Postgres, and asserts key values match.

Notes
- Skipped by default. Run with RUN_ORACLE_TESTS=1 to enable.
- Also skips if the `oracledb` package isn't available.
- Uses a tmp directory for Parquet output; no repo pollution.
"""

import datetime
import importlib.util
import json
import os

import pandas as pd
import pytest
from dotenv import load_dotenv

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Float,
    Numeric,
    String,
    Text,
    DateTime,
    Date,
    Time,
    Boolean,
    LargeBinary,
    Enum,
    JSON,
)
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.oracle import TIMESTAMP
from sqlalchemy.sql import text

from ggm_dev_server.get_connection import get_connection
from utils.database.create_connectorx_uri import create_connectorx_uri

# Import heavy, optional deps inside the test to allow import-time skip handling.
# from utils.database.initialize_oracle_client import initialize_oracle_client
# from source_to_staging.functions.download_parquet import download_parquet
# from source_to_staging.functions.upload_parquet import upload_parquet


# Custom TypeDecorator to handle Python time objects on Oracle
class OracleTime(TypeDecorator):
    impl = TIMESTAMP
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.time):
            return datetime.datetime(
                1970, 1, 1, value.hour, value.minute, value.second, value.microsecond
            )
        return value

    def process_result_value(self, value, dialect):
        if isinstance(value, datetime.datetime):
            return value.time()
        return value


# Custom TypeDecorator to serialize JSON to text on Oracle
class OracleJSON(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        # Serialize Python dict/list to JSON string
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # Deserialize JSON string to Python object
        return json.loads(value)


def setup_oracle():
    # 1) Establish a fresh Oracle connection
    engine = get_connection(
        db_type="oracle",
        db_name="ggm",
        user="SA",
        password="SecureP@ss1!24323482349",
        force_refresh=True,
    )

    # 2) Define metadata + tables under schema=SA
    metadata = MetaData(schema="SA")

    # Existing tables
    Table(
        "SZCLIENT",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False),
    )
    Table(
        "WVBEDRAG",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("bedrag", Numeric(10, 2)),
    )
    Table(
        "WVAANB",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("description", String(200)),
    )

    # New table with a variety of SQLAlchemy-supported types
    all_types = Table(
        "ALL_TYPES",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("small_int", SmallInteger),
        Column("big_int", BigInteger),
        Column("float_col", Float),
        Column("numeric_col", Numeric(12, 4)),
        Column("string_col", String(50)),
        Column("text_col", Text),
        Column("datetime_col", DateTime),
        Column("date_col", Date),
        Column("time_col", Time().with_variant(OracleTime(), "oracle")),
        Column("bool_col", Boolean),
        Column("binary_col", LargeBinary),
        # Column("interval_col", Interval),
        Column("enum_col", Enum("A", "B", "C", name="my_enum")),
        Column("json_col", JSON().with_variant(OracleJSON(), "oracle")),
    )

    # 3) Create all tables
    metadata.create_all(engine)

    # 4) Insert sample data
    with engine.begin() as conn:
        # Existing inserts
        conn.execute(text("INSERT INTO SA.SZCLIENT (id, name) VALUES (1, 'Client A')"))
        conn.execute(text("INSERT INTO SA.SZCLIENT (id, name) VALUES (2, 'Client B')"))
        conn.execute(text("INSERT INTO SA.WVBEDRAG  (id, bedrag) VALUES (1, 100.00)"))
        conn.execute(text("INSERT INTO SA.WVBEDRAG  (id, bedrag) VALUES (2, 200.00)"))
        conn.execute(
            text(
                "INSERT INTO SA.WVAANB   (id, description) VALUES (1, 'Description A')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO SA.WVAANB   (id, description) VALUES (2, 'Description B')"
            )
        )

        # New table sample row
        conn.execute(
            all_types.insert().values(
                id=1,
                small_int=42,
                big_int=123456789012345,
                float_col=3.14159,
                numeric_col=2.7182,
                string_col="Sample str",
                text_col="Longer text sample",
                datetime_col=datetime.datetime(2025, 7, 30, 15, 45, 0),
                date_col=datetime.date(2025, 7, 30),
                time_col=datetime.time(15, 45, 0),
                bool_col=True,
                binary_col=b"\xde\xad\xbe\xef",
                # interval_col=datetime.timedelta(days=1, hours=2, minutes=30),
                enum_col="B",
                json_col={"key": "value"},
            )
        )

    print("✓ Oracle ready with SZCLIENT, WVBEDRAG, WVAANB, ALL_TYPES")
    return engine


def compare_and_print(df_ora, df_pg, table_name):
    # Normalize column names to lowercase to avoid casing mismatches
    df_ora = df_ora.copy()
    df_pg = df_pg.copy()
    df_ora.columns = [c.lower() for c in df_ora.columns]
    df_pg.columns = [c.lower() for c in df_pg.columns]

    # Determine all columns present in either
    all_columns = sorted(set(df_ora.columns) | set(df_pg.columns))

    print(f"\n===== Table: {table_name} =====")

    # Outer join on index to align rows; if no natural key, this will align by positional index
    # (you can enhance by merging on a primary key if known)
    df_ora_suf = df_ora.add_suffix("_ora")
    df_pg_suf = df_pg.add_suffix("_pg")
    df_both = pd.concat([df_ora_suf, df_pg_suf], axis=1)

    for col in all_columns:
        col_ora = f"{col}_ora"
        col_pg = f"{col}_pg"
        print(f"\n--- Column: {col} ---")
        # Check existence
        has_ora = col_ora in df_both.columns
        has_pg = col_pg in df_both.columns

        if not has_ora:
            print(f"(⚠️ Kolom '{col}' ontbreekt in Oracle result)")
        if not has_pg:
            print(f"(⚠️ Kolom '{col}' ontbreekt in Postgres result)")

        # Build display frame with what exists
        display_cols = {}
        if has_ora:
            display_cols["Oracle"] = df_both[col_ora]
        if has_pg:
            display_cols["Postgres"] = df_both[col_pg]

        if display_cols:
            display_df = pd.DataFrame(display_cols)
            # If both exist, try to highlight mismatches per row
            if has_ora and has_pg:
                # simple diff indicator
                diffs = display_df["Oracle"] != display_df["Postgres"]
                for idx, is_diff in diffs.items():
                    if is_diff:
                        print(
                            f"Row {idx}: verschil -> Oracle: {display_df.loc[idx, 'Oracle']!r}, "
                            f"Postgres: {display_df.loc[idx, 'Postgres']!r}"
                        )
                # Print the side-by-side for context
                print(display_df.to_string(index=False))
            else:
                # Only one side exists
                print(display_df.to_string(index=False))
        else:
            print("Geen data beschikbaar voor deze kolom aan beide kanten.")
    print("\n" + "=" * 80)


RUN_ORACLE_TESTS = os.getenv("RUN_ORACLE_TESTS", "0").lower() in {"1", "true", "yes", "on"}
ORACLEDB_AVAILABLE = importlib.util.find_spec("oracledb") is not None


@pytest.mark.skipif(not RUN_ORACLE_TESTS, reason="RUN_ORACLE_TESTS not enabled; set to 1 to run this integration test.")
@pytest.mark.skipif(not ORACLEDB_AVAILABLE, reason="oracledb package not installed; required for Oracle integration test.")
def test_oracle_to_postgres_roundtrip(tmp_path):
    """End-to-end Oracle → Parquet → Postgres validation for key types."""
    # Late imports to avoid import-time failures when test is skipped
    from utils.database.initialize_oracle_client import initialize_oracle_client
    from source_to_staging.functions.download_parquet import download_parquet
    from source_to_staging.functions.upload_parquet import upload_parquet

    # Load optional env (e.g., Oracle client path for connectorx/oracledb thick mode)
    load_dotenv("source_to_staging/.env")
    initialize_oracle_client(config_key="SRC_CONNECTORX_ORACLE_CLIENT_PATH")

    # 1) Setup Oracle with test data
    oracle = setup_oracle()

    # 2) Export Oracle tables to Parquet in a temp dir
    oracle_connectorx_uri = create_connectorx_uri(
        driver="oracle",
        username="SA",
        password="SecureP@ss1!24323482349",
        host="localhost",
        port=1521,
        database="ggm",
    )
    out_dir = tmp_path / "parquet"
    download_parquet(
        oracle_connectorx_uri,
        tables=["SZCLIENT", "WVBEDRAG", "WVAANB", "ALL_TYPES"],
        output_dir=str(out_dir),
    )

    # 3) Fresh Postgres and load Parquet
    postgres = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="postgres",
        password="SecureP@ss1!24323482349",
        force_refresh=True,
        print_tables=False,
    )
    upload_parquet(postgres, input_dir=str(out_dir), cleanup=True)

    # 4) Compare key values per table (concise, assertive)
    # a) SZCLIENT
    df_ora = pd.read_sql_query("SELECT id, name FROM SA.SZCLIENT ORDER BY id", con=oracle)
    df_pg = pd.read_sql_query('SELECT id, name FROM public."SZCLIENT" ORDER BY id', con=postgres)
    assert df_ora.shape == df_pg.shape == (2, 2)
    assert df_pg["name"].tolist() == ["Client A", "Client B"]

    # b) WVBEDRAG
    df_ora = pd.read_sql_query("SELECT id, bedrag FROM SA.WVBEDRAG ORDER BY id", con=oracle)
    df_pg = pd.read_sql_query('SELECT id, bedrag FROM public."WVBEDRAG" ORDER BY id', con=postgres)
    assert df_ora.shape == df_pg.shape == (2, 2)
    # Ensure numeric survives the trip (allow coercion via Decimal/float to compare sums)
    assert pytest.approx(float(df_pg["bedrag"].sum())) == 300.00

    # c) WVAANB
    df_ora = pd.read_sql_query("SELECT id, description FROM SA.WVAANB ORDER BY id", con=oracle)
    df_pg = pd.read_sql_query('SELECT id, description FROM public."WVAANB" ORDER BY id', con=postgres)
    assert df_ora.equals(df_pg)

    # d) ALL_TYPES (spot-check representative types)
    df_ora = pd.read_sql_query("SELECT * FROM SA.ALL_TYPES WHERE id = 1", con=oracle)
    df_pg = pd.read_sql_query('SELECT * FROM public."ALL_TYPES" WHERE id = 1', con=postgres)
    assert df_ora.shape[0] == df_pg.shape[0] == 1
    row_pg = df_pg.iloc[0].to_dict()

    # Strings and enums
    assert row_pg["string_col"] == "Sample str"
    assert row_pg["enum_col"] == "B"

    # Numeric types
    assert int(row_pg["small_int"]) == 42
    assert int(row_pg["big_int"]) == 123456789012345
    assert pytest.approx(float(row_pg["float_col"])) == pytest.approx(3.14159, rel=1e-6)
    assert pytest.approx(float(row_pg["numeric_col"])) == pytest.approx(2.7182, rel=1e-6)

    # Date/time types (normalize to strings for robustness)
    assert str(row_pg["date_col"]).startswith("2025-07-30")
    # datetime stored should preserve this timestamp
    assert "2025-07-30" in str(row_pg["datetime_col"]) and "15:45:00" in str(row_pg["datetime_col"]).replace(".000000", "")
    # time_col may roundtrip as a datetime with an epoch date; ensure time-of-day is preserved
    assert "15:45:00" in str(row_pg["time_col"])  # e.g., '1970-01-01 15:45:00' or '15:45:00'

    # JSON and binary
    # json may be a dict already or a JSON string; normalize
    json_val = row_pg["json_col"]
    if isinstance(json_val, str):
        json_val = json.loads(json_val)
    assert json_val == {"key": "value"}

    # binary may come back as bytes or memoryview
    bin_val = row_pg["binary_col"]
    if isinstance(bin_val, memoryview):
        bin_val = bin_val.tobytes()
    elif isinstance(bin_val, str):
        # Common representation from Postgres bytea: '\xdeadbeef'
        s = bin_val.strip()
        if s.startswith("\\x") and len(s) % 2 == 0:
            try:
                bin_val = bytes.fromhex(s[2:])
            except ValueError:
                # Fallback: treat as UTF-8 if not valid hex
                bin_val = s.encode("utf-8")
        else:
            bin_val = s.encode("utf-8")
    assert bin_val == b"\xde\xad\xbe\xef"

    # If you need a full diff during debugging, uncomment:
    # compare_and_print(
    #     pd.read_sql_query("SELECT * FROM SA.ALL_TYPES", con=oracle),
    #     pd.read_sql_query('SELECT * FROM public."ALL_TYPES"', con=postgres),
    #     "ALL_TYPES",
    # )
