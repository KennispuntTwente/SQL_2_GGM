import os
import logging
from collections import defaultdict
from pathlib import Path
import re

import polars as pl
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.schema import CreateSchema

logger = logging.getLogger("source_to_staging.upload_parquet")


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
        logger.info("📦 Uploading %s part(s) to table %s", len(files), full_table)

        for idx, fname in enumerate(files):
            path = os.path.join(input_dir, fname)
            logger.info("🔹 Processing %s", path)
            df = pl.read_parquet(path)
            df = df.rename({col: col.lower() for col in df.columns})
            # For Oracle, guide type creation for floats to avoid generic FLOAT precision issues
            engine_options = None
            if dialect == "oracle":
                try:
                    from sqlalchemy.dialects.oracle import (
                        BINARY_FLOAT as ORA_BINARY_FLOAT,
                        BINARY_DOUBLE as ORA_BINARY_DOUBLE,
                        NUMBER as ORA_NUMBER,
                        TIMESTAMP as ORA_TIMESTAMP,
                    )
                except Exception:
                    ORA_BINARY_FLOAT = None  # type: ignore
                    ORA_BINARY_DOUBLE = None  # type: ignore
                    ORA_NUMBER = None  # type: ignore
                    ORA_TIMESTAMP = None  # type: ignore

                dtype_map: dict[str, object] = {}
                # Map float columns explicitly; leave others to defaults unless clearly defined
                for col, dt in zip(df.columns, df.dtypes):
                    try:
                        # Floats
                        if (
                            str(dt).startswith("Float64")
                            and ORA_BINARY_DOUBLE is not None
                        ):
                            dtype_map[col] = ORA_BINARY_DOUBLE()
                        elif (
                            str(dt).startswith("Float32")
                            and ORA_BINARY_FLOAT is not None
                        ):
                            dtype_map[col] = ORA_BINARY_FLOAT()
                        # Decimals like Decimal(18,5)
                        elif dt.__class__.__name__ == "Decimal":
                            # Extract precision/scale if available
                            prec = getattr(dt, "precision", None)
                            scale = getattr(dt, "scale", None)
                            if ORA_NUMBER is not None and prec is not None:
                                dtype_map[col] = ORA_NUMBER(prec, scale)
                        # Datetime -> TIMESTAMP(6) to preserve microseconds (Oracle DATE would drop them)
                        elif (
                            (getattr(pl, "Datetime", None) is not None and dt.__class__.__name__ == "Datetime")
                            or str(dt).startswith("Datetime")
                        ) and ORA_TIMESTAMP is not None:
                            # Use precision 6 (microseconds); Parquet dumps typically use us resolution
                            dtype_map[col] = ORA_TIMESTAMP(6)
                        # Booleans as NUMBER(1)
                        elif str(dt) == "Boolean" and ORA_NUMBER is not None:
                            dtype_map[col] = ORA_NUMBER(1, 0)
                    except Exception:
                        # Best-effort mapping; fallback to default for problematic columns
                        pass

                if dtype_map:
                    engine_options = {"dtype": dtype_map}

            df.write_database(
                table_name=full_table,
                connection=engine,
                if_table_exists="replace" if idx == 0 else "append",
                engine="sqlalchemy",
                engine_options=engine_options,
            )

        logger.info("✅ Loaded: %s", table_name)

        # 5) Cleanup parquet files
        if cleanup:
            for fname in files:
                os.remove(os.path.join(input_dir, fname))
            logger.info("🗑️ Cleanup completed for %s", table_name)
