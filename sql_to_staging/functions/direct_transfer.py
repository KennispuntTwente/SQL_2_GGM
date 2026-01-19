import logging
import random
import time
from typing import Sequence

from sqlalchemy import MetaData, Table, Column, select, text
from sqlalchemy import types as satypes
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError, DBAPIError
from sqlalchemy.schema import CreateSchema
from utils.database.ensure_db import ensure_database_and_schema
from utils.database.identifiers import (
    quote_ident,
    quote_truncate_target,
    mssql_bracket_escape,
)

logger = logging.getLogger("sql_to_staging.direct_transfer")


def _coerce_generic_type(
    col: Column, source_dialect: str, dest_dialect: str
) -> satypes.TypeEngine:
    """
    Convert a reflected, possibly dialect-specific SQLAlchemy type to a portable
    generic type that can be rendered by any destination dialect.

    Special cases:
    - Oracle NUMBER(1) -> Boolean
    - Integral NUMBER/DECIMAL with scale 0 (or None) -> Integer
    - Preserve length/precision/scale where applicable
    """
    # Start from the generic representation if available
    asgeneric = getattr(col.type, "asgeneric", None)
    if callable(asgeneric):
        try:
            t = asgeneric()
        except Exception:
            t = col.type
    else:
        t = col.type

    # Oracle-specific source hints: NUMBER(1) mostly used as boolean
    if source_dialect == "oracle":
        if isinstance(t, satypes.Numeric) and not isinstance(t, satypes.Float):
            p = getattr(t, "precision", None)
            s = getattr(t, "scale", None)
            if p == 1 and (s in (0, None)):
                return satypes.Boolean()

    # If destination is Oracle, prefer Oracle-native types to avoid ORA-00902
    if dest_dialect == "oracle":
        try:
            from sqlalchemy.dialects.oracle import NUMBER, VARCHAR2, CLOB, BLOB
            from sqlalchemy.dialects.oracle import BINARY_FLOAT, BINARY_DOUBLE
            from sqlalchemy.dialects.oracle import TIMESTAMP as ORA_TIMESTAMP
        except Exception:
            NUMBER = None  # type: ignore
            VARCHAR2 = None  # type: ignore
            CLOB = None  # type: ignore
            BLOB = None  # type: ignore
            BINARY_FLOAT = None  # type: ignore
            BINARY_DOUBLE = None  # type: ignore
            ORA_TIMESTAMP = satypes.DateTime

        # Floats first
        if isinstance(t, satypes.Float):
            # Use binary_float for single precision, binary_double for double
            prec = getattr(t, "precision", None)
            if prec is not None and prec <= 24 and BINARY_FLOAT is not None:
                return BINARY_FLOAT()
            if BINARY_DOUBLE is not None:
                return BINARY_DOUBLE()
            return satypes.Float()

        if (
            isinstance(t, (satypes.Integer, satypes.SmallInteger, satypes.BigInteger))
            and NUMBER is not None
        ):
            if isinstance(t, satypes.SmallInteger):
                return NUMBER(5, 0)
            elif isinstance(t, satypes.BigInteger):
                return NUMBER(19, 0)
            else:
                return NUMBER(10, 0)

        if isinstance(t, satypes.Boolean) and NUMBER is not None:
            return NUMBER(1, 0)

        if (
            isinstance(t, satypes.Numeric)
            and not isinstance(t, satypes.Float)
            and NUMBER is not None
        ):
            p = getattr(t, "precision", None)
            s = getattr(t, "scale", None)
            return NUMBER(p, s)

        if isinstance(t, (satypes.String, satypes.VARCHAR)) and VARCHAR2 is not None:
            length = getattr(t, "length", None)
            if length is None:
                # treat as text
                if CLOB is not None:
                    return CLOB()
                return satypes.Text()
            return VARCHAR2(length)

        if isinstance(t, satypes.Text):
            if CLOB is not None:
                return CLOB()
            return satypes.Text()

        if isinstance(t, satypes.LargeBinary):
            if BLOB is not None:
                return BLOB()
            return satypes.LargeBinary()

        if isinstance(t, satypes.Date):
            return satypes.Date()
        if isinstance(t, satypes.DateTime):
            # Prefer Oracle TIMESTAMP
            try:
                return ORA_TIMESTAMP()
            except Exception:
                return satypes.DateTime()

        # Fallback generic
        if isinstance(t, satypes.TypeEngine):
            return t
        return satypes.String()

    # Prefer higher-precision datetime on MSSQL to avoid millisecond rounding
    if dest_dialect in ("mssql", "sql server"):
        try:
            from sqlalchemy.dialects.mssql import DATETIME2 as MSSQL_DATETIME2  # type: ignore
        except Exception:
            MSSQL_DATETIME2 = None  # type: ignore

        if isinstance(t, satypes.DateTime):
            # Use DATETIME2(6) to preserve microseconds similar to Postgres/MySQL
            if MSSQL_DATETIME2 is not None:
                try:
                    return MSSQL_DATETIME2(precision=6)
                except Exception:
                    return satypes.DateTime()
            return satypes.DateTime()
        # Fall through for other types to generic handling below

    # Normalize floats
    if isinstance(t, satypes.Float):
        return satypes.Float(precision=getattr(t, "precision", None))

    # Normalize numerics that are effectively integers (non-float)
    if isinstance(t, satypes.Numeric) and not isinstance(t, satypes.Float):
        p = getattr(t, "precision", None)
        s = getattr(t, "scale", None)
        asdec = getattr(t, "asdecimal", True)
        # Treat scale 0/None as integer when precision is reasonable
        if s in (0, None):
            if p is not None and p <= 5:
                return satypes.SmallInteger()
            if p is not None and p > 11:
                return satypes.BigInteger()
            if asdec is False or (p is not None and p <= 11):
                return satypes.Integer()
        # Otherwise, return a generic Numeric with same precision/scale
        return satypes.Numeric(precision=p, scale=s, asdecimal=True)

    # Strings
    if isinstance(t, (satypes.String, satypes.VARCHAR, satypes.Text)):
        length = getattr(t, "length", None)
        if isinstance(t, satypes.Text) or length is None:
            return satypes.Text()
        return satypes.String(length=length)

    # Date/Time
    if isinstance(t, satypes.Date):
        return satypes.Date()
    if isinstance(t, satypes.DateTime):
        return satypes.DateTime()
    if isinstance(t, satypes.Time):
        return satypes.Time()

    # Boolean
    if isinstance(t, satypes.Boolean):
        return satypes.Boolean()

    # Binary
    if isinstance(t, (satypes.LargeBinary,)):
        length = getattr(t, "length", None)
        return satypes.LargeBinary(length)

    # Integers
    if isinstance(t, (satypes.Integer, satypes.BigInteger, satypes.SmallInteger)):
        return t.__class__()

    # Fallback to a safe generic String
    return satypes.String()


