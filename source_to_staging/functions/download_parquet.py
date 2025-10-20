import os
import logging
from typing import Iterable

import polars as pl
import pyarrow as pa
import connectorx as cx
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy import MetaData, Table, select, cast, String
from sqlalchemy.dialects.mssql import DATETIMEOFFSET as MSSQL_DATETIMEOFFSET
from sqlalchemy.sql.sqltypes import DateTime as SA_DateTime
from urllib.parse import urlparse

logger = logging.getLogger("source_to_staging.download_parquet")


def download_parquet(
    connection,
    tables,
    output_dir: str = "data",
    chunk_size: int = 100_000,
    schema: str | None = None,
):
    """
    Dumps specified *tables* to Parquet files **without ever holding more than
    ``chunk_size`` rows in memory**.

        The *connection* can be either a ConnectorX-compatible URI (str) or a
        SQLAlchemy Engine. Behavior:

        - If a URI is provided, uses ConnectorX read_sql with return_type="arrow_stream"
            and batch_size to stream Arrow record batches and write each to an
            individual Parquet part file.
        - If an Engine is provided, uses `polars.read_database(..., iter_batches=True)`
            with `batch_size` to iterate and write Parquet part files.

        This avoids manual SQL pagination and keeps memory bounded to ~chunk_size rows.
    """

    # Create destination directory once
    os.makedirs(output_dir, exist_ok=True)

    # ──────────────────────────────────────────────────────────────────────
    # 1 Identify connection mode
    # ──────────────────────────────────────────────────────────────────────
    if isinstance(connection, str):
        is_uri = True
        uri = connection
    elif isinstance(connection, Engine):
        is_uri = False
        engine = connection
    else:
        raise ValueError(
            "connection must be a SQLAlchemy Engine or a ConnectorX URI string"
        )

    # Helper: qualify table names by schema
    def qualify(tbl: str) -> str:
        eff_schema = schema
        if is_uri and not eff_schema:
            try:
                parsed = urlparse(uri)
                scheme = (parsed.scheme or "").lower()
            except Exception:
                scheme = ""
            if scheme.startswith("postgres"):
                eff_schema = "public"
            elif scheme in ("mssql", "sqlserver"):
                eff_schema = "dbo"
        if not eff_schema:
            return tbl
        return f"{eff_schema}.{tbl}"

    # ──────────────────────────────────────────────────────────────────────
    # 2 Export loop per table
    # ──────────────────────────────────────────────────────────────────────
    for table in tables:
        qualified = qualify(table)
        base_select = f"SELECT * FROM {qualified}"

        # ── ConnectorX path ───────────────────────────────────
        if is_uri:
            logger.info("📥 Dumping table via ConnectorX (arrow_stream): %s", qualified)
            # If using MSSQL via ConnectorX, cast overly large DECIMAL columns to VARCHAR
            # to avoid rust_decimal overflow during Arrow materialization.
            try:
                parsed_uri = urlparse(uri)
                scheme = (parsed_uri.scheme or "").lower()
            except Exception:
                scheme = ""
            force_sqlalchemy = False
            eng_tmp = None
            if scheme in ("mssql", "sqlserver"):
                try:
                    # Build a temporary SQLAlchemy engine for reflection
                    from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
                    from urllib.parse import unquote
                    user = unquote(parsed_uri.username) if parsed_uri.username else ""
                    pw = unquote(parsed_uri.password) if parsed_uri.password else ""
                    host = parsed_uri.hostname or "localhost"
                    port = int(parsed_uri.port or 1433)
                    db = (parsed_uri.path or "/").lstrip("/")
                    eng_tmp = create_sqlalchemy_engine("mssql", user, pw, host, port, db)
                    with eng_tmp.connect() as conn_tmp:
                        # Reflect and build a safe SELECT with casts for large NUMERICs
                        if "." in qualified:
                            sch, tbl = qualified.split(".", 1)
                        else:
                            sch, tbl = None, qualified
                        md = MetaData()
                        t = Table(tbl, md, autoload_with=conn_tmp, schema=sch)
                        from sqlalchemy.sql.sqltypes import Numeric as SA_Numeric
                        select_list = []
                        big_decimal_found = False
                        for col in t.columns:
                            dt = col.type
                            if isinstance(dt, SA_Numeric) and getattr(dt, "precision", None) and getattr(dt, "precision") > 28:
                                big_decimal_found = True
                                expr = cast(col, String(100)).label(col.name)
                            else:
                                expr = col
                            select_list.append(expr)
                        stmt = select(*select_list).select_from(t)
                        base_select = stmt.compile(
                            dialect=conn_tmp.engine.dialect,
                            compile_kwargs={"literal_binds": True},
                        ).string
                        logger.info("Using MSSQL ConnectorX-safe SELECT: %s", base_select)
                        if big_decimal_found:
                            force_sqlalchemy = True
                except Exception as _mssql_rewrite_err:
                    # If any step fails, proceed with the original base_select
                    logger.debug("MSSQL SELECT rewrite failed: %s", _mssql_rewrite_err)
                # Regardless of rewrite, prefer SQLAlchemy path for MSSQL to ensure type fidelity
                force_sqlalchemy = True

            # Postgres: prefer SQLAlchemy streaming due to ConnectorX decimal scale mismatch
            if scheme.startswith("postgres"):
                try:
                    from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
                    from urllib.parse import unquote
                    user = unquote(parsed_uri.username) if parsed_uri.username else ""
                    pw = unquote(parsed_uri.password) if parsed_uri.password else ""
                    host = parsed_uri.hostname or "localhost"
                    port = int(parsed_uri.port or 5432)
                    db = (parsed_uri.path or "/").lstrip("/")
                    eng_tmp = create_sqlalchemy_engine("postgresql+psycopg2", user, pw, host, port, db)
                except Exception as _pg_eng_err:
                    logger.debug("Postgres engine build failed: %s", _pg_eng_err)
                force_sqlalchemy = True

            # MySQL/MariaDB: prefer SQLAlchemy streaming to avoid float coercion of DECIMAL and TIME duration issues
            if scheme in ("mysql", "mariadb"):
                try:
                    from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
                    from urllib.parse import unquote
                    user = unquote(parsed_uri.username) if parsed_uri.username else ""
                    pw = unquote(parsed_uri.password) if parsed_uri.password else ""
                    host = parsed_uri.hostname or "localhost"
                    port = int(parsed_uri.port or (3306 if scheme == "mysql" else 3306))
                    db = (parsed_uri.path or "/").lstrip("/")
                    eng_tmp = create_sqlalchemy_engine("mysql+pymysql", user, pw, host, port, db)
                except Exception as _my_eng_err:
                    logger.debug("MySQL engine build failed: %s", _my_eng_err)
                force_sqlalchemy = True

            # Oracle: prefer SQLAlchemy streaming; ensure DECIMAL columns preserve precision/scale
            if scheme == "oracle":
                try:
                    from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
                    from urllib.parse import unquote
                    user = unquote(parsed_uri.username) if parsed_uri.username else ""
                    pw = unquote(parsed_uri.password) if parsed_uri.password else ""
                    host = parsed_uri.hostname or "localhost"
                    port = int(parsed_uri.port or 1521)
                    db = (parsed_uri.path or "/").lstrip("/")
                    # oracledb dialect
                    eng_tmp = create_sqlalchemy_engine("oracle+oracledb", user, pw, host, port, db)
                except Exception as _ora_eng_err:
                    logger.debug("Oracle engine build failed: %s", _ora_eng_err)
                force_sqlalchemy = True

            if force_sqlalchemy:
                logger.info(
                    "Falling back to SQLAlchemy streaming for %s due to wide DECIMAL columns",
                    qualified,
                )
                # Build schema overrides for tz-aware datetimes
                schema_overrides_fallback: dict[str, pl.datatypes.PolarsDataType] | None = None
                try:
                    with eng_tmp.connect() as c2:
                        if "." in qualified:
                            sch2, tbl2 = qualified.split(".", 1)
                        else:
                            sch2, tbl2 = None, qualified
                        md2 = MetaData()
                        t2 = Table(tbl2, md2, autoload_with=c2, schema=sch2)
                        overrides2: dict[str, pl.datatypes.PolarsDataType] = {}
                        for c in t2.columns:
                            if isinstance(c.type, SA_DateTime) and getattr(c.type, "timezone", False):
                                overrides2[c.name] = pl.Datetime(time_unit="us", time_zone="UTC")
                            elif isinstance(c.type, MSSQL_DATETIMEOFFSET):
                                overrides2[c.name] = pl.Datetime(time_unit="us", time_zone="UTC")
                            else:
                                # Preserve DECIMAL/NUMERIC columns as Polars Decimal to avoid float coercion
                                try:
                                    from sqlalchemy.sql.sqltypes import Numeric as SA_Numeric
                                except Exception:
                                    SA_Numeric = None  # type: ignore[assignment]
                                if SA_Numeric and isinstance(c.type, SA_Numeric):
                                    prec = getattr(c.type, "precision", None)
                                    scale = getattr(c.type, "scale", None)
                                    if prec and scale is not None and 1 <= prec <= 38 and 0 <= scale <= prec:
                                        overrides2[c.name] = pl.Decimal(precision=prec, scale=scale)
                        if overrides2:
                            schema_overrides_fallback = overrides2
                except Exception:
                    schema_overrides_fallback = None

                try:
                    with eng_tmp.connect() as c3:
                        batches_fb = pl.read_database(
                            query=f"SELECT * FROM {qualified}",
                            connection=c3,
                            iter_batches=True,
                            batch_size=chunk_size,
                            infer_schema_length=chunk_size,
                            schema_overrides=schema_overrides_fallback,
                        )
                        for idx, batch_df in enumerate(batches_fb):
                            out = os.path.join(output_dir, f"{table}_part{idx:04d}.parquet")
                            batch_df.write_parquet(out)
                            logger.info("✅ pl.read_database chunk %s written: %s", idx, out)
                except Exception as e:
                    logger.warning("SQLAlchemy fallback streaming failed for %s: %s", qualified, e)
                # Move to next table since we've handled via fallback
                continue
            # Stream arrow record batches directly from the source using ConnectorX
            reader_or_iter: Iterable
            reader_or_iter = cx.read_sql(
                uri,
                base_select,
                return_type="arrow_stream",
                batch_size=chunk_size,
            )
            # Normalize to an iterator of RecordBatch regardless of concrete return type
            iterator: Iterable
            if isinstance(reader_or_iter, pa.Table):
                # Chunk the table into batches of roughly chunk_size rows
                iterator = reader_or_iter.to_batches(max_chunksize=chunk_size)
            elif hasattr(reader_or_iter, "read_next_batch"):
                # RecordBatchReader: expose as python iterator
                reader = reader_or_iter

                def _iter_reader():
                    while True:
                        try:
                            batch = reader.read_next_batch()
                        except StopIteration:
                            break
                        if batch is None:
                            break
                        yield batch

                iterator = _iter_reader()
            else:
                # Assume it's already an iterable of RecordBatch
                iterator = reader_or_iter  # type: ignore[assignment]

            wrote_any = False
            part_written = 0
            for batch in iterator:
                # Ensure we have a non-empty batch; some sources could return empty
                if getattr(batch, "num_rows", None) in (0, None):
                    continue
                table_arrow = pa.Table.from_batches([batch])
                df: pl.DataFrame = pl.from_arrow(table_arrow)  # type: ignore[assignment]

                out = os.path.join(
                    output_dir, f"{table}_part{part_written:04d}.parquet"
                )
                df.write_parquet(out)
                wrote_any = True
                try:
                    nrows = len(df)
                except Exception:
                    nrows = "?"
                logger.info(
                    "✅ ConnectorX chunk %s written: %s (%s rows)",
                    part_written,
                    out,
                    nrows,
                )
                part_written += 1

            if not wrote_any:
                # Fallback: fetch as a single Arrow Table and write if there are rows
                try:
                    table_full: pa.Table = cx.read_sql(uri, base_select, return_type="arrow")  # type: ignore[assignment]
                    if table_full.num_rows and table_full.num_rows > 0:
                        df_full = pl.from_arrow(table_full)
                        out = os.path.join(output_dir, f"{table}_part0000.parquet")
                        df_full.write_parquet(out)
                        logger.info(
                            "✅ ConnectorX fallback written: %s (%s rows)", out, table_full.num_rows
                        )
                    else:
                        logger.info("   (no rows)")
                except Exception as e:
                    logger.warning("ConnectorX fallback failed: %s", e)

        # ── SQLAlchemy Engine path  ────────────
        else:
            logger.info("📥 Dumping table via SQLAlchemy: %s", qualified)
            with engine.connect() as conn:
                try:
                    row_count = conn.execute(
                        text(f"SELECT COUNT(*) FROM {qualified}")
                    ).scalar()
                except Exception as err:
                    raise RuntimeError(
                        f"Failed to count rows for {qualified}: {err}"
                    ) from err

                logger.info("   (total rows: %s)", f"{row_count:,}")

                # For some dialects (notably MSSQL), tz-aware DateTime columns can
                # cause Polars to infer Utf8 while rows provide datetime[tz],
                # leading to a ComputeError. Provide explicit schema_overrides for
                # such columns to ensure a stable dtype.
                schema_overrides: dict[str, pl.datatypes.PolarsDataType] | None = None
                try:
                    if "." in qualified:
                        sch, tbl = qualified.split(".", 1)
                    else:
                        sch, tbl = None, qualified
                    md = MetaData()
                    t = Table(tbl, md, autoload_with=conn, schema=sch)
                    overrides: dict[str, pl.datatypes.PolarsDataType] = {}
                    for c in t.columns:
                        # tz-aware generic DateTime
                        if isinstance(c.type, SA_DateTime) and getattr(c.type, "timezone", False):
                            overrides[c.name] = pl.Datetime(time_unit="us", time_zone="UTC")
                        # MSSQL DATETIMEOFFSET
                        elif isinstance(c.type, MSSQL_DATETIMEOFFSET):
                            overrides[c.name] = pl.Datetime(time_unit="us", time_zone="UTC")
                        else:
                            # Preserve DECIMAL/NUMERIC as Polars Decimal for all dialects
                            try:
                                from sqlalchemy.sql.sqltypes import Numeric as SA_Numeric
                            except Exception:
                                SA_Numeric = None  # type: ignore[assignment]
                            if SA_Numeric and isinstance(c.type, SA_Numeric):
                                prec = getattr(c.type, "precision", None)
                                scale = getattr(c.type, "scale", None)
                                if prec and scale is not None and 1 <= prec <= 38 and 0 <= scale <= prec:
                                    overrides[c.name] = pl.Decimal(precision=prec, scale=scale)
                    if overrides:
                        schema_overrides = overrides
                except Exception:
                    schema_overrides = None

                batches = pl.read_database(
                    query=base_select,
                    connection=conn,
                    iter_batches=True,
                    batch_size=chunk_size,
                    infer_schema_length=chunk_size,
                    schema_overrides=schema_overrides,
                )
                for idx, batch_df in enumerate(batches):
                    out = os.path.join(output_dir, f"{table}_part{idx:04d}.parquet")
                    batch_df.write_parquet(out)
                    logger.info("✅ pl.read_database chunk %s written: %s", idx, out)

    logger.info("🎉 Export complete – all tables written")
