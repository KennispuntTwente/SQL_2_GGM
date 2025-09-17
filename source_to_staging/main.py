import os
from dotenv import load_dotenv
import oracledb

from utils.config.cli_ini_config import parse_and_load_ini_configs
from utils.config.get_config_value import get_config_value

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
from utils.database.create_connectorx_uri import create_connectorx_uri

from source_to_staging.functions.download_parquet import download_parquet
from source_to_staging.functions.upload_parquet import upload_parquet

# Load environment variables from .env file if .env exists
if os.path.exists("source_to_staging/.env"):
    print("Loading environment variables from .env file...")
    load_dotenv(dotenv_path="source_to_staging/.env")

# Load config parsers
# User can provide --source-config and --destination-config arguments, which may contain
#   paths to INI files with database credentials and settings
# These take priority over environment variables;
#   get_config_value() will first check INI files, then environment variables
args, source_cfg, dest_cfg = parse_and_load_ini_configs()

# Build connection to source database
if get_config_value("SRC_CONNECTORX", section="settings", cfg_parser=source_cfg):
    # Use ConnectorX URI
    source_connection = create_connectorx_uri(
        driver=get_config_value("SRC_DRIVER", cfg_parser=source_cfg),
        username=get_config_value("SRC_USERNAME", cfg_parser=source_cfg),
        password=get_config_value(
            "SRC_PASSWORD", cfg_parser=source_cfg, print_value=False,
            ask_in_command_line=get_config_value("ASK_PASSWORD_IN_CLI", section="settings", cfg_parser=source_cfg, default=False)
        ),
        host=get_config_value("SRC_HOST", cfg_parser=source_cfg),
        port=int(get_config_value("SRC_PORT", cfg_parser=source_cfg)),
        database=get_config_value("SRC_DB", cfg_parser=source_cfg),
    )

    # If SRC_CONNECTORX_ORACLE_CLIENT_PATH is set, use it to try to initialize Oracle client
    oracle_client_path = get_config_value(
        "SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=source_cfg
    )
    if oracle_client_path:
        print(f"Initializing Oracle client with path: {oracle_client_path}")
        oracledb.init_oracle_client(lib_dir=oracle_client_path)
    # If driver contains "oracle", warn user to set SRC_CONNECTORX_ORACLE_CLIENT_PATH
    elif "oracle" in get_config_value("SRC_DRIVER", cfg_parser=source_cfg).lower():
        print(
            "Warning: using CONNECTORX & Oracle, but SRC_CONNECTORX_ORACLE_CLIENT_PATH is not set, "
            "which means ConnectorX may not work correctly with Oracle databases. "
            "Download here: https://www.oracle.com/database/technologies/instant-client/downloads.html; "
            "then unzip, and set SRC_CONNECTORX_ORACLE_CLIENT_PATH to the path of the unzipped folder "
            "(e.g., 'C:\\oracle\\instantclient_21_18') "
        )
else:
    # Use SQLAlchemy engine
    source_connection = create_sqlalchemy_engine(
        driver=get_config_value("SRC_DRIVER", cfg_parser=source_cfg),
        username=get_config_value("SRC_USERNAME", cfg_parser=source_cfg),
        password=get_config_value(
            "SRC_PASSWORD", cfg_parser=source_cfg, print_value=False,
            ask_in_command_line=get_config_value("ASK_PASSWORD_IN_CLI", section="settings", cfg_parser=source_cfg, default=False)
        ),
        host=get_config_value("SRC_HOST", cfg_parser=source_cfg),
        port=int(get_config_value("SRC_PORT", cfg_parser=source_cfg)),
        database=get_config_value("SRC_DB", cfg_parser=source_cfg),
    )

# Build connection to destination database
dest_engine = create_sqlalchemy_engine(
    driver=get_config_value("DST_DRIVER", cfg_parser=dest_cfg),
    username=get_config_value("DST_USERNAME", cfg_parser=dest_cfg),
    password=get_config_value(
        "DST_PASSWORD", cfg_parser=dest_cfg, print_value=False,
        ask_in_command_line=get_config_value("ASK_PASSWORD_IN_CLI", section="settings", cfg_parser=dest_cfg, default=False)
    ),
    host=get_config_value("DST_HOST", cfg_parser=dest_cfg),
    port=int(get_config_value("DST_PORT", cfg_parser=dest_cfg)),
    database=get_config_value("DST_DB", cfg_parser=dest_cfg),
)

# Read which tables to dump from source database
tables_str = get_config_value("SRC_TABLES", section="settings", cfg_parser=source_cfg)
tables = [t.strip() for t in tables_str.split(",")]

# Step 1/2: Dump tables from source to parquet files
download_parquet(
    source_connection,
    schema=get_config_value("SRC_SCHEMA", cfg_parser=source_cfg),
    tables=tables,
    output_dir="data",
    chunk_size=int(
        get_config_value(
            "SRC_CHUNK_SIZE", section="settings", cfg_parser=source_cfg, default=100_000
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
