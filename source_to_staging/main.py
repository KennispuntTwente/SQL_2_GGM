import os
import argparse
import sys
from dotenv import load_dotenv
import configparser
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

from source_to_staging.functions.source_dump import dump_tables_to_parquet
from source_to_staging.functions.upload_parquet import upload_parquet_to_db


# Load environment variables from .env file
load_dotenv(dotenv_path="source_to_staging/.env")

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run source to staging data migration')
parser.add_argument(
    '--source-config', '-s', 
    help='Settings for source (credentials, tables to extract) in INI format (optional - will use .env if not provided)'
)
parser.add_argument(
    '--destination-config', '-t', 
    help='Settings for destination (credentials, database, schema, etc.) in INI format (optional - will use .env if not provided)'
)

# Handle interactive vs command-line execution
if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
    args = parser.parse_args([])
else:
    args = parser.parse_args()

# Read config files if provided
source_cfg = configparser.ConfigParser()
if args.source_config:
    source_cfg.read(args.source_config)

dest_cfg = configparser.ConfigParser()
if args.destination_config:
    dest_cfg.read(args.destination_config)


def get_config_value(key, section="database", cfg_parser=None):
    """
    Get configuration value from INI file if present, otherwise from environment variable.
    """
    # Try INI first
    if cfg_parser and cfg_parser.has_option(section, key):
        return cfg_parser.get(section, key)

    # Fallback to environment variable
    env_value = os.environ.get(key)
    if env_value is None:
        raise ValueError(f"Configuration key '{key}' not found in config file or environment variables")
    return env_value

# Get tables list from source config (or env fallback)
tables_str = get_config_value("SRC_TABLES", section="settings", cfg_parser=source_cfg)
tables = [t.strip() for t in tables_str.split(",")]

# Create source SQLAlchemy engine
source_url = URL.create(
    drivername=get_config_value("SRC_DRIVER", cfg_parser=source_cfg),
    username=get_config_value("SRC_USER", cfg_parser=source_cfg),
    password=get_config_value("SRC_PW", cfg_parser=source_cfg),
    host=get_config_value("SRC_HOST", cfg_parser=source_cfg),
    port=int(get_config_value("SRC_PORT", cfg_parser=source_cfg)),
    database=get_config_value("SRC_DB", cfg_parser=source_cfg)
)
source_engine = create_engine(source_url)

# Create destination SQLAlchemy engine
dest_url = URL.create(
    drivername=get_config_value("DST_DRIVER", cfg_parser=dest_cfg),
    username=get_config_value("DST_USER", cfg_parser=dest_cfg),
    password=get_config_value("DST_PW", cfg_parser=dest_cfg),
    host=get_config_value("DST_HOST", cfg_parser=dest_cfg),
    port=int(get_config_value("DST_PORT", cfg_parser=dest_cfg)),
    database=get_config_value("DST_DB", cfg_parser=dest_cfg)
)
dest_engine = create_engine(dest_url)

# Dump tables from source to parquet files
dump_tables_to_parquet(source_engine, tables, output_dir="data")

# Upload parquet files into destination database
upload_parquet_to_db(
    dest_engine,
    database=get_config_value("DST_DB", cfg_parser=dest_cfg),
    schema=get_config_value("DST_SCHEMA", cfg_parser=dest_cfg),
    input_dir="data"
)