def _build_destination_table(
    source_table: Table,
    dest_meta: MetaData,
    dest_table_name: str,
    dest_schema: str | None,
    lowercase_columns: bool,
    *,
    source_dialect: str,
    dest_dialect: str,
) -> Table:
    """
    Create a lightweight Table in dest metadata mirroring columns and types from
    source_table. Keeps nullability; omits constraints for portability.
    """
    cols: list[Column] = []
    for col in source_table.columns:
        new_name = col.name.lower() if lowercase_columns else col.name
        # Preserve nullability; coerce type to generic for cross-dialect DDL
        portable_type = _coerce_generic_type(col, source_dialect, dest_dialect)
        new_col = Column(new_name, portable_type, nullable=col.nullable)
        cols.append(new_col)
    return Table(dest_table_name, dest_meta, *cols, schema=dest_schema)


def direct_transfer(
    source_engine: Engine,
    dest_engine: Engine,
    tables: Sequence[str],
    *,
    source_schema: str | None = None,
    dest_schema: str | None = None,
    chunk_size: int = 100_000,
    lowercase_columns: bool = True,
    write_mode: str = "replace",  # replace | truncate | append
    row_limit: int | None = None,
    log_row_count: bool = True,
    # Retry/backoff for transient insert errors
    max_retries: int = 3,
    backoff_base_seconds: float = 0.5,
    backoff_max_seconds: float = 8.0,
    # Optional override for admin DB hop when creating databases on Postgres/MSSQL
    admin_database: str | None = None,
) -> None:
    """
    Copy listed tables from source to destination using SQLAlchemy only, in chunks.

    - Streams rows using server-side cursors (fetchmany) to keep memory bounded.
    - Creates destination database and schema if missing.
    - Creates or truncates destination tables depending on write_mode.
    - Optionally lowercases column names for consistency (default True, matching
      historical staging behavior in this repo).
    """
    assert chunk_size > 0, "chunk_size must be > 0"
    if write_mode not in {"replace", "truncate", "append"}:
        raise ValueError("write_mode must be one of: replace|truncate|append")

    ensure_database_and_schema(dest_engine, dest_schema, admin_database=admin_database)

    dest_dialect = dest_engine.dialect.name.lower()

    src_meta = MetaData()
    dest_meta = MetaData()

    for table_name in tables:
        qualified_src = f"{source_schema}.{table_name}" if source_schema else table_name
        qualified_dst = f"{dest_schema}.{table_name}" if dest_schema else table_name
        logger.info(
            "Copying table %s -> %s (chunk_size=%s)",
            qualified_src,
            qualified_dst,
            chunk_size,
        )

        # Optional upfront row count logging (can be expensive on huge tables)
        if log_row_count:
            try:
                with source_engine.connect() as sconn:
                    qname = quote_ident(source_engine, table_name)
                    if source_schema:
                        qname = f"{quote_ident(source_engine, source_schema)}.{qname}"
                    cnt = sconn.execute(text(f"SELECT COUNT(*) FROM {qname}")).scalar()
                logger.info("   (source rows: %s)", f"{cnt:,}")
            except Exception as e:
                logger.warning("Failed to COUNT(*) for %s: %s", qualified_src, e)
        else:
            logger.info("   (row count skipped; LOG_ROW_COUNT disabled)")

        # Reflect source table
        src_table = Table(
            table_name, src_meta, schema=source_schema, autoload_with=source_engine
        )
        dest_table = _build_destination_table(
            src_table,
            dest_meta,
            dest_table_name=table_name,
            dest_schema=dest_schema,
            lowercase_columns=lowercase_columns,
            source_dialect=source_engine.dialect.name.lower(),
            dest_dialect=dest_engine.dialect.name.lower(),
        )

        # Prepare destination table according to write mode
        with dest_engine.begin() as dconn:
            if write_mode == "replace":
                dest_table.drop(bind=dconn, checkfirst=True)
                dest_table.create(bind=dconn, checkfirst=True)
            elif write_mode == "truncate":
                # Create if missing, then truncate
                dest_table.create(bind=dconn, checkfirst=True)
                # SQLite does not support TRUNCATE; fall back to DELETE
                if dest_engine.dialect.name.lower() == "sqlite":
                    # Prefer SQLAlchemy DELETE for safe quoting
                    dconn.execute(dest_table.delete())
                else:
                    # Use dialect-aware quoted identifier for TRUNCATE
                    qname = quote_truncate_target(
                        dest_engine,
                        db=None,
                        schema=dest_schema,
                        table=table_name,
                    )
                    dconn.execute(text(f"TRUNCATE TABLE {qname}"))
            else:  # append
                dest_table.create(bind=dconn, checkfirst=True)

        # Stream copy rows (optionally limited for development)
        select_stmt = select(src_table)
        if row_limit and row_limit > 0:
            select_stmt = select_stmt.limit(row_limit)
        inserted_total = 0
        with source_engine.connect() as sconn:
            # Enable streaming results to avoid reading entire result set into memory
            result = sconn.execution_options(stream_results=True).execute(select_stmt)
            mapping_result = result.mappings()
            insert_stmt = dest_table.insert()

            while True:
                rows = mapping_result.fetchmany(chunk_size)
                if not rows:
                    break

                # Normalize case if needed
                if lowercase_columns:
                    batch = [
                        {k.lower(): v for k, v in row.items()}  # type: ignore[union-attr]
                        for row in rows
                    ]
                else:
                    batch = [dict(row) for row in rows]  # type: ignore[union-attr]

                # For PostgreSQL, strip NUL (0x00) from all string values.
                # Postgres text/varchar columns cannot contain NUL bytes; psycopg will error.
                if dest_dialect == "postgresql":
                    for rec in batch:
                        for key, val in rec.items():
                            if isinstance(val, str) and "\x00" in val:
                                rec[key] = val.replace("\x00", "")

                # Execute insert with small retry/backoff on transient DB errors
                attempt = 0
                while True:
                    try:
                        with dest_engine.begin() as dconn:
                            dconn.execute(insert_stmt, batch)
                        break  # success
                    except DBAPIError as e:  # type: ignore[asynckind]
                        # Determine if error looks transient and should be retried
                        msg = str(e).lower()
                        is_disconnect = bool(
                            getattr(e, "is_disconnect", False)
                            or getattr(e, "connection_invalidated", False)
                        )
                        looks_transient = is_disconnect or any(
                            tok in msg
                            for tok in (
                                "deadlock",
                                "timeout",
                                "could not serialize access",
                                "lock wait timeout exceeded",
                                "connection reset",
                                "broken pipe",
                            )
                        )
                        if attempt >= max_retries or not looks_transient:
                            logger.error(
                                "Insert batch failed (attempt %s/%s). Giving up. Error: %s",
                                attempt + 1,
                                max_retries,
                                e,
                            )
                            raise
                        # Backoff with jitter
                        sleep = min(
                            backoff_max_seconds,
                            backoff_base_seconds * (2**attempt),
                        )
                        # full jitter in [0.5x, 1.5x]
                        sleep *= 0.5 + random.random()
                        attempt += 1
                        logger.warning(
                            "Transient DB error on insert (attempt %s/%s). Retrying in %.2fs: %s",
                            attempt,
                            max_retries,
                            sleep,
                            e,
                        )
                        time.sleep(sleep)

                inserted_total += len(batch)
                logger.info(
                    "   inserted %s rows (total %s)", len(batch), inserted_total
                )

        logger.info("Finished table %s (%s rows)", qualified_dst, f"{inserted_total:,}")
