# source_to_staging/functions/upload_parquet.py

import os
import polars as pl
from collections import defaultdict
from sqlalchemy import text

def upload_parquet_to_db(
    engine, schema, input_dir="data",
    cleanup=True
):
    """
    Uploads (possibly chunked) Parquet files into destination DB.
    Creates schema if it doesn't exist.
    """
    # Create schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        conn.commit()

    # Group files by base table name (before _partXXXX or .parquet)
    grouped_files = defaultdict(list)
    for file in os.listdir(input_dir):
        if file.endswith(".parquet"):
            base = file.split("_part")[0].replace(".parquet", "")
            grouped_files[base].append(file)

    for table_name, files in grouped_files.items():
        print(f"📦 Uploading {len(files)} part(s) to table {schema}.{table_name}")
        full_table_name = f"{schema}.{table_name}"

        for idx, file in enumerate(sorted(files)):
            parquet_path = os.path.join(input_dir, file)
            print(f"🔹 Processing {parquet_path}")
            df = pl.read_parquet(parquet_path)

            df.write_database(
                table_name=full_table_name,
                connection=engine,
                if_table_exists="replace" if idx == 0 else "append",
                engine="sqlalchemy"
            )
        print(f"✅ Ingeladen: {table_name}")

        if cleanup:
            for file in files:
                os.remove(os.path.join(input_dir, file))
            print(f"🗑️ Schoonmaak voltooid voor {table_name}")
