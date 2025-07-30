# Tijdelijk script om te testen of verschillende datatypes vanuit Oracle goed worden
#   overgebracht naar Postgres

from sqlalchemy import (
    MetaData, Table, Column,
    Integer, BigInteger, SmallInteger, Float, Numeric,
    String, Text, DateTime, Date, Time, Boolean,
    LargeBinary, Interval, Enum, JSON
)
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.oracle import TIMESTAMP
from sqlalchemy.sql import text
from ggm_dev_server.get_connection import get_connection
from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
import datetime
import json
import pandas as pd

# Custom TypeDecorator to handle Python time objects on Oracle
class OracleTime(TypeDecorator):
    impl = TIMESTAMP
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.time):
            return datetime.datetime(
                1970, 1, 1,
                value.hour,
                value.minute,
                value.second,
                value.microsecond
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
        force_refresh=True
    )

    # 2) Define metadata + tables under schema=SA
    metadata = MetaData(schema="SA")

    # Existing tables
    Table(
        "SZCLIENT", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False)
    )
    Table(
        "WVBEDRAG", metadata,
        Column("id", Integer, primary_key=True),
        Column("bedrag", Numeric(10,2))
    )
    Table(
        "WVAANB", metadata,
        Column("id", Integer, primary_key=True),
        Column("description", String(200))
    )

    # New table with a variety of SQLAlchemy-supported types
    all_types = Table(
        "ALL_TYPES", metadata,
        Column("id", Integer, primary_key=True),
        Column("small_int", SmallInteger),
        Column("big_int", BigInteger),
        Column("float_col", Float),
        Column("numeric_col", Numeric(12,4)),
        Column("string_col", String(50)),
        Column("text_col", Text),
        Column("datetime_col", DateTime),
        Column("date_col", Date),
        Column(
            "time_col",
            Time().with_variant(OracleTime(), "oracle")
        ),
        Column("bool_col", Boolean),
        Column("binary_col", LargeBinary),
        Column("interval_col", Interval),
        Column("enum_col", Enum("A", "B", "C", name="my_enum")),
        Column(
            "json_col",
            JSON().with_variant(OracleJSON(), "oracle")
        )
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
        conn.execute(text("INSERT INTO SA.WVAANB   (id, description) VALUES (1, 'Description A')"))
        conn.execute(text("INSERT INTO SA.WVAANB   (id, description) VALUES (2, 'Description B')"))

        # New table sample row
        conn.execute(all_types.insert().values(
            id=1,
            small_int=42,
            big_int=123456789012345,
            float_col=3.14159,
            numeric_col=2.7182,
            string_col='Sample str',
            text_col='Longer text sample',
            datetime_col=datetime.datetime(2025,7,30,15,45,0),
            date_col=datetime.date(2025,7,30),
            time_col=datetime.time(15,45,0),
            bool_col=True,
            binary_col=b'\xDE\xAD\xBE\xEF',
            interval_col=datetime.timedelta(days=1, hours=2, minutes=30),
            enum_col='B',
            json_col={"key": "value"}
        ))

    print("✓ Oracle ready with SZCLIENT, WVBEDRAG, WVAANB, ALL_TYPES")
    return engine

def compare_and_print(df_ora, df_pg, table_name):
    # add suffixes so we can align same‑named columns
    df_ora_s = df_ora.add_suffix('_ora')
    df_pg_s  = df_pg.add_suffix('_pg')
    # concat them horizontally
    df_both = pd.concat([df_ora_s, df_pg_s], axis=1)

    print(f"\n===== Table: {table_name} =====")
    for col in df_ora.columns:
        col_ora = f"{col}_ora"
        col_pg  = f"{col}_pg"
        print(f"\n--- Column: {col} ---")
        # print side‑by‑side, without the index
        print(
            df_both[[col_ora, col_pg]]
            .rename(columns={col_ora: 'Oracle', col_pg: 'Postgres'})
            .to_string(index=False)
        )
    print("\n" + "="*80)

if __name__ == '__main__':
    oracle = setup_oracle()

    # Export to Parquet
    download_parquet(
        oracle,
        tables=["SZCLIENT", "WVBEDRAG", "WVAANB", "ALL_TYPES"],
        output_dir="data"
    )

    # Load into Postgres
    postgres = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="postgres",
        password="SecureP@ss1!24323482349",
        force_refresh=True
    )

    upload_parquet(
        postgres,
        input_dir="data",
        cleanup=True
    )

    # --- Begin comparison of table contents ---
    tables = ["SZCLIENT", "WVBEDRAG", "WVAANB", "ALL_TYPES"]
    for table in tables:
        # Read from Oracle using direct SELECT
        oracle_query = f"SELECT * FROM SA.{table}"
        df_oracle = pd.read_sql_query(oracle_query, con=oracle)

        # Read from Postgres using direct SELECT with quoted table name
        postgres_query = f"SELECT * FROM public.\"{table}\""
        df_postgres = pd.read_sql_query(postgres_query, con=postgres)

        compare_and_print(df_oracle, df_postgres, table)

