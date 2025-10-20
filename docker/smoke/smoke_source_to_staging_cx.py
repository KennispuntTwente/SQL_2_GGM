import os
from sqlalchemy import text

# Use shared helpers directly to avoid side effects from importing main modules
from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value
from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
from utils.database.create_connectorx_uri import create_connectorx_uri
from utils.database.initialize_oracle_client import initialize_oracle_client
from typing import cast


def main():
    # Load single INI passed via command line
    args, cfg = load_single_ini_config()

    # If Oracle thick mode is configured, initialize the client for ConnectorX
    try:
        initialize_oracle_client(
            config_key="SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=cfg
        )
    except Exception as e:
        # Non-fatal: continue; environments without Oracle client will still work for other drivers
        print(f"[smoke-cx] Oracle client init skipped or failed: {e}")

    # Build source ConnectorX URI
    source_cx_uri = create_connectorx_uri(
        driver=cast(
            str,
            get_config_value("SRC_DRIVER", section="database-source", cfg_parser=cfg),
        ),
        username=cast(
            str | None,
            get_config_value("SRC_USERNAME", section="database-source", cfg_parser=cfg),
        ),
        password=cast(
            str | None,
            get_config_value(
                "SRC_PASSWORD",
                section="database-source",
                cfg_parser=cfg,
                print_value=False,
            ),
        ),
        host=cast(
            str | None,
            get_config_value("SRC_HOST", section="database-source", cfg_parser=cfg),
        ),
        port=int(
            str(get_config_value("SRC_PORT", section="database-source", cfg_parser=cfg))
        ),
        database=cast(
            str | None,
            get_config_value("SRC_DB", section="database-source", cfg_parser=cfg),
        ),
    )

    # Build destination engine
    dest_engine = create_sqlalchemy_engine(
        driver=cast(
            str,
            get_config_value(
                "DST_DRIVER", section="database-destination", cfg_parser=cfg
            ),
        ),
        username=cast(
            str,
            get_config_value(
                "DST_USERNAME", section="database-destination", cfg_parser=cfg
            ),
        ),
        password=cast(
            str,
            get_config_value(
                "DST_PASSWORD",
                section="database-destination",
                cfg_parser=cfg,
                print_value=False,
            ),
        ),
        host=cast(
            str,
            get_config_value(
                "DST_HOST", section="database-destination", cfg_parser=cfg
            ),
        ),
        port=int(
            str(
                get_config_value(
                    "DST_PORT", section="database-destination", cfg_parser=cfg
                )
            )
        ),
        database=cast(
            str,
            get_config_value("DST_DB", section="database-destination", cfg_parser=cfg),
        ),
    )

    # Read list of tables
    tables_str = cast(
        str, get_config_value("SRC_TABLES", section="settings", cfg_parser=cfg)
    )
    tables = [t.strip() for t in tables_str.split(",")]

    # Step 1: dump source table to Parquet via ConnectorX
    print("[smoke-cx] Download parquet via ConnectorX…")
    dump_dir = "/app/data"
    os.makedirs(dump_dir, exist_ok=True)
    from source_to_staging.functions.download_parquet import download_parquet

    download_parquet(
        source_cx_uri,  # pass URI string -> ConnectorX code path
        schema=cast(
            str | None,
            get_config_value("SRC_SCHEMA", section="database-source", cfg_parser=cfg),
        ),
        tables=tables,
        output_dir=dump_dir,
        chunk_size=int(
            str(
                get_config_value(
                    "SRC_CHUNK_SIZE",
                    section="settings",
                    cfg_parser=cfg,
                    default=100000,
                )
            )
        ),
    )

    # Step 2: upload into destination
    print("[smoke-cx] Upload parquet…")
    from source_to_staging.functions.upload_parquet import upload_parquet

    upload_parquet(
        dest_engine,
        schema=cast(
            str | None,
            get_config_value(
                "DST_SCHEMA", section="database-destination", cfg_parser=cfg
            ),
        ),
        input_dir=dump_dir,
        cleanup=True,
    )

    # Step 3: verify rows present
    with dest_engine.connect() as conn:
        # demotable will load into table name without schema if DST_SCHEMA empty, otherwise schema.tablename
        dst_schema = cast(
            str | None,
            get_config_value(
                "DST_SCHEMA", section="database-destination", cfg_parser=cfg
            ),
        )
        table = "demotable" if not dst_schema else f"{dst_schema}.demotable"
        cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    print(f"[smoke-cx] Row count in destination table: {cnt}")
    assert cnt and cnt >= 2, "Expected at least two rows in destination"
    print("[smoke-cx] OK")


if __name__ == "__main__":
    main()
