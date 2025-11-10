import os
import logging
from typing import cast
from dotenv import load_dotenv

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value

from source_to_staging.functions.engine_loaders import (
    load_source_connection,
    load_destination_engine,
)
from utils.logging.setup_logging import setup_logging

# Load environment variables from .env file if .env exists
if os.path.exists("source_to_staging/.env"):
    load_dotenv(dotenv_path="source_to_staging/.env")
    logging.getLogger(__name__).info(
        "Loaded environment variables from source_to_staging/.env"
    )

# Load single config parser
# User can provide --config argument pointing to a single INI with sections
#   [database-source], [database-destination], [settings], [logging]
# INI takes priority over environment variables
args, cfg = load_single_ini_config(prog_desc="Run source to staging data migration")

# Configure logging (console + optional file via INI/env)
setup_logging(app_name="source_to_staging", cfg_parsers=[cfg])
log = logging.getLogger("source_to_staging")

# Determine transfer mode
transfer_mode = cast(
    str,
    get_config_value(
        "TRANSFER_MODE",
        section="settings",
        cfg_parser=cfg,
        default="SQLALCHEMY_DIRECT",
    ),
)

valid_modes = {"SQLALCHEMY_DIRECT", "CONNECTORX_DUMP", "SQLALCHEMY_DUMP"}
if transfer_mode not in valid_modes:
    raise ValueError(
        f"TRANSFER_MODE must be one of {sorted(valid_modes)}; got {transfer_mode!r}"
    )

source_connection = load_source_connection(cfg, transfer_mode)

dest_engine = load_destination_engine(cfg)

# Read which tables to dump from source database
tables_str = cast(
    str | None,
    get_config_value("SRC_TABLES", section="settings", cfg_parser=cfg),
)
if tables_str is None:
    tables_str = ""
raw_tables = [t.strip() for t in tables_str.split(",")]
# Validate SRC_TABLES after splitting: must not be empty and must not contain blanks
tables = [t for t in raw_tables if t]
if not tables or len(tables) != len(raw_tables):
    raise ValueError(
        "SRC_TABLES must be a comma-separated list of non-empty table names; got: "
        f"{tables_str!r}"
    )

# Optional developer row limit: limit rows read per source table (0/blank disables)
row_limit = get_config_value(
    "ROW_LIMIT",
    section="settings",
    cfg_parser=cfg,
    cast_type=int,
    allow_none_if_cast_fails=True,
)

if transfer_mode == "SQLALCHEMY_DIRECT":
    # Direct SQLAlchemy-to-SQLAlchemy chunked copy
    from source_to_staging.functions.direct_transfer import direct_transfer

    # Configure destination write mode (replace | truncate | append)
    write_mode = cast(
        str,
        get_config_value(
            "WRITE_MODE",
            section="settings",
            cfg_parser=cfg,
            default="replace",
        ),
    ).lower()
    if write_mode not in {"replace", "truncate", "append"}:
        raise ValueError(
            f"WRITE_MODE must be one of ['replace','truncate','append']; got {write_mode!r}"
        )

    # Optional admin database override (for managed Postgres/MSSQL where default admin DB isn't accessible)
    admin_db_override = cast(
        str | None,
        get_config_value(
            "DST_ADMIN_DB",
            section="database-destination",
            cfg_parser=cfg,
        ),
    )

    direct_transfer(
        source_engine=source_connection,  # type: ignore[arg-type]
        dest_engine=dest_engine,
        tables=tables,
        source_schema=cast(
            str | None,
            get_config_value("SRC_SCHEMA", section="database-source", cfg_parser=cfg),
        ),
        dest_schema=cast(
            str | None,
            get_config_value(
                "DST_SCHEMA", section="database-destination", cfg_parser=cfg
            ),
        ),
        chunk_size=get_config_value(
            "SRC_CHUNK_SIZE",
            section="settings",
            cfg_parser=cfg,
            default=100_000,
            cast_type=int,
        ),
        lowercase_columns=True,
        write_mode=write_mode,
        row_limit=row_limit,
        log_row_count=get_config_value(
            "LOG_ROW_COUNT",
            section="settings",
            cfg_parser=cfg,
            default=True,
            cast_type=bool,
        ),
        # Optional retry/backoff tuning for direct transfer inserts
        max_retries=get_config_value(
            "DIRECT_MAX_RETRIES",
            section="settings",
            cfg_parser=cfg,
            default=3,
            cast_type=int,
        ),
        backoff_base_seconds=get_config_value(
            "DIRECT_BACKOFF_BASE_SECONDS",
            section="settings",
            cfg_parser=cfg,
            default=0.5,
            cast_type=float,
        ),
        backoff_max_seconds=get_config_value(
            "DIRECT_BACKOFF_MAX_SECONDS",
            section="settings",
            cfg_parser=cfg,
            default=8.0,
            cast_type=float,
        ),
        admin_database=admin_db_override,
    )
else:
    # Step 1/2: Dump tables from source to parquet files
    from source_to_staging.functions.download_parquet import download_parquet

    manifest_path = download_parquet(
        source_connection,
        schema=cast(
            str | None,
            get_config_value("SRC_SCHEMA", section="database-source", cfg_parser=cfg),
        ),
        tables=tables,
        output_dir="data",
        chunk_size=get_config_value(
            "SRC_CHUNK_SIZE",
            section="settings",
            cfg_parser=cfg,
            default=100_000,
            cast_type=int,
        ),
        row_limit=row_limit,
        log_row_count=get_config_value(
            "LOG_ROW_COUNT",
            section="settings",
            cfg_parser=cfg,
            default=True,
            cast_type=bool,
        ),
    )

    # Step 2/2: Upload parquet files into destination database
    from source_to_staging.functions.upload_parquet import upload_parquet

    # Configure destination write mode for parquet upload as well
    write_mode = cast(
        str,
        get_config_value(
            "WRITE_MODE",
            section="settings",
            cfg_parser=cfg,
            default="replace",
        ),
    ).lower()
    if write_mode not in {"replace", "truncate", "append"}:
        raise ValueError(
            f"WRITE_MODE must be one of ['replace','truncate','append']; got {write_mode!r}"
        )

    # Optional admin database override (for managed Postgres/MSSQL where default admin DB isn't accessible)
    admin_db_override = cast(
        str | None,
        get_config_value(
            "DST_ADMIN_DB",
            section="database-destination",
            cfg_parser=cfg,
        ),
    )

    upload_parquet(
        dest_engine,
        schema=get_config_value(
            "DST_SCHEMA", section="database-destination", cfg_parser=cfg
        ),
        input_dir="data",
        cleanup=get_config_value(
            "CLEANUP_PARQUET_FILES",
            section="settings",
            cfg_parser=cfg,
            default=True,
            cast_type=bool,
        ),
        manifest_path=manifest_path,
        write_mode=write_mode,
        admin_database=admin_db_override,
    )
