#!/usr/bin/env bash
set -euo pipefail

# Eenvoudige demo voor staging_to_silver op de Postgres dev DB.

PORT=${PORT:-55432}

# Zorg dat de Postgres dev DB bestaat (wordt normaal door andere demo's opgezet)
python - <<PY
from dev_sql_server.get_connection import get_connection
engine = get_connection(db_type="postgres", db_name="ggm", user="postgres", password="postgres", port=${PORT}, force_refresh=False, print_tables=False)
PY

# Run staging_to_silver met demo/config.ini
python -m staging_to_silver.main --config staging_to_silver/demo/config.ini
