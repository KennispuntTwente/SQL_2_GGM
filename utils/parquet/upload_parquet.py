"""Shared Parquet upload helpers.

This module hosts the generic Parquet → SQLAlchemy upload logic so that
pipelines (sql_to_staging, odata_to_staging, etc.) can all depend on the
same implementation without cross-importing each other.
"""

from __future__ import annotations

from collections import defaultdict
import json
import logging
import os
from pathlib import Path
import re
from typing import Any

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text
from sqlalchemy import types as satypes
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.schema import CreateSchema

from utils.database.ensure_db import ensure_database_and_schema
from utils.database.identifiers import (
    mssql_bracket_escape,
    quote_ident,
    quote_truncate_target,
)


logger = logging.getLogger("utils.parquet.upload_parquet")


def _sanitize_table_name(name: str) -> str:
    """Sanitize a table name by removing brackets and replacing dots with underscores.

    This handles OData entity set names like '[APICUST].[METADATA]' which would
    otherwise be misinterpreted as schema-qualified table names.

    Args:
        name: Raw table name that may contain brackets and dots

    Returns:
        Sanitized table name safe for use as a SQL identifier
    """
    # Remove square brackets
    sanitized = name.replace("[", "").replace("]", "")
    # Replace dots with underscores to avoid schema.table interpretation
    sanitized = sanitized.replace(".", "_")
    return sanitized


def _parse_parquet_base_name(filename: str) -> str:
    """Derive the logical table base name from a parquet filename."""

    stem = Path(filename).stem
    m = re.match(r"^(?P<base>.+)_part\d+$", stem)
    base = m.group("base") if m else stem
    # Sanitize to handle bracket-quoted OData names
    return _sanitize_table_name(base)


def group_parquet_files(
    input_dir: str, only_files: list[str] | None = None
) -> dict[str, list[str]]:
    """Scan input_dir and group parquet files by logical table base name."""

    input_path = Path(input_dir)
    if not input_path.exists():
        raise RuntimeError(
            "Parquet input directory is missing; run the download/export step first or point --input-dir/manifest to an existing folder."
            f" Missing path: {input_path}"
        )
    if not input_path.is_dir():
        raise RuntimeError(f"Parquet input path is not a directory: {input_path}")

    grouped: dict[str, list[str]] = defaultdict(list)
    if only_files is not None:
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

    for k in list(grouped.keys()):
        grouped[k].sort()
    return grouped


def _decimal_type_for(dialect: str, precision: int | None, scale: int | None):
    """Return a dialect-appropriate Numeric/Decimal type."""

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
        return satypes.Numeric(precision=precision, scale=scale)
    except Exception:
        return None


