#!/usr/bin/env bash
set -euo pipefail

# Eenvoudige demo voor sql_to_staging met synthetische data en Postgres dev-server

PORT=${PORT:-55432}

# 1) Genereer synthetische CSV's
python -m synthetic.generate_synthetic_data --out data/synthetic --rows 10 --seed 123

# 2) Laad CSV's in Postgres (schema source) – bron apart van staging
python -m synthetic.load_csvs_to_db \
  --db postgres \
  --db-name source \
  --user postgres \
  --password postgres \
  --port "${PORT}" \
  --schema source \
  --csv-dir data/synthetic \
  --force-refresh

# 3) Run sql_to_staging met demo/config.ini
python -m sql_to_staging.main --config sql_to_staging/demo/config.ini
