#!/usr/bin/env bash
# Run the end-to-end synthetic pipeline exactly as documented, with small knobs for CI.
# Env overrides:
#   PORT      - host port for Postgres container (default 55432)
#   PASSWORD  - database password (default matches README)
#   ROWS      - number of rows to generate (default 10)
#   OUT_DIR   - output dir for CSVs (default data/synthetic)
set -euo pipefail

PORT=${PORT:-55432}
PASSWORD=${PASSWORD:-SecureP@ss1!24323482349}
ROWS=${ROWS:-10}
OUT_DIR=${OUT_DIR:-data/synthetic}

# 1) Generate synthetic CSVs
python -m synthetic.generate_synthetic_data --out "${OUT_DIR}" --rows "${ROWS}" --seed 123

# 2) Load CSVs into Postgres DB "source" (schema: public)
python -m synthetic.load_csvs_to_db \
  --db postgres \
  --db-name source \
  --user sa \
  --password "${PASSWORD}" \
  --port "${PORT}" \
  --schema "" \
  --csv-dir "${OUT_DIR}" \
  --force-refresh

# 3) Ensure DB ggm exists + create staging & silver schemas
python - <<PY
from dev_sql_server.get_connection import get_connection
engine = get_connection(db_type="postgres", db_name="ggm", user="sa", password="${PASSWORD}", port=${PORT}, force_refresh=True, print_tables=False)
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text('CREATE SCHEMA IF NOT EXISTS staging'))
    conn.execute(text('CREATE SCHEMA IF NOT EXISTS silver'))
PY

# 4) Pre-create silver tables from GGM DDL
python - <<'PY'
import os
from dev_sql_server.get_connection import get_connection
from sqlalchemy import text
from utils.database.execute_sql_folder import execute_sql_folder

PORT = int(os.environ.get('PORT', '55432'))
PASSWORD = os.environ.get('PASSWORD', 'SecureP@ss1!24323482349')

# Connect to ggm DB (Postgres)
engine = get_connection(db_type="postgres", db_name="ggm", user="sa", password=PASSWORD, port=PORT, force_refresh=False, print_tables=False)

# 4a) Execute the standard GGM DDL scripts into schema "silver"
execute_sql_folder(engine, "ggm_selectie/CSSD", suffix_filter=True, schema="silver")
PY

# 5) sql_to_staging: source -> staging schema in DB ggm
printf "%s\n" \
  "[database-source]" \
  "SRC_DRIVER = postgresql+psycopg2" \
  "SRC_HOST = localhost" \
  "SRC_PORT = ${PORT}" \
  "SRC_DB = source" \
  "SRC_USERNAME = sa" \
  "SRC_PASSWORD = ${PASSWORD}" \
  "" \
  "[database-destination]" \
  "DST_DRIVER = postgresql+psycopg2" \
  "DST_HOST = localhost" \
  "DST_PORT = ${PORT}" \
  "DST_DB = ggm" \
  "DST_SCHEMA = staging" \
  "DST_USERNAME = sa" \
  "DST_PASSWORD = ${PASSWORD}" \
  "" \
  "[settings]" \
  "TRANSFER_MODE = SQLALCHEMY_DIRECT" \
  "SRC_TABLES = szclient,wvbesl,wvind_b,szregel,wvdos,abc_refcod,szukhis,szwerker" \
  "ASK_PASSWORD_IN_CLI = False" \
> ./src_to_staging.ini
python -m sql_to_staging.main --config ./src_to_staging.ini

# 6) staging_to_silver in DB ggm (read from staging, write to silver)
#    We already created tables and trigger; skip INIT step
printf "%s\n" \
  "[database-destination]" \
  "DST_DRIVER = postgresql+psycopg2" \
  "DST_HOST = localhost" \
  "DST_PORT = ${PORT}" \
  "DST_DB = ggm" \
  "DST_SCHEMA = staging" \
  "DST_USERNAME = sa" \
  "DST_PASSWORD = ${PASSWORD}" \
  "" \
  "[settings]" \
  "SILVER_SCHEMA = silver" \
  "INIT_SQL_FOLDER =" \
  "DELETE_EXISTING_SCHEMA = False" \
> ./staging_to_silver.ini
python -m staging_to_silver.main --config ./staging_to_silver.ini