def _collect_decimal_metadata(file_paths: list[str]) -> dict[str, tuple[int, int]]:
    """Combine decimal precision/scale across parquet parts for a logical table."""

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
    engine: Any,
    schema: str | None = None,
    input_dir: str = "data",
    cleanup: bool = True,
    manifest_path: str | None = None,
    *,
    write_mode: str = "replace",  # replace | truncate | append
    admin_database: str | None = None,
    lower_table_names: bool = False,
):
    """Upload (possibly chunked) Parquet files into a destination database."""

    if write_mode.lower() not in {"replace", "truncate", "append"}:
        raise ValueError("write_mode must be one of: replace|truncate|append")
    write_mode = write_mode.lower()
    dialect = engine.dialect.name.lower()

    manifest_files: list[str] | None = None
    if manifest_path:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:  # pragma: no cover - defensive logging
            raise RuntimeError(
                f"Failed to read parquet manifest {manifest_path}: {e}. Aborting upload to avoid stale file ingestion."
            ) from e

        mf_dir = manifest.get("output_dir")
        files = manifest.get("files")
        if not isinstance(files, list):
            raise RuntimeError(
                f"Manifest {manifest_path} missing 'files' list; aborting to avoid scanning stale directory contents."
            )
        manifest_files = [str(x) for x in files]
        if mf_dir and os.path.isabs(mf_dir):
            if os.path.abspath(input_dir) != os.path.abspath(mf_dir):
                logger.warning(
                    "Manifest output_dir %s differs from input_dir %s; proceeding with input_dir anyway (files list still enforced).",
                    mf_dir,
                    input_dir,
                )

    ensure_database_and_schema(engine, schema, admin_database=admin_database)

    grouped = group_parquet_files(input_dir, only_files=manifest_files)

    remaining_files = {fname for flist in grouped.values() for fname in flist}

    try:
        for table_name, files in grouped.items():
            logical_table = table_name.lower() if lower_table_names else table_name
            full_table = f"{schema}.{logical_table}" if schema else logical_table
            logger.info("📦 Uploading %s part(s) to table %s", len(files), full_table)

            from sqlalchemy import inspect

            inspector = inspect(engine)
            table_exists = False
            try:
                table_exists = inspector.has_table(logical_table, schema=schema)
            except Exception:
                table_exists = False

            if write_mode == "truncate" and table_exists:
                from sqlalchemy import MetaData, Table

                with engine.begin() as conn:
                    dname = engine.dialect.name.lower()
                    if dname == "sqlite":
                        try:
                            meta = MetaData()
                            tgt = Table(
                                logical_table,
                                meta,
                                schema=schema,
                                autoload_with=engine,
                            )
                            conn.execute(tgt.delete())
                        except Exception:
                            qname = quote_truncate_target(
                                engine, None, schema, logical_table
                            )
                            conn.execute(text(f"DELETE FROM {qname}"))
                    else:
                        qname = quote_truncate_target(
                            engine, engine.url.database, schema, logical_table
                        )
                        conn.execute(text(f"TRUNCATE TABLE {qname}"))

            decimal_meta = _collect_decimal_metadata(
                [os.path.join(input_dir, fname) for fname in files]
            )

            for idx, fname in enumerate(files):
                path = os.path.join(input_dir, fname)
                logger.info("🔹 Processing %s", path)
                # Use glob=False to prevent brackets in filenames being treated as glob patterns
                df = pl.read_parquet(path, glob=False)
                df = df.rename({col: col.lower() for col in df.columns})

                if dialect == "postgresql":
                    string_cols: list[str] = []
                    for col_name, dtype in zip(df.columns, df.dtypes):
                        if str(dtype) in ("Utf8", "String"):
                            string_cols.append(col_name)
                    if string_cols:
                        df = df.with_columns(
                            [
                                pl.col(c).str.replace_all("\x00", "").alias(c)
                                for c in string_cols
                            ]
                        )

                dtype_map: dict[str, Any] = {}

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
                            pass
                    if casts:
                        df = df.with_columns(casts)

                if dialect != "oracle" and decimal_meta:
                    for col, (prec, scale) in decimal_meta.items():
                        sa_type = _decimal_type_for(dialect, prec, scale)
                        if sa_type is not None:
                            dtype_map[col] = sa_type

                if dialect in ("mssql", "sql server"):
                    try:
                        from sqlalchemy.dialects.mssql import (
                            DATETIME2 as MSSQL_DATETIME2,
                        )  # type: ignore
                    except Exception:  # pragma: no cover - environment specific
                        MSSQL_DATETIME2 = None  # type: ignore

                    if MSSQL_DATETIME2 is not None:
                        for col, dt in zip(df.columns, df.dtypes):
                            try:
                                if dt.__class__.__name__ == "Datetime" or str(
                                    dt
                                ).startswith("Datetime"):
                                    try:
                                        dtype_map[col] = MSSQL_DATETIME2(precision=6)  # type: ignore[call-arg]
                                    except Exception:
                                        dtype_map[col] = MSSQL_DATETIME2()
                            except Exception:
                                pass

                if dialect == "oracle":
                    try:
                        from sqlalchemy.dialects.oracle import (
                            BINARY_DOUBLE as ORA_BINARY_DOUBLE,
                            BINARY_FLOAT as ORA_BINARY_FLOAT,
                            NUMBER as ORA_NUMBER,
                            TIMESTAMP as ORA_TIMESTAMP,
                        )
                    except Exception:  # pragma: no cover - env specific
                        ORA_BINARY_FLOAT = None  # type: ignore
                        ORA_BINARY_DOUBLE = None  # type: ignore
                        ORA_NUMBER = None  # type: ignore
                        ORA_TIMESTAMP = None  # type: ignore

                    for col, dt in zip(df.columns, df.dtypes):
                        try:
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
                            elif dt.__class__.__name__ == "Decimal":
                                if ORA_NUMBER is not None and decimal_meta:
                                    meta = decimal_meta.get(col)
                                    if meta is not None:
                                        prec, scale = meta
                                        dtype_map[col] = ORA_NUMBER(prec, scale)
                            elif (
                                (
                                    getattr(pl, "Datetime", None) is not None
                                    and dt.__class__.__name__ == "Datetime"
                                )
                                or str(dt).startswith("Datetime")
                            ) and ORA_TIMESTAMP is not None:
                                try:
                                    dtype_map[col] = ORA_TIMESTAMP(precision=6)  # type: ignore[call-arg]
                                except Exception:
                                    dtype_map[col] = ORA_TIMESTAMP()
                            elif str(dt) == "Boolean" and ORA_NUMBER is not None:
                                dtype_map[col] = ORA_NUMBER(1, 0)
                        except Exception:
                            pass

                if idx == 0:
                    if write_mode == "replace":
                        mode = "replace"
                    elif write_mode == "append":
                        mode = "append" if table_exists else "replace"
                    else:
                        mode = "append" if table_exists else "replace"
                else:
                    mode = "append"

                engine_options: dict[str, Any] | None = (
                    {"dtype": dtype_map} if dtype_map else None
                )

                write_kwargs: dict[str, Any] = dict(
                    table_name=logical_table,
                    connection=engine,
                    if_table_exists=mode,
                    engine="sqlalchemy",
                    engine_options=engine_options,
                )
                if schema is not None:
                    write_kwargs["schema"] = schema

                try:
                    df.write_database(**write_kwargs)  # type: ignore[arg-type]
                except TypeError as e:
                    dname = engine.dialect.name.lower()
                    if schema is not None and dname == "postgresql":
                        try:
                            write_kwargs.pop("schema", None)
                            with engine.begin() as conn:
                                try:
                                    conn.execute(
                                        text("SET search_path TO :schema, public"),
                                        {"schema": schema},
                                    )
                                except Exception:
                                    conn.execute(
                                        text(
                                            f"SET search_path TO {quote_ident(engine, schema)}, public"
                                        )
                                    )
                                write_kwargs["connection"] = conn
                                df.write_database(**write_kwargs)  # type: ignore[arg-type]
                                continue
                        except TypeError:
                            pass
                        except Exception:
                            pass

                    for drop_key in ("schema", "dtype"):
                        if drop_key in write_kwargs:
                            write_kwargs.pop(drop_key, None)
                            try:
                                df.write_database(**write_kwargs)  # type: ignore[arg-type]
                                break
                            except TypeError:
                                continue
                    else:
                        raise e

            logger.info("✅ Loaded: %s", logical_table)

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
        if cleanup and manifest_path:
            try:
                os.remove(manifest_path)
            except FileNotFoundError:
                pass
            except Exception as e:
                logger.warning("Failed to delete manifest %s: %s", manifest_path, e)


__all__ = [
    "upload_parquet",
    "group_parquet_files",
]
