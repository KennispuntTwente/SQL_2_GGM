import os
import logging
from typing import Optional, cast
from dotenv import load_dotenv
import oracledb

from utils.config.cli_ini_config import parse_and_load_ini_configs
from utils.config.get_config_value import get_config_value

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
from utils.database.create_connectorx_uri import create_connectorx_uri

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet
from utils.logging.setup_logging import setup_logging

# Load environment variables from .env file if .env exists
if os.path.exists("source_to_staging/.env"):
    load_dotenv(dotenv_path="source_to_staging/.env")
    logging.getLogger(__name__).info(
        "Loaded environment variables from source_to_staging/.env"
    )

# Load config parsers
# User can provide --source-config and --destination-config arguments, which may contain
#   paths to INI files with database credentials and settings
# These take priority over environment variables;
#   get_config_value() will first check INI files, then environment variables
args, source_cfg, dest_cfg = parse_and_load_ini_configs()

# Configure logging (console + optional file via INI/env)
setup_logging(app_name="source_to_staging", cfg_parsers=[source_cfg, dest_cfg])
log = logging.getLogger("source_to_staging")

# Build connection to source database
use_cx = bool(
    get_config_value(
        "SRC_CONNECTORX", section="settings", cfg_parser=source_cfg, default=False
    )
)
src_driver = cast(str, get_config_value("SRC_DRIVER", cfg_parser=source_cfg))
src_username = cast(
    Optional[str], get_config_value("SRC_USERNAME", cfg_parser=source_cfg)
)
src_password = cast(
    Optional[str],
    get_config_value(
        "SRC_PASSWORD",
        cfg_parser=source_cfg,
        print_value=False,
        ask_in_command_line=bool(
            get_config_value(
                "ASK_PASSWORD_IN_CLI",
                section="settings",
                cfg_parser=source_cfg,
                default=False,
            )
        ),
    ),
)
src_host = cast(Optional[str], get_config_value("SRC_HOST", cfg_parser=source_cfg))
src_port = int(str(get_config_value("SRC_PORT", cfg_parser=source_cfg)))
src_db = cast(Optional[str], get_config_value("SRC_DB", cfg_parser=source_cfg))

if use_cx:
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
                cfg_parser=source_cfg,
                default=False,
            )
        ),
    )

    # If SRC_CONNECTORX_ORACLE_CLIENT_PATH is set, use it to try to initialize Oracle client
    oracle_client_path = get_config_value(
        "SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=source_cfg
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
else:
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
    driver=cast(str, get_config_value("DST_DRIVER", cfg_parser=dest_cfg)),
    username=cast(str, get_config_value("DST_USERNAME", cfg_parser=dest_cfg)),
    password=cast(
        str,
        get_config_value(
            "DST_PASSWORD",
            cfg_parser=dest_cfg,
            print_value=False,
            ask_in_command_line=bool(
                get_config_value(
                    "ASK_PASSWORD_IN_CLI",
                    section="settings",
                    cfg_parser=dest_cfg,
                    default=False,
                )
            ),
        ),
    ),
    host=cast(str, get_config_value("DST_HOST", cfg_parser=dest_cfg)),
    port=int(str(get_config_value("DST_PORT", cfg_parser=dest_cfg))),
    database=cast(str, get_config_value("DST_DB", cfg_parser=dest_cfg)),
)

# Read which tables to dump from source database
tables_str = cast(
    str, get_config_value("SRC_TABLES", section="settings", cfg_parser=source_cfg)
)
tables = [t.strip() for t in tables_str.split(",")]

# Step 1/2: Dump tables from source to parquet files
download_parquet(
    source_connection,
    schema=cast(str | None, get_config_value("SRC_SCHEMA", cfg_parser=source_cfg)),
    tables=tables,
    output_dir="data",
    chunk_size=int(
        str(
            get_config_value(
                "SRC_CHUNK_SIZE",
                section="settings",
                cfg_parser=source_cfg,
                default=100_000,
            )
        )
    ),
)

# Step 2/2: Upload parquet files into destination database
upload_parquet(
    dest_engine,
    schema=get_config_value("DST_SCHEMA", cfg_parser=dest_cfg),
    input_dir="data",
    cleanup=True,
)
