import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

from source_to_staging.functions.parse_args_and_load_parsers import parse_args_and_load_parsers
from source_to_staging.functions.get_config_value import get_config_value
from source_to_staging.functions.create_database_url import create_database_url
from source_to_staging.functions.source_dump import dump_tables_to_parquet
from source_to_staging.functions.upload_parquet import upload_parquet_to_db

# Load environment variables from .env file if .env exists
if os.path.exists("source_to_staging/.env"):
    print("Loading environment variables from .env file...")
    load_dotenv(dotenv_path="source_to_staging/.env")

# Load config parsers
# User can provide --source-config and --destination-config arguments, which may contain
#   paths to INI files with database credentials and settings
# These take priority over environment variables;
#   get_config_value() will first check INI files, then environment variables
args, source_cfg, dest_cfg = parse_args_and_load_parsers()

# Build connection to source database
source_url = create_database_url(
    driver = get_config_value("SRC_DRIVER", cfg_parser=source_cfg),
    username = get_config_value("SRC_USERNAME", cfg_parser=source_cfg),
    password = get_config_value("SRC_PASSWORD", cfg_parser=source_cfg),
    host = get_config_value("SRC_HOST", cfg_parser=source_cfg),
    port = int(get_config_value("SRC_PORT", cfg_parser=source_cfg)),
    database = get_config_value("SRC_DB", cfg_parser=source_cfg)
)
source_engine = create_engine(source_url)

# Build connection to destination database
dest_url = create_database_url(
    driver = get_config_value("DST_DRIVER", cfg_parser=dest_cfg),
    username = get_config_value("DST_USERNAME", cfg_parser=dest_cfg),
    password = get_config_value("DST_PASSWORD", cfg_parser=dest_cfg),
    host = get_config_value("DST_HOST", cfg_parser=dest_cfg),
    port = int(get_config_value("DST_PORT", cfg_parser=dest_cfg)),
    database = get_config_value("DST_DB", cfg_parser=dest_cfg)
)
dest_engine = create_engine(dest_url)

# Read which tables to dump from source database
tables_str = get_config_value("SRC_TABLES", section="settings", cfg_parser=source_cfg)
tables = [t.strip() for t in tables_str.split(",")]

# Step 1/2: Dump tables from source to parquet files
dump_tables_to_parquet(
    source_engine,
    schema = get_config_value("SRC_SCHEMA", cfg_parser=source_cfg),
    tables = tables,
    output_dir = "data"
)

# Step 2/2: Upload parquet files into destination database
upload_parquet_to_db(
    dest_engine,
    schema = get_config_value("DST_SCHEMA", cfg_parser=dest_cfg),
    input_dir = "data",
    cleanup = True
)
