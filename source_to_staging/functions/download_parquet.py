import os
import logging
from typing import Iterable

import polars as pl
import pyarrow as pa
import connectorx as cx
from sqlalchemy import text
from sqlalchemy.engine import Engine

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
        if not schema:
            return tbl
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
                    row_count = conn.execute(
                        text(f"SELECT COUNT(*) FROM {qualified}")
                    ).scalar()
                except Exception as err:
                    raise RuntimeError(
                        f"Failed to count rows for {qualified}: {err}"
                    ) from err

                logger.info("   (total rows: %s)", f"{row_count:,}")

                batches = pl.read_database(
                    query=base_select,
                    connection=conn,
                    iter_batches=True,
                    batch_size=chunk_size,
                    infer_schema_length=chunk_size,
                )
                for idx, batch_df in enumerate(batches):
                    out = os.path.join(output_dir, f"{table}_part{idx:04d}.parquet")
                    batch_df.write_parquet(out)
                    logger.info("✅ pl.read_database chunk %s written: %s", idx, out)

    logger.info("🎉 Export complete – all tables written")
