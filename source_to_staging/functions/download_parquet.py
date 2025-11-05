import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Iterable

import polars as pl
import pyarrow as pa
import connectorx as cx
from sqlalchemy import text
from sqlalchemy.engine import Engine
from utils.database.identifiers import quote_fqn

logger = logging.getLogger("source_to_staging.download_parquet")


def download_parquet(
    connection,
    tables,
    output_dir: str = "data",
    chunk_size: int = 100_000,
    schema: str | None = None,
    *,
    row_limit: int | None = None,
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

    # Track files created during this run and emit a manifest so the upload step can
    # limit itself strictly to these files (avoids picking up leftovers from previous runs).
    run_id = uuid.uuid4().hex
    created_files: list[str] = []  # file names relative to output_dir

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
        if not schema:
            # Without a schema, rely on the base identifier quoting only if/when needed
            return tbl
        # We don't have an Engine for the URI path, but later we determine scheme
        # and will rebuild the SELECT accordingly; here, just join parts plainly.
        return f"{schema}.{tbl}"

    # ──────────────────────────────────────────────────────────────────────
    # 2 Export loop per table
    # ──────────────────────────────────────────────────────────────────────
    for table in tables:
        qualified = qualify(table)
        base_select = f"SELECT * FROM {qualified}"

        # ── ConnectorX path ───────────────────────────────────
        if is_uri:
            logger.info("📥 Dumping table via ConnectorX (arrow_stream): %s", qualified)
            # Apply optional row limit by dialect when using URI
            if row_limit and row_limit > 0:
                # Determine base scheme; handle driver suffix like postgresql+psycopg2
                scheme = uri.split("://", 1)[0].lower()
                scheme = scheme.split("+", 1)[0]
                if scheme in ("postgres", "postgresql", "mysql", "sqlite", "redshift"):
                    base_select = f"{base_select} LIMIT {row_limit}"
                elif scheme in ("mssql", "sqlserver", "sql server"):
                    base_select = f"SELECT TOP ({row_limit}) * FROM {qualified}"
                elif scheme == "oracle":
                    base_select = f"{base_select} FETCH FIRST {row_limit} ROWS ONLY"
                else:
                    logger.warning("Unknown URI scheme %r – skipping ROW_LIMIT for %s", scheme, qualified)
            # Rebuild the FROM target using dialect-aware quoting for the scheme
            scheme = uri.split("://", 1)[0].lower()
            scheme = scheme.split("+", 1)[0]
            try:
                quoted_target = quote_fqn(scheme, [schema, table]) if schema else quote_fqn(scheme, [table])
            except Exception:
                # Fallback: leave unquoted
                quoted_target = qualified
            base_select = f"SELECT * FROM {quoted_target}" if base_select.startswith("SELECT * FROM ") else base_select.replace(qualified, quoted_target)
            # Stream arrow record batches directly from the source using ConnectorX
            reader_or_iter: Iterable
            reader_or_iter = cx.read_sql(
                uri,
                base_select,
                return_type="arrow_stream",
                batch_size=chunk_size,
            )

            # The return can be a RecordBatchReader or an iterable of RecordBatch
            try:
                iterator = iter(reader_or_iter)  # type: ignore[arg-type]
            except TypeError:
                # If it's a RecordBatchReader, convert to iterator via .read_next_batch()
                reader = reader_or_iter  # type: ignore[assignment]

                class _ReaderIter:
                    def __init__(self, r):
                        self._r = r

                    def __iter__(self):
                        return self

                    def __next__(self):
                        batch = self._r.read_next_batch()
                        # Stop only when the reader returns None (end of stream).
                        # Empty batches (num_rows == 0) should be yielded so the
                        # outer loop can skip them without terminating iteration.
                        if batch is None:
                            raise StopIteration
                        return batch

                iterator = _ReaderIter(reader)

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
                created_files.append(os.path.basename(out))
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
                logger.info("   (no rows)")

        # ── SQLAlchemy Engine path  ────────────
        else:
            logger.info("📥 Dumping table via SQLAlchemy: %s", qualified)
            with engine.connect() as conn:
                try:
                    qname = quote_fqn(engine, [schema, table]) if schema else quote_fqn(engine, [table])
                    row_count = conn.execute(text(f"SELECT COUNT(*) FROM {qname}")).scalar()
                except Exception as err:
                    raise RuntimeError(
                        f"Failed to count rows for {qualified}: {err}"
                    ) from err

                logger.info("   (total rows: %s)", f"{row_count:,}")

                # Apply optional row limit based on SQLAlchemy engine dialect
                # Ensure base_select uses quoted target
                q_target = quote_fqn(engine, [schema, table]) if schema else quote_fqn(engine, [table])
                limited_select = f"SELECT * FROM {q_target}"
                if row_limit and row_limit > 0:
                    dname = engine.dialect.name.lower()
                    if dname in ("postgresql", "mysql", "sqlite"):
                        limited_select = f"{limited_select} LIMIT {row_limit}"
                    elif dname in ("mssql", "sql server"):
                        limited_select = f"SELECT TOP ({row_limit}) * FROM {q_target}"
                    elif dname == "oracle":
                        limited_select = f"{limited_select} FETCH FIRST {row_limit} ROWS ONLY"
                    else:
                        logger.warning("Unknown dialect %r – skipping ROW_LIMIT for %s", dname, qualified)

                batches = pl.read_database(
                    query=limited_select,
                    connection=conn,
                    iter_batches=True,
                    batch_size=chunk_size,
                    infer_schema_length=chunk_size,
                )
                for idx, batch_df in enumerate(batches):
                    out = os.path.join(output_dir, f"{table}_part{idx:04d}.parquet")
                    batch_df.write_parquet(out)
                    created_files.append(os.path.basename(out))
                    logger.info("✅ pl.read_database chunk %s written: %s", idx, out)

    # Write a manifest for this run so upload can be restricted to the current files only
    manifest_path = os.path.join(
        output_dir, f".ggmpilot_parquet_manifest_{run_id}.json"
    )
    try:
        manifest = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "output_dir": os.path.abspath(output_dir),
            "files": created_files,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        logger.info(
            "🧾 Manifest written: %s (%s files)", manifest_path, len(created_files)
        )
    except Exception as e:
        logger.warning("Failed to write manifest %s: %s", manifest_path, e)
        manifest_path = None  # type: ignore[assignment]

    logger.info("🎉 Export complete – all tables written")

    # Return the manifest path for callers that wish to limit subsequent upload
    return manifest_path
