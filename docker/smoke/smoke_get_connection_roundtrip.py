import os
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection
from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet


def main():
    # Which DB to test can be picked via env, default postgres
    db_type = os.getenv("SMOKE_DB", "postgres").lower()
    username = os.getenv("SMOKE_USER", "sa")
    password = os.getenv("SMOKE_PASS", "S3cureP@ssw0rd!23243")
    port = int(os.getenv("SMOKE_PORT", "5433" if db_type == "postgres" else "1434"))

    dump_dir = "/app/data"
    os.makedirs(dump_dir, exist_ok=True)

    # Start source DB container and create a tiny table
    src_engine = get_connection(
        db_type=db_type,
        db_name="smoke_src",
        user=username,
        password=password,
        port=port,
        force_refresh=True,
        sql_folder=None,
        print_tables=False,
    )
    with src_engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS demotable"))
        conn.execute(text("CREATE TABLE demotable (id INT PRIMARY KEY, val VARCHAR(50))"))
        conn.execute(text("INSERT INTO demotable (id, val) VALUES (1, 'foo'), (2, 'bar')"))

    # Dump to parquet
    download_parquet(src_engine, ["demotable"], output_dir=dump_dir)

    # Start destination DB container
    dst_engine = get_connection(
        db_type=db_type,
        db_name="smoke_dst",
        user=username,
        password=password,
        port=port,
        force_refresh=True,
        sql_folder=None,
        print_tables=False,
    )

    # Upload parquet
    upload_parquet(dst_engine, input_dir=dump_dir, cleanup=True)

    # Validate
    with dst_engine.connect() as conn:
        cnt = conn.execute(text("SELECT COUNT(*) FROM demotable")).scalar()
    print(f"[smoke-get-conn] Count in destination: {cnt}")
    assert cnt == 2
    print("[smoke-get-conn] OK")


if __name__ == "__main__":
    main()
