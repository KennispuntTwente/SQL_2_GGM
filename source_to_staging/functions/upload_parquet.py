import os
import json
import logging
from collections import defaultdict
from pathlib import Path
import re

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine, text
from sqlalchemy import types as satypes
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


def group_parquet_files(
    input_dir: str, only_files: list[str] | None = None
) -> dict[str, list[str]]:
    """
    Scan input_dir and group parquet files by their logical table base name.
    Returns a mapping {base_table_name: [sorted_filenames]}.
    Filenames are returned without directory prefixes.
    """
    grouped: dict[str, list[str]] = defaultdict(list)
    if only_files is not None:
        # trust provided list, but filter to existing parquet files
        for fname in only_files:
            if not fname.lower().endswith(".parquet"):
                continue
            path = Path(input_dir, fname)
            if path.is_file():
                base = _parse_parquet_base_name(fname)
                grouped[base].append(fname)
    else:
        for fname in os.listdir(input_dir):
            path = Path(input_dir, fname)
            if fname.lower().endswith(".parquet") and path.is_file():
                base = _parse_parquet_base_name(fname)
                grouped[base].append(fname)
    # ensure deterministic order for stable loads and tests
    for k in list(grouped.keys()):
        grouped[k].sort()
    return grouped


def _decimal_type_for(dialect: str, precision: int | None, scale: int | None):
    """
    Return an appropriate SQLAlchemy Numeric/Decimal type for the target dialect.

    Falls back to a generic Numeric when no dialect specific type is required.
    """
    if precision is None:
        return None

    try:
        if dialect in ("postgresql", "sqlite"):
            return satypes.Numeric(precision=precision, scale=scale)
        if dialect in ("mysql", "mariadb"):
            from sqlalchemy.dialects.mysql import DECIMAL as MYSQL_DECIMAL  # type: ignore

            return MYSQL_DECIMAL(precision=precision, scale=scale)
        if dialect in ("mssql", "sql server"):
            from sqlalchemy.dialects.mssql import DECIMAL as MSSQL_DECIMAL  # type: ignore

            return MSSQL_DECIMAL(precision, scale)
        # For other dialects rely on the generic Numeric type
        return satypes.Numeric(precision=precision, scale=scale)
    except Exception:
        return None


def _collect_decimal_metadata(file_paths: list[str]) -> dict[str, tuple[int, int]]:
    """
    Combine decimal precision/scale across parquet parts for a logical table.

    The first chunk we load needs to create columns wide enough for all
    subsequent chunks; otherwise later values may be rounded by the destination
    database (e.g. 99.99 → 100 when the first chunk only carried scale 1).
    """

    meta: dict[str, tuple[int, int]] = {}
    for path in file_paths:
        try:
            schema = pq.read_schema(path)
        except Exception:
            continue

        for name, field in zip(schema.names, schema):
            try:
                if pa.types.is_decimal(field.type):
                    precision = getattr(field.type, "precision", None)
                    scale = getattr(field.type, "scale", None)
                    if precision is None or scale is None:
                        continue
                    key = name.lower()
                    prev = meta.get(key)
                    if prev is None:
                        meta[key] = (precision, scale)
                    else:
                        meta[key] = (
                            max(prev[0], precision),
                            max(prev[1], scale),
                        )
            except Exception:
                continue

    return meta


