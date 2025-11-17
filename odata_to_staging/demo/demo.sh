#!/usr/bin/env bash
set -euo pipefail

# Eenvoudige demo voor odata_to_staging richting Postgres dev DB.

PORT=${PORT:-55432}

# Zorg dat de Postgres dev DB draait
python - <<PY
from dev_sql_server.get_connection import get_connection
engine = get_connection(db_type="postgres", db_name="ggm", user="postgres", password="postgres", port=${PORT}, force_refresh=False, print_tables=False)
PY

# Run odata_to_staging. If a local .env exists, prefer environment-driven config;
# otherwise fall back to the demo INI for sensible defaults.
if [ -f "odata_to_staging/.env" ]; then
	python -m odata_to_staging.main
else
	python -m odata_to_staging.main --config odata_to_staging/demo/config.ini
fi
