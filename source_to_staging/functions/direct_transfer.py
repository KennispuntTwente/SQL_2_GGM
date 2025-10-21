import logging
from typing import Sequence

from sqlalchemy import MetaData, Table, Column, select, text
from sqlalchemy import types as satypes
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.schema import CreateSchema

logger = logging.getLogger("source_to_staging.direct_transfer")


def _ensure_database_and_schema(engine: Engine, schema: str | None) -> None:
    """
    Ensure destination database (where applicable) and schema exist.
    Mirrors behavior used in upload_parquet for Postgres and MSSQL.
    """
    dialect = engine.dialect.name.lower()

    # 1) Ensure database exists (Postgres/MSSQL)
    db_name = engine.url.database
    if db_name:
        if dialect == "postgresql":
            from sqlalchemy import create_engine

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
            from sqlalchemy import create_engine

            admin_url = engine.url.set(database="master")
            admin_eng = create_engine(admin_url)
            try:
                with admin_eng.connect() as conn:
                    conn.execute(
                        text(
                            f"""
                        IF DB_ID(N'{db_name}') IS NULL
                        BEGIN
                            CREATE DATABASE [{db_name}];
                        END
                        """
                        )
                    )
            finally:
                admin_eng.dispose()

    # 2) Ensure schema exists
    if schema:
        with engine.begin() as conn:
            if dialect == "postgresql":
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            elif dialect in ("mssql", "sql server"):
                conn.execute(
                    text(
                        f"""
                    IF SCHEMA_ID(N'{schema}') IS NULL
                    BEGIN
                        EXEC(N'CREATE SCHEMA {schema}');
                    END
                    """
                    )
                )
            elif dialect == "oracle":
                # Oracle uses users as schemas; assume exists / has perms
                pass
            elif dialect in ("mysql", "mariadb"):
                # MySQL doesn't support schemas outside of databases
                pass
            else:
                try:
                    conn.execute(CreateSchema(schema))
                except ProgrammingError as e:
                    if "already exists" not in str(e).lower():
                        raise


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

    _ensure_database_and_schema(dest_engine, dest_schema)

    src_meta = MetaData()
    dest_meta = MetaData()

    for table_name in tables:
        qualified_src = f"{source_schema}.{table_name}" if source_schema else table_name
        qualified_dst = f"{dest_schema}.{table_name}" if dest_schema else table_name
        logger.info(
            "🚚 Copying table %s -> %s (chunk_size=%s)",
            qualified_src,
            qualified_dst,
            chunk_size,
        )

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
                dconn.execute(text(f"TRUNCATE TABLE {qualified_dst}"))
            else:  # append
                dest_table.create(bind=dconn, checkfirst=True)

        # Stream copy rows
        select_stmt = select(src_table)
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

                with dest_engine.begin() as dconn:
                    dconn.execute(insert_stmt, batch)

                inserted_total += len(batch)
                logger.info(
                    "   ↳ inserted %s rows (total %s)", len(batch), inserted_total
                )

        logger.info(
            "✅ Finished table %s (%s rows)", qualified_dst, f"{inserted_total:,}"
        )