def upload_parquet(
    engine,
    schema=None,
    input_dir="data",
    cleanup=True,
    manifest_path: str | None = None,
):
    """
    Uploads (possibly chunked) Parquet files into destination DB.
    Ensures the target database and schema exist before loading.
    """
    dialect = engine.dialect.name.lower()
    manifest_files: list[str] | None = None
    if manifest_path:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            # Basic sanity: ensure manifest output_dir matches input_dir if absolute
            mf_dir = manifest.get("output_dir")
            files = manifest.get("files")
            if isinstance(files, list):
                manifest_files = [str(x) for x in files]
            if mf_dir and os.path.isabs(mf_dir):
                if os.path.abspath(input_dir) != os.path.abspath(mf_dir):
                    logger.warning(
                        "Manifest output_dir %s differs from input_dir %s; proceeding with input_dir",
                        mf_dir,
                        input_dir,
                    )
        except Exception as e:
            logger.warning(
                "Failed to read manifest %s: %s; falling back to directory scan",
                manifest_path,
                e,
            )
            manifest_files = None

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
            elif dialect == "sqlite":
                # SQLite has no schema namespace; skip
                pass
            else:
                try:
                    conn.execute(CreateSchema(schema))
                except ProgrammingError as e:
                    if "already exists" not in str(e).lower():
                        raise

    # 3) Group Parquet files by table base name (robust to names containing "_part").
    # If a manifest is provided, only consider files from this run.
    grouped = group_parquet_files(input_dir, only_files=manifest_files)

    # 4) Write each group into its table
    # Track remaining files across all groups so we can still cleanup if a fatal error happens mid-way
    remaining_files = {fname for flist in grouped.values() for fname in flist}

    try:
        for table_name, files in grouped.items():
            full_table = f"{schema}.{table_name}" if schema else table_name
            logger.info("📦 Uploading %s part(s) to table %s", len(files), full_table)
            # Ensure per-table cleanup executes even if an error occurs during processing
            try:
                decimal_meta = _collect_decimal_metadata(
                    [os.path.join(input_dir, fname) for fname in files]
                )

                for idx, fname in enumerate(files):
                    path = os.path.join(input_dir, fname)
                    logger.info("🔹 Processing %s", path)
                    df = pl.read_parquet(path)
                    df = df.rename({col: col.lower() for col in df.columns})
                    dtype_map: dict[str, object] = {}

                    # Ensure the in-memory frame uses fixed-precision decimals before writing so
                    # downstream engines don't see float rounding artefacts (e.g. 99.99 -> 100.0).
                    if decimal_meta:
                        casts = []
                        for col, (prec, scale) in decimal_meta.items():
                            if col not in df.columns:
                                continue
                            try:
                                casts.append(
                                    pl.col(col).cast(
                                        pl.Decimal(precision=prec, scale=scale)
                                    )
                                )
                            except Exception:
                                # If casting fails, fall back to existing representation.
                                pass
                        if casts:
                            df = df.with_columns(casts)

                    # Apply dialect aware decimal typing (skip Oracle here; handled below).
                    if dialect != "oracle" and decimal_meta:
                        for col, (prec, scale) in decimal_meta.items():
                            sa_type = _decimal_type_for(dialect, prec, scale)
                            if sa_type is not None:
                                dtype_map[col] = sa_type

                    # For Microsoft SQL Server, ensure datetime-like columns use DATETIME2 to avoid
                    # out-of-range errors caused by the narrower DATETIME type (which starts at 1753-01-01).
                    if dialect in ("mssql", "sql server"):
                        try:
                            from sqlalchemy.dialects.mssql import (
                                DATETIME2 as MSSQL_DATETIME2,
                            )  # type: ignore
                        except Exception:
                            MSSQL_DATETIME2 = None  # type: ignore

                        if MSSQL_DATETIME2 is not None:
                            for col, dt in zip(df.columns, df.dtypes):
                                try:
                                    # Polars dtypes stringify like "Datetime(time_unit='us', time_zone=None)"
                                    if dt.__class__.__name__ == "Datetime" or str(
                                        dt
                                    ).startswith("Datetime"):
                                        # Use DATETIME2(6) to preserve microseconds if present
                                        try:
                                            dtype_map[col] = MSSQL_DATETIME2(
                                                precision=6
                                            )  # type: ignore[call-arg]
                                        except Exception:
                                            dtype_map[col] = MSSQL_DATETIME2()
                                except Exception:
                                    # Best-effort mapping; fallback to default for problematic columns
                                    pass

                    # For Oracle, guide type creation for floats to avoid generic FLOAT precision issues
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
                                    if ORA_NUMBER is not None and decimal_meta:
                                        meta = decimal_meta.get(col)
                                        if meta is not None:
                                            prec, scale = meta
                                            dtype_map[col] = ORA_NUMBER(prec, scale)
                                # Datetime -> TIMESTAMP(6) to preserve microseconds (Oracle DATE would drop them)
                                elif (
                                    (
                                        getattr(pl, "Datetime", None) is not None
                                        and dt.__class__.__name__ == "Datetime"
                                    )
                                    or str(dt).startswith("Datetime")
                                ) and ORA_TIMESTAMP is not None:
                                    # Use TIMESTAMP(6) to preserve microseconds
                                    try:
                                        dtype_map[col] = ORA_TIMESTAMP(precision=6)  # type: ignore[call-arg]
                                    except Exception:
                                        dtype_map[col] = ORA_TIMESTAMP()
                                # Booleans as NUMBER(1)
                                elif str(dt) == "Boolean" and ORA_NUMBER is not None:
                                    dtype_map[col] = ORA_NUMBER(1, 0)
                            except Exception:
                                # Best-effort mapping; fallback to default for problematic columns
                                pass

                    engine_options = {"dtype": dtype_map} if dtype_map else None

                    df.write_database(
                        table_name=full_table,
                        connection=engine,
                        if_table_exists="replace" if idx == 0 else "append",
                        engine="sqlalchemy",
                        engine_options=engine_options,
                    )

                logger.info("✅ Loaded: %s", table_name)
            finally:
                # 5) Cleanup parquet files for this table, even if an error occurred
                if cleanup:
                    for fname in files:
                        try:
                            os.remove(os.path.join(input_dir, fname))
                        except FileNotFoundError:
                            pass
                        except Exception as e:
                            logger.warning("Failed to delete %s: %s", fname, e)
                        finally:
                            remaining_files.discard(fname)
                    logger.info("🗑️ Cleanup completed for %s", table_name)
    finally:
        # If a fatal error occurred before some files were cleaned, attempt to remove them now
        if cleanup and remaining_files:
            for fname in list(remaining_files):
                try:
                    os.remove(os.path.join(input_dir, fname))
                except FileNotFoundError:
                    pass
                except Exception as e:
                    logger.warning("Final cleanup failed to delete %s: %s", fname, e)
                finally:
                    remaining_files.discard(fname)
        # Optionally remove manifest file as well when cleanup is requested
        if cleanup and manifest_path:
            try:
                os.remove(manifest_path)
            except FileNotFoundError:
                pass
            except Exception as e:
                logger.warning("Failed to delete manifest %s: %s", manifest_path, e)
