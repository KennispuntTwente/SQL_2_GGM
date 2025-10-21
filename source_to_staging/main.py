import os
import logging
from typing import Optional, cast
from dotenv import load_dotenv
import oracledb

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
from utils.database.create_connectorx_uri import create_connectorx_uri

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
from source_to_staging.functions.direct_transfer import direct_transfer
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

# Build connection to source database
src_driver = cast(
    str, get_config_value("SRC_DRIVER", section="database-source", cfg_parser=cfg)
)
src_username = cast(
    Optional[str],
    get_config_value("SRC_USERNAME", section="database-source", cfg_parser=cfg),
)
src_password = cast(
    Optional[str],
    get_config_value(
        "SRC_PASSWORD",
        section="database-source",
        cfg_parser=cfg,
        print_value=False,
        ask_in_command_line=bool(
            get_config_value(
                "ASK_PASSWORD_IN_CLI",
                section="settings",
                cfg_parser=cfg,
                default=False,
            )
        ),
    ),
)
src_host = cast(
    Optional[str],
    get_config_value("SRC_HOST", section="database-source", cfg_parser=cfg),
)
src_port = int(
    str(get_config_value("SRC_PORT", section="database-source", cfg_parser=cfg))
)
src_db = cast(
    Optional[str], get_config_value("SRC_DB", section="database-source", cfg_parser=cfg)
)

if transfer_mode == "SQLALCHEMY_DIRECT":
    # Force SQLAlchemy engine for direct copy mode
    source_connection = create_sqlalchemy_engine(
        driver=src_driver,
        username=cast(str, src_username),
        password=cast(str, src_password),
        host=cast(str, src_host),
        port=src_port,
        database=cast(str, src_db),
    )
elif transfer_mode == "CONNECTORX_DUMP":
    # Use ConnectorX URI
    source_connection = create_connectorx_uri(
        driver=src_driver,
        username=src_username,
        password=src_password,
        host=src_host,
        port=src_port,
        database=src_db,
        alias=bool(
            get_config_value(
                "SRC_ORACLE_TNS_ALIAS",
                section="settings",
                cfg_parser=cfg,
                default=False,
            )
        ),
    )

    # If SRC_CONNECTORX_ORACLE_CLIENT_PATH is set, use it to try to initialize Oracle client
    oracle_client_path = get_config_value(
        "SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=cfg
    )
    if oracle_client_path:
        log.info(f"Initializing Oracle client with path: {oracle_client_path}")
        oracledb.init_oracle_client(lib_dir=oracle_client_path)
    # If driver contains "oracle", warn user to set SRC_CONNECTORX_ORACLE_CLIENT_PATH
    elif "oracle" in src_driver.lower():
        log.warning(
            "Using CONNECTORX & Oracle, but SRC_CONNECTORX_ORACLE_CLIENT_PATH is not set; "
            "ConnectorX may not work correctly with Oracle. Download Instant Client and set the path "
            "(e.g., C:\\oracle\\instantclient_21_18)."
        )
else:  # SQLALCHEMY_DUMP
    # Use SQLAlchemy engine
    source_connection = create_sqlalchemy_engine(
        driver=src_driver,
        username=cast(str, src_username),
        password=cast(str, src_password),
        host=cast(str, src_host),
        port=src_port,
        database=cast(str, src_db),
    )

# Build connection to destination database
dest_engine = create_sqlalchemy_engine(
    driver=cast(
        str,
        get_config_value("DST_DRIVER", section="database-destination", cfg_parser=cfg),
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
            ask_in_command_line=bool(
                get_config_value(
                    "ASK_PASSWORD_IN_CLI",
                    section="settings",
                    cfg_parser=cfg,
                    default=False,
                )
            ),
        ),
    ),
    host=cast(
        str,
        get_config_value("DST_HOST", section="database-destination", cfg_parser=cfg),
    ),
    port=int(
        str(
            get_config_value("DST_PORT", section="database-destination", cfg_parser=cfg)
        )
    ),
    database=cast(
        str, get_config_value("DST_DB", section="database-destination", cfg_parser=cfg)
    ),
)

# Read which tables to dump from source database
tables_str = cast(
    str, get_config_value("SRC_TABLES", section="settings", cfg_parser=cfg)
)
tables = [t.strip() for t in tables_str.split(",")]

if transfer_mode == "SQLALCHEMY_DIRECT":
    # Direct SQLAlchemy-to-SQLAlchemy chunked copy
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
        chunk_size=int(
            str(
                get_config_value(
                    "SRC_CHUNK_SIZE",
                    section="settings",
                    cfg_parser=cfg,
                    default=100_000,
                )
            )
        ),
        lowercase_columns=True,
        write_mode="replace",
    )
else:
    # Step 1/2: Dump tables from source to parquet files
    download_parquet(
        source_connection,
        schema=cast(
            str | None,
            get_config_value("SRC_SCHEMA", section="database-source", cfg_parser=cfg),
        ),
        tables=tables,
        output_dir="data",
        chunk_size=int(
            str(
                get_config_value(
                    "SRC_CHUNK_SIZE",
                    section="settings",
                    cfg_parser=cfg,
                    default=100_000,
                )
            )
        ),
    )

    # Step 2/2: Upload parquet files into destination database
    upload_parquet(
        dest_engine,
        schema=get_config_value(
            "DST_SCHEMA", section="database-destination", cfg_parser=cfg
        ),
        input_dir="data",
        cleanup=get_config_value(
            "CLEANUP_PARQUET_FILES", section="settings", cfg_parser=cfg, default=True
        ),
    )
