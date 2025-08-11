# Tijdelijk script om te testen of verschillende datatypes vanuit Oracle goed worden
#   overgebracht naar Postgres

import datetime
import json
import pandas as pd
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
from utils.database.initialize_oracle_client import initialize_oracle_client

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet


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


if __name__ == "__main__":
    # Load .env
    load_dotenv("source_to_staging\\.env")

    # If using ConnectorX with Oracle, ensure Oracle client is initialized
    initialize_oracle_client(config_key="SRC_CONNECTORX_ORACLE_CLIENT_PATH")

    # Setup Oracle database with required tables
    oracle = setup_oracle()

    # Make connectorx uri for Oracle
    oracle_connectorx_uri = create_connectorx_uri(
        driver="oracle",
        username="SA",
        password="SecureP@ss1!24323482349",
        host="localhost",
        port=1521,
        database="ggm",
    )

    # Export to Parquet
    download_parquet(
        oracle_connectorx_uri,
        tables=["SZCLIENT", "WVBEDRAG", "WVAANB", "ALL_TYPES"],
        output_dir="data",
    )

    # Load into Postgres
    postgres = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="postgres",
        password="SecureP@ss1!24323482349",
        force_refresh=True,
    )

    upload_parquet(postgres, input_dir="data", cleanup=True)

    # Now compare the tables in Oracle and Postgres
    tables = ["SZCLIENT", "WVBEDRAG", "WVAANB", "ALL_TYPES"]
    for table in tables:
        # Read from Oracle using direct SELECT
        oracle_query = f"SELECT * FROM SA.{table}"
        df_oracle = pd.read_sql_query(oracle_query, con=oracle)

        # Read from Postgres using direct SELECT with quoted table name
        postgres_query = f'SELECT * FROM public."{table}"'
        df_postgres = pd.read_sql_query(postgres_query, con=postgres)

        compare_and_print(df_oracle, df_postgres, table)
