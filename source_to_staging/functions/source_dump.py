import os
import polars as pl
from sqlalchemy import text
from sqlalchemy.engine import Engine


def dump_tables_to_parquet(
    engine: Engine,
    tables,
    output_dir: str = "data",
    chunk_size: int = 100_000,
    schema: str = None
):
    """
    Dumps specified tables from the given database engine to Parquet files in chunks.

    :param engine: SQLAlchemy Engine for source database
    :param tables: List of table names (unqualified); will prefix with schema if provided
    :param output_dir: Directory to write Parquet files
    :param chunk_size: Number of rows per Parquet file chunk
    :param schema: Optional schema (or owner) to qualify table names
    """
    os.makedirs(output_dir, exist_ok=True)
    dialect = engine.dialect.name.lower()

    # Helper to qualify table names per dialect
    def qualify(table_name: str) -> str:
        if schema:
            # Oracle uses uppercase for schema and tables by default
            if dialect == "oracle":
                return f"{schema.upper()}.{table_name.upper()}"
            # MySQL/MariaDB treat schema as database
            if dialect in ("mysql", "mariadb"):  # database already in engine.url
                return table_name
            # Other SQL dialects support schema.table
            return f"{schema}.{table_name}"
        return table_name

    for table in tables:
        qualified = qualify(table)
        with engine.connect() as conn:
            # Count rows
            count_sql = text(f"SELECT COUNT(*) FROM {qualified}")
            try:
                row_count = conn.execute(count_sql).scalar()
            except Exception as e:
                raise RuntimeError(f"Failed to count rows for {qualified}: {e}")
            print(f"📥 Dumping table: {qualified} ({row_count:,} rows)")

            # Stream and dump in chunks
            select_sql = text(f"SELECT * FROM {qualified}")
            result = conn.execution_options(stream_results=True).execute(select_sql)

            chunk_idx = 0
            while True:
                rows = result.fetchmany(chunk_size)
                if not rows:
                    break

                df = pl.from_records(rows, schema=result.keys())
                out_path = os.path.join(output_dir, f"{table}_part{chunk_idx:04d}.parquet")
                df.write_parquet(out_path)
                print(f"✅ Chunk {chunk_idx} written: {out_path}")
                chunk_idx += 1
