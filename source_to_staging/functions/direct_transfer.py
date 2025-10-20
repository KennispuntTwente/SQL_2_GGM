import logging
from typing import Sequence

from sqlalchemy import MetaData, Table, Column, select, text
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


def _build_destination_table(
    source_table: Table,
    dest_meta: MetaData,
    dest_table_name: str,
    dest_schema: str | None,
    lowercase_columns: bool,
) -> Table:
    """
    Create a lightweight Table in dest metadata mirroring columns and types from
    source_table. Keeps nullability; omits constraints for portability.
    """
    cols: list[Column] = []
    for col in source_table.columns:
        new_name = col.name.lower() if lowercase_columns else col.name
        # Preserve type and nullability; skip constraints/sequences for portability
        new_col = Column(new_name, col.type, nullable=col.nullable)
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
        logger.info("🚚 Copying table %s -> %s (chunk_size=%s)", qualified_src, qualified_dst, chunk_size)

        # Reflect source table
        src_table = Table(table_name, src_meta, schema=source_schema, autoload_with=source_engine)
        dest_table = _build_destination_table(
            src_table,
            dest_meta,
            dest_table_name=table_name,
            dest_schema=dest_schema,
            lowercase_columns=lowercase_columns,
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
                logger.info("   ↳ inserted %s rows (total %s)", len(batch), inserted_total)

        logger.info("✅ Finished table %s (%s rows)", qualified_dst, f"{inserted_total:,}")
