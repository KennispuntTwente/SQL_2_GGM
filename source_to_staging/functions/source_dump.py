# source_to_staging/functions/source_dump.py

import os
import polars as pl
from sqlalchemy import text
from sqlalchemy.engine import Engine

def dump_tables_to_parquet(engine: Engine, tables, output_dir="data", chunk_size=100_000):
    os.makedirs(output_dir, exist_ok=True)

    for table in tables:
        with engine.connect() as conn:
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"📥 Dumpen van tabel: {table} ({row_count:,} rows)")
            result = conn.execution_options(stream_results=True).execute(text(f"SELECT * FROM {table}"))

            chunk_idx = 0
            while True:
                rows = result.fetchmany(chunk_size)
                if not rows:
                    break

                df = pl.from_records(rows, schema=result.keys())
                out_path = os.path.join(output_dir, f"{table}_part{chunk_idx:04d}.parquet")
                df.write_parquet(out_path)
                print(f"✅ Chunk {chunk_idx} geschreven: {out_path}")
                chunk_idx += 1
