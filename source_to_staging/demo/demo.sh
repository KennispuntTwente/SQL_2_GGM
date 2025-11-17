#!/usr/bin/env bash
set -euo pipefail

# Eenvoudige demo voor source_to_staging met synthetische data en Postgres dev DB.

PORT=${PORT:-55432}

# 1) Genereer synthetische CSV's
python -m synthetic.generate_synthetic_data --out data/synthetic --rows 10 --seed 123

# 2) Laad CSV's in Postgres (schema staging)
python -m synthetic.load_csvs_to_db \
  --db postgres \
  --db-name ggm \
  --user postgres \
  --password postgres \
  --port "${PORT}" \
  --schema staging \
  --csv-dir data/synthetic \
  --force-refresh

# 3) Run source_to_staging met demo/config.ini
python -m source_to_staging.main --config source_to_staging/demo/config.ini
