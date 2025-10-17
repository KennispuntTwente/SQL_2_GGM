import os
from collections import defaultdict
from pathlib import Path
import re

import polars as pl
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.schema import CreateSchema


def _parse_parquet_base_name(filename: str) -> str:
    """
    Derive the logical table base name from a parquet filename.

    Rules:
    - Accept chunked files like "table_part0001.parquet" and return "table".
    - If the stem doesn't end with "_part<digits>", return the stem.
    - Do not strip substrings "_part" that appear in the middle of the name
      (e.g., "user_partitions.parquet" stays "user_partitions").
    """
    stem = Path(filename).stem
    m = re.match(r"^(?P<base>.+)_part\d+$", stem)
    return m.group("base") if m else stem


def group_parquet_files(input_dir: str) -> dict[str, list[str]]:
    """
    Scan input_dir and group parquet files by their logical table base name.
    Returns a mapping {base_table_name: [sorted_filenames]}.
    Filenames are returned without directory prefixes.
    """
    grouped: dict[str, list[str]] = defaultdict(list)
    for fname in os.listdir(input_dir):
        path = Path(input_dir, fname)
        if fname.lower().endswith(".parquet") and path.is_file():
            base = _parse_parquet_base_name(fname)
            grouped[base].append(fname)
    # ensure deterministic order for stable loads and tests
    for k in list(grouped.keys()):
        grouped[k].sort()
    return grouped


def upload_parquet(engine, schema=None, input_dir="data", cleanup=True):
    """
    Uploads (possibly chunked) Parquet files into destination DB.
    Ensures the target database and schema exist before loading.
    """
    dialect = engine.dialect.name.lower()

    # 1) Determine and create target database if needed
    db_name = engine.url.database
    if db_name:
        if dialect == "postgresql":
            # connect to 'postgres' admin DB and run CREATE DATABASE in autocommit
            admin_url = engine.url.set(database="postgres")
            admin_eng = create_engine(admin_url)
            try:
                with admin_eng.connect() as conn:
                    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
                    exists = conn.execute(
                        text("SELECT 1 FROM pg_database WHERE datname = :db"),
                        {"db": db_name},
                    ).scalar()
                    if not exists:
                        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            finally:
                admin_eng.dispose()

        elif dialect in ("mssql", "sql server"):
            # connect to 'master' admin DB and run CREATE DATABASE outside explicit txn
            admin_url = engine.url.set(database="master")
            admin_eng = create_engine(admin_url)
            try:
                with admin_eng.connect() as conn:
                    conn.execute(
                        text(f"""
                        IF DB_ID(N'{db_name}') IS NULL
                        BEGIN
                            CREATE DATABASE [{db_name}];
                        END
                    """)
                    )
            finally:
                admin_eng.dispose()

    # 2) Ensure the schema exists
    if schema:
        with engine.begin() as conn:
            if dialect == "postgresql":
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            elif dialect in ("mssql", "sql server"):
                conn.execute(
                    text(f"""
                    IF SCHEMA_ID(N'{schema}') IS NULL
                    BEGIN
                        EXEC(N'CREATE SCHEMA {schema}');
                    END
                """)
                )
            elif dialect == "oracle":
                pass
            elif dialect in ("mysql", "mariadb"):
                # MySQL doesn't support schemas other than databases
                pass
            else:
                try:
                    conn.execute(CreateSchema(schema))
                except ProgrammingError as e:
                    if "already exists" not in str(e).lower():
                        raise

    # 3) Group Parquet files by table base name (robust to names containing "_part")
    grouped = group_parquet_files(input_dir)

    # 4) Write each group into its table
    for table_name, files in grouped.items():
        full_table = f"{schema}.{table_name}" if schema else table_name
        print(f"📦 Uploading {len(files)} part(s) to table {full_table}")

        for idx, fname in enumerate(files):
            path = os.path.join(input_dir, fname)
            print(f"🔹 Processing {path}")
            df = pl.read_parquet(path)
            df = df.rename({col: col.lower() for col in df.columns})
            df.write_database(
                table_name=full_table,
                connection=engine,
                if_table_exists="replace" if idx == 0 else "append",
                engine="sqlalchemy",
            )

        print(f"✅ Loaded: {table_name}")

        # 5) Cleanup parquet files
        if cleanup:
            for fname in files:
                os.remove(os.path.join(input_dir, fname))
            print(f"🗑️ Cleanup completed for {table_name}")
