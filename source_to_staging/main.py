# source_to_staging/main.py

import os
from dotenv import load_dotenv
import configparser
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

from functions.source_dump import dump_tables_to_parquet
from functions.upload_parquet import upload_parquet_to_db

# Load environment variables from .env file
load_dotenv(dotenv_path="source_to_staging/.env")

# Read table/schema config from INI file
cfg = configparser.ConfigParser()
cfg.read("source_to_staging/connection_config.ini")

tables = [t.strip() for t in cfg["general"]["tables"].split(",")]
schema = cfg["general"].get("schema", "public")

# Create SQLAlchemy engines from ENV vars
source_url = URL.create(
    drivername=os.environ["SRC_DRIVER"],
    username=os.environ["SRC_USER"],
    password=os.environ["SRC_PW"],
    host=os.environ["SRC_HOST"],
    port=int(os.environ["SRC_PORT"]),
    database=os.environ["SRC_DB"]
)
source_engine = create_engine(source_url)

dest_url = URL.create(
    drivername=os.environ["DST_DRIVER"],
    username=os.environ["DST_USER"],
    password=os.environ["DST_PW"],
    host=os.environ["DST_HOST"],
    port=int(os.environ["DST_PORT"]),
    database=os.environ["DST_DB"]
)
dest_engine = create_engine(dest_url)

# Run migration process
dump_tables_to_parquet(source_engine, tables, output_dir="data")
upload_parquet_to_db(dest_engine, schema, input_dir="data")
