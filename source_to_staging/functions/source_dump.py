# source_to_staging/functions/source_dump.py

import os
import polars as pl
from sqlalchemy import text

def dump_tables_to_parquet(engine, tables, output_dir="data"):
    """
    Dumps specified tables from a source DB to Parquet files.
    """
    os.makedirs(output_dir, exist_ok=True)

    for table in tables:
        print(f"📥 Dumpen van tabel: {table}")
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table}"))
            df = pl.from_records(result.fetchall(), schema=result.keys())
            out_path = os.path.join(output_dir, f"{table}.parquet")
            df.write_parquet(out_path)
            print(f"✅ Geslaagd: {out_path}")

