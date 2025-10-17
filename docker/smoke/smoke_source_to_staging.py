import os
from sqlalchemy import text

# Use shared helpers directly to avoid side effects from importing main modules
from utils.config.cli_ini_config import parse_and_load_ini_configs as load_two
from utils.config.get_config_value import get_config_value
from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine


def main():
    # Load INI configs passed via command line
    args, source_cfg, dest_cfg = load_two()

    # Build source connection (SQLAlchemy engine)
    source_connection = create_sqlalchemy_engine(
        driver=get_config_value("SRC_DRIVER", cfg_parser=source_cfg),
        username=get_config_value("SRC_USERNAME", cfg_parser=source_cfg),
        password=get_config_value("SRC_PASSWORD", cfg_parser=source_cfg, print_value=False),
        host=get_config_value("SRC_HOST", cfg_parser=source_cfg),
        port=int(get_config_value("SRC_PORT", cfg_parser=source_cfg)),
        database=get_config_value("SRC_DB", cfg_parser=source_cfg),
    )

    # Build destination engine
    dest_engine = create_sqlalchemy_engine(
        driver=get_config_value("DST_DRIVER", cfg_parser=dest_cfg),
        username=get_config_value("DST_USERNAME", cfg_parser=dest_cfg),
        password=get_config_value("DST_PASSWORD", cfg_parser=dest_cfg, print_value=False),
        host=get_config_value("DST_HOST", cfg_parser=dest_cfg),
        port=int(get_config_value("DST_PORT", cfg_parser=dest_cfg)),
        database=get_config_value("DST_DB", cfg_parser=dest_cfg),
    )

    # Read list of tables
    tables_str = get_config_value("SRC_TABLES", section="settings", cfg_parser=source_cfg)
    tables = [t.strip() for t in tables_str.split(",")]

    # Step 1: dump source table to Parquet
    print("[smoke] Download parquet…")
    dump_dir = "/app/data"
    os.makedirs(dump_dir, exist_ok=True)
    from source_to_staging.functions.download_parquet import download_parquet
    download_parquet(
        source_connection,
        schema=get_config_value("SRC_SCHEMA", cfg_parser=source_cfg),
        tables=tables,
        output_dir=dump_dir,
        chunk_size=int(get_config_value("SRC_CHUNK_SIZE", section="settings", cfg_parser=source_cfg, default=100000)),
    )

    # Step 2: upload into destination
    print("[smoke] Upload parquet…")
    from source_to_staging.functions.upload_parquet import upload_parquet
    upload_parquet(
        dest_engine,
        schema=get_config_value("DST_SCHEMA", cfg_parser=dest_cfg),
        input_dir=dump_dir,
        cleanup=True,
    )

    # Step 3: verify rows present
    with dest_engine.connect() as conn:
        # demotable will load into table name without schema if DST_SCHEMA empty, otherwise schema.tablename
        table = "demotable" if not get_config_value("DST_SCHEMA", cfg_parser=dest_cfg) else f"{get_config_value('DST_SCHEMA', cfg_parser=dest_cfg)}.demotable"
        cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    print(f"[smoke] Row count in destination table: {cnt}")
    assert cnt and cnt >= 2, "Expected at least two rows in destination"
    print("[smoke] OK")


if __name__ == "__main__":
    main()
