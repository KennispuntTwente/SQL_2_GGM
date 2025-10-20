import os
import logging
from collections import defaultdict
from pathlib import Path
import re

import polars as pl
from sqlalchemy import create_engine, text, MetaData, Table, Column
from sqlalchemy import Integer, BigInteger, Float, Boolean, Date, Time, DateTime, Text
from sqlalchemy import Numeric
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

    # Helper: map Polars dtype to SQLAlchemy type (best-effort, cross-dialect)
    def _sa_type_from_polars(dtype, db_dialect: str):
        # Decimal with precision/scale
        if isinstance(dtype, pl.Decimal):
            # pl.Decimal exposes .precision and .scale
            try:
                return Numeric(dtype.precision, dtype.scale)
            except Exception:
                # Fallback without explicit precision/scale
                return Numeric()
        # Integer sizes
        if dtype == pl.Int64 or dtype == pl.UInt64:
            return BigInteger()
        if dtype in (pl.Int32, pl.UInt32, pl.Int16, pl.UInt16, pl.Int8, pl.UInt8):
            return Integer()
        # Floats
        if dtype in (pl.Float64, pl.Float32):
            return Float()
        # Booleans
        if dtype == pl.Boolean:
            return Boolean()
        # Dates/Times
        if dtype == pl.Date:
            return Date()
        if dtype == pl.Time:
            return Time()
        # Some sources (e.g., MySQL via pandas) round-trip TIME as Duration; treat as TIME
        if dtype == pl.Duration:
            return Time()
        # Datetime (timezone-aware if time_zone set)
        if isinstance(dtype, pl.datatypes.Datetime):
            tz = getattr(dtype, "time_zone", None)
            return DateTime(timezone=bool(tz))
    # Default to Text for strings/objects
        return Text()

    # 4) Write each group into its table
    for table_name, files in grouped.items():
        full_table = f"{schema}.{table_name}" if schema else table_name
        logger.info("📦 Uploading %s part(s) to table %s", len(files), full_table)

        # Pre-create table with inferred SQL types from first parquet file to preserve DECIMAL types
        first_path = os.path.join(input_dir, files[0])
        df0 = pl.read_parquet(first_path)
        df0 = df0.rename({col: col.lower() for col in df0.columns})
        # Build SQLAlchemy table
        md = MetaData()
        cols = []
        for col_name, dtype in df0.schema.items():
            sa_type = _sa_type_from_polars(dtype, dialect)
            # Heuristic: promote Utf8 columns that look like decimals to NUMERIC with inferred precision/scale
            if sa_type.__class__ is Text and dtype == pl.Utf8:
                series = df0.get_column(col_name).drop_nans().drop_nulls()
                # Consider only a reasonable sample to avoid heavy scans
                sample = series.head(1000).to_list()
                dec_pattern = re.compile(r"^-?\d+(?:\.\d+)?$")
                decimal_like = [s for s in sample if isinstance(s, str) and dec_pattern.match(s)]
                if decimal_like and len(decimal_like) == len(sample):
                    max_int = 1
                    max_scale = 0
                    for s in decimal_like:
                        sign_stripped = s[1:] if s.startswith("-") else s
                        if "." in sign_stripped:
                            int_part, frac_part = sign_stripped.split(".", 1)
                        else:
                            int_part, frac_part = sign_stripped, ""
                        # Count digits; preserve 1 digit for zero
                        int_digits = len(int_part.lstrip("0")) or 1
                        frac_digits = len(frac_part)
                        if int_digits > max_int:
                            max_int = int_digits
                        if frac_digits > max_scale:
                            max_scale = frac_digits
                    precision = max_int + max_scale
                    # Cap precision to a common max (e.g., 38 for many DBs)
                    if precision > 38:
                        precision = 38
                        if max_scale > precision:
                            max_scale = min(max_scale, precision)
                    sa_type = Numeric(precision, max_scale)
                else:
                    # Heuristic: time-like strings 'HH:MM:SS' -> TIME
                    time_pat = re.compile(r"^\d{1,2}:\d{2}:\d{2}$")
                    time_like = [s for s in sample if isinstance(s, str) and time_pat.match(s)]
                    if time_like and len(time_like) == len(sample) and len(sample) > 0:
                        sa_type = Time()
            cols.append(Column(col_name, sa_type))
        tbl = Table(table_name, md, *cols, schema=schema)
        # Drop and create fresh (mirrors previous replace semantics)
        with engine.begin() as conn:
            tbl.drop(bind=conn, checkfirst=True)
            md.create_all(bind=conn)

        for idx, fname in enumerate(files):
            path = os.path.join(input_dir, fname)
            logger.info("🔹 Processing %s", path)
            df = pl.read_parquet(path)
            df = df.rename({col: col.lower() for col in df.columns})
            # Workaround for MySQL and other backends: Polars writes pl.Time via pandas as timedelta/int (ns),
            # which leads to values like 11045000000000 instead of '03:04:05'. Convert time columns to
            # canonical 'HH:MM:SS' strings before inserting; SQL engines accept these for TIME columns.
            try:
                # Normalize pl.Time columns using strftime
                time_cols = [name for name, dtype in df.schema.items() if dtype == pl.Time]
                # Normalize pl.Duration columns by deriving HH:MM:SS from nanoseconds
                duration_cols = [name for name, dtype in df.schema.items() if dtype == pl.Duration]
                # Normalize Utf8 columns that are time-like to HH:MM:SS
                utf8_time_cols = []
                for name, dtype in df.schema.items():
                    if dtype == pl.Utf8:
                        series = df.get_column(name).drop_nans().drop_nulls()
                        sample = series.head(1000).to_list()
                        if sample:
                            if all(isinstance(s, str) and re.match(r"^\d{1,2}:\d{2}:\d{2}$", s) for s in sample):
                                utf8_time_cols.append(name)
                exprs = []
                if time_cols:
                    exprs.extend([
                        pl.col(c).dt.strftime("%H:%M:%S").alias(c) for c in time_cols
                    ])
                if duration_cols:
                    for c in duration_cols:
                        # Unit-agnostic: derive total seconds using Polars, then HH:MM:SS
                        secs = pl.col(c).dt.total_seconds().floor().cast(pl.Int64)
                        hh = (secs // 3600).cast(pl.Utf8).str.pad_start(2, fill_char="0")
                        mm = ((secs % 3600) // 60).cast(pl.Utf8).str.pad_start(2, fill_char="0")
                        ss = (secs % 60).cast(pl.Utf8).str.pad_start(2, fill_char="0")
                        exprs.append(pl.concat_str([hh, mm, ss], separator=":").alias(c))
                if utf8_time_cols:
                    for c in utf8_time_cols:
                        # Coerce to strict zero-padded HH:MM:SS
                        parts = pl.col(c).str.split(":", inclusive=False)
                        hh = parts.list.get(0).cast(pl.Int64).cast(pl.Utf8).str.pad_start(2, fill_char="0")
                        mm = parts.list.get(1).cast(pl.Int64).cast(pl.Utf8).str.pad_start(2, fill_char="0")
                        ss = parts.list.get(2).cast(pl.Int64).cast(pl.Utf8).str.pad_start(2, fill_char="0")
                        exprs.append(pl.concat_str([hh, mm, ss], separator=":").alias(c))
                if exprs:
                    df = df.with_columns(exprs)
            except Exception as e:
                logger.debug("Time column normalization skipped due to: %s", e)
            # For SQLAlchemy engines, prefer passing schema separately to avoid creating a literal
            # table named "schema.table". This ensures rows append to the pre-created table.
            try:
                df.write_database(
                    table_name=table_name,
                    connection=engine,
                    if_table_exists="append",  # table already created with correct types
                    engine="sqlalchemy",
                    schema=schema,
                )
            except TypeError:
                # Older Polars versions may not support 'schema' param; fall back to base name.
                df.write_database(
                    table_name=table_name,
                    connection=engine,
                    if_table_exists="append",
                    engine="sqlalchemy",
                )

        logger.info("✅ Loaded: %s", table_name)

        # 5) Cleanup parquet files
        if cleanup:
            for fname in files:
                os.remove(os.path.join(input_dir, fname))
            logger.info("🗑️ Cleanup completed for %s", table_name)
