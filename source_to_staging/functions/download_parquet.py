from urllib.parse import urlparse
import os
import polars as pl
from sqlalchemy import text
from sqlalchemy.engine import Engine


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

    This function supports both a ConnectorX URI string or a SQLAlchemy Engine
    as the *connection* parameter. If a URI is provided, it will use ConnectorX
    to fetch the data in chunks. If an Engine is provided, it will use
    `polars.read_database` to read the data in batches. Advantage of
    ConnectorX may be that it is more efficient and it also should be able
    to better determine the data types of the columns (SQLAlchemy + Polars
    will sample data to infer types, which may not always be accurate, and
    could encounter errors when a column has mixed types across chunks).

    Note: when connectorx 0.4.4 will be released, code may be simplified,
    as that will introduce a chunking parameter to cx.read_sql.
    """

    # Create destination directory once
    os.makedirs(output_dir, exist_ok=True)

    # ──────────────────────────────────────────────────────────────────────
    # 1 Identify connection mode & SQL dialect
    # ──────────────────────────────────────────────────────────────────────
    if isinstance(connection, str):
        is_uri = True
        uri = connection
        scheme = urlparse(uri).scheme.lower()
    elif isinstance(connection, Engine):
        is_uri = False
        engine = connection
        scheme = engine.dialect.name.lower()
    else:
        raise ValueError(
            "connection must be a SQLAlchemy Engine or a ConnectorX URI string"
        )

    # Helper: qualify table names by schema
    def qualify(tbl: str) -> str:
        if not schema:
            return tbl
        return f"{schema}.{tbl}"

    # Helper: build a paged SQL statement appropriate for the dialect
    def paged_sql(base_select: str, offset: int) -> str:
        if scheme in ("mssql", "sqlserver"):
            return f"{base_select} ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {chunk_size} ROWS ONLY"
        if scheme == "oracle":
            # 12c+ syntax – requires *some* ORDER BY, using literal 1 keeps it deterministic enough
            return f"{base_select} ORDER BY 1 OFFSET {offset} ROWS FETCH NEXT {chunk_size} ROWS ONLY"
        # Default LIMIT/OFFSET path (Postgres, MySQL, SQLite, DuckDB, …)
        return f"{base_select} LIMIT {chunk_size} OFFSET {offset}"

    # ──────────────────────────────────────────────────────────────────────
    # 2 Export loop per table
    # ──────────────────────────────────────────────────────────────────────
    for table in tables:
        qualified = qualify(table)
        base_select = f"SELECT * FROM {qualified}"

        # ── ConnectorX path ───────────────────────────────────
        if is_uri:
            print(f"📥 Dumping table via ConnectorX in pages: {qualified}")
            offset = 0
            part = 0
            while True:
                sql = paged_sql(base_select, offset)
                df = pl.read_database_uri(query=sql, uri=uri)
                if df.is_empty():
                    break  # no more rows

                out = os.path.join(output_dir, f"{table}_part{part:04d}.parquet")
                df.write_parquet(out)
                print(f"✅ ConnectorX chunk {part} written: {out} ({df.height:,} rows)")

                part += 1
                offset += chunk_size

        # ── SQLAlchemy Engine path  ────────────
        else:
            print(f"📥 Dumping table via SQLAlchemy: {qualified}")
            with engine.connect() as conn:
                try:
                    row_count = conn.execute(
                        text(f"SELECT COUNT(*) FROM {qualified}")
                    ).scalar()
                except Exception as err:
                    raise RuntimeError(
                        f"Failed to count rows for {qualified}: {err}"
                    ) from err

                print(f"   (total rows: {row_count:,})")

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
                    print(f"✅ pl.read_database chunk {idx} written: {out}")

    print("🎉 Export complete – all tables written")
