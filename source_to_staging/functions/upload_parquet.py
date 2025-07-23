# source_to_staging/functions/upload_parquet.py

import os
import polars as pl

def upload_parquet_to_db(engine, schema, input_dir="data"):
    """
    Uploads Parquet files from a folder into the destination DB.
    """
    for file in os.listdir(input_dir):
        if not file.endswith(".parquet"):
            continue

        table_name = file.replace(".parquet", "")
        parquet_path = os.path.join(input_dir, file)

        print(f"📦 Importeren van {parquet_path} naar tabel {schema}.{table_name}")
        df = pl.read_parquet(parquet_path)

        df.write_database(
            table_name=f"{schema}.{table_name}",
            connection=engine,
            if_table_exists="replace",
            engine="sqlalchemy"
        )
        print(f"✅ Ingeladen: {table_name}")

