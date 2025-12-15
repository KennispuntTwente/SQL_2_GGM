#!/usr/bin/env bash

set -euo errexit

# Some minimal environments don't support `pipefail` (or may run under `sh`).
# Best effort: enable it when available.
set -o pipefail 2>/dev/null || true

# ============================================================================
# ggmpilot Demo Entrypoint
# ============================================================================
# Dit script draait de volledige ggmpilot demo-pipeline in Docker:
#   1. Genereer synthetische CSV-data
#   2. Laad CSVs in source-schema
#   3. Draai sql_to_staging (source -> staging)
#   4. Draai staging_to_silver (staging -> silver)
#
# Environment variables (met standaardwaarden):
#   DEMO_DB_HOST       - Database host (standaard: demo-db)
#   DEMO_DB_PORT       - Database poort (standaard: 5432)
#   DEMO_DB_USER       - Database gebruiker (standaard: postgres)
#   DEMO_DB_PASSWORD   - Database wachtwoord (standaard: postgres)
#   DEMO_DB_NAME       - Database naam (standaard: demo)
#   DEMO_DB_DRIVER     - SQLAlchemy driver (standaard: postgresql+psycopg2)
#   DEMO_ROWS          - Aantal synthetische rijen (standaard: 10)
#   DEMO_SEED          - Random seed voor reproduceerbaarheid (standaard: 123)
#   SKIP_GENERATE      - Sla synthetische data generatie over (standaard: 0)
#   SKIP_LOAD          - Sla CSVs laden naar source-schema over (standaard: 0)
#   SKIP_SQL_TO_STAGING    - Sla sql_to_staging stap over (standaard: 0)
#   SKIP_STAGING_TO_SILVER - Sla staging_to_silver stap over (standaard: 0)
# ============================================================================

echo "=============================================="
echo "ggmpilot Demo - Volledige pipeline in Docker"
echo "=============================================="
echo ""

# Read environment with defaults
DB_HOST="${DEMO_DB_HOST:-demo-db}"
DB_PORT="${DEMO_DB_PORT:-5432}"
DB_USER="${DEMO_DB_USER:-postgres}"
DB_PASSWORD="${DEMO_DB_PASSWORD:-postgres}"
DB_NAME="${DEMO_DB_NAME:-demo}"
DB_DRIVER="${DEMO_DB_DRIVER:-postgresql+psycopg2}"
ROWS="${DEMO_ROWS:-10}"
SEED="${DEMO_SEED:-123}"

echo "Configuratie:"
echo "  Database: ${DB_DRIVER}://${DB_USER}:****@${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo "  Synthetische rijen: ${ROWS}"
echo "  Random seed: ${SEED}"
echo ""

# Generate config files dynamically based on environment
CONFIG_DIR="/tmp/demo_config"
mkdir -p "${CONFIG_DIR}"

# sql_to_staging config
cat > "${CONFIG_DIR}/sql_to_staging.ini" <<EOF
[database-source]
SRC_DRIVER = ${DB_DRIVER}
SRC_USERNAME = ${DB_USER}
SRC_PASSWORD = ${DB_PASSWORD}
SRC_HOST = ${DB_HOST}
SRC_PORT = ${DB_PORT}
SRC_DB = ${DB_NAME}
SRC_SCHEMA = source

[database-destination]
DST_DRIVER = ${DB_DRIVER}
DST_USERNAME = ${DB_USER}
DST_PASSWORD = ${DB_PASSWORD}
DST_HOST = ${DB_HOST}
DST_PORT = ${DB_PORT}
DST_DB = ${DB_NAME}
DST_SCHEMA = staging

[settings]
TRANSFER_MODE = SQLALCHEMY_DIRECT
SRC_TABLES = szclient,wvbesl,wvind_b,szregel,wvdos,abc_refcod,szukhis,szwerker
SRC_CHUNK_SIZE = 50000
ASK_PASSWORD_IN_CLI = False

[logging]
LOG_LEVEL = INFO
EOF

# staging_to_silver config
cat > "${CONFIG_DIR}/staging_to_silver.ini" <<EOF
[database-destination]
DST_DRIVER = ${DB_DRIVER}
DST_USERNAME = ${DB_USER}
DST_PASSWORD = ${DB_PASSWORD}
DST_HOST = ${DB_HOST}
DST_PORT = ${DB_PORT}
DST_DB = ${DB_NAME}
DST_SCHEMA = staging

[settings]
SILVER_SCHEMA = silver
SILVER_NAME_MATCHING = auto
SILVER_TABLE_NAME_CASE = upper
SILVER_COLUMN_NAME_CASE =
INIT_SQL_FOLDER = ggm_selectie/cssd
INIT_SQL_SUFFIX_FILTER = True
DELETE_EXISTING_SCHEMA = True

[logging]
LOG_LEVEL = INFO
EOF

echo "Configuratiebestanden gegenereerd in ${CONFIG_DIR}"
echo ""

# ============================================================================
# Stap 1: Genereer synthetische data
# ============================================================================
if [[ "${SKIP_GENERATE:-0}" != "1" ]]; then
    echo "----------------------------------------------"
    echo "Stap 1: Synthetische CSV-data genereren..."
    echo "----------------------------------------------"
    /app/.venv/bin/python -m synthetic.generate_synthetic_data \
        --out /app/data/synthetic \
        --rows "${ROWS}" \
        --seed "${SEED}"
    echo "✓ Synthetische data gegenereerd in /app/data/synthetic"
    echo ""
else
    echo "Stap 1: Synthetische data generatie overgeslagen (SKIP_GENERATE=1)"
    echo ""
fi

# ============================================================================
# Stap 2: Laad CSVs in source-schema
# ============================================================================
if [[ "${SKIP_LOAD:-0}" != "1" ]]; then
    echo "----------------------------------------------"
    echo "Stap 2: CSVs laden in source-schema..."
    echo "----------------------------------------------"
    
    # Use the direct loader (no Docker management - works inside containers)
    /app/.venv/bin/python -m synthetic.load_csvs_to_db_direct \
        --driver "${DB_DRIVER}" \
        --host "${DB_HOST}" \
        --port "${DB_PORT}" \
        --user "${DB_USER}" \
        --password "${DB_PASSWORD}" \
        --db-name "${DB_NAME}" \
        --schema source \
        --csv-dir /app/data/synthetic
    echo "✓ CSVs geladen in source-schema"
    echo ""
else
    echo "Stap 2: CSVs laden overgeslagen (SKIP_LOAD=1)"
    echo ""
fi

# ============================================================================
# Stap 3: Draai sql_to_staging
# ============================================================================
if [[ "${SKIP_SQL_TO_STAGING:-0}" != "1" ]]; then
    echo "----------------------------------------------"
    echo "Stap 3: sql_to_staging draaien..."
    echo "----------------------------------------------"
    /app/.venv/bin/python -m sql_to_staging.main --config "${CONFIG_DIR}/sql_to_staging.ini"
    echo "✓ sql_to_staging voltooid"
    echo ""
else
    echo "Stap 3: sql_to_staging overgeslagen (SKIP_SQL_TO_STAGING=1)"
    echo ""
fi

# ============================================================================
# Stap 4: Draai staging_to_silver
# ============================================================================
if [[ "${SKIP_STAGING_TO_SILVER:-0}" != "1" ]]; then
    echo "----------------------------------------------"
    echo "Stap 4: staging_to_silver draaien..."
    echo "----------------------------------------------"
    /app/.venv/bin/python -m staging_to_silver.main --config "${CONFIG_DIR}/staging_to_silver.ini"
    echo "✓ staging_to_silver voltooid"
    echo ""
else
    echo "Stap 4: staging_to_silver overgeslagen (SKIP_STAGING_TO_SILVER=1)"
    echo ""
fi

# ============================================================================
# Klaar
# ============================================================================
echo "=============================================="
echo "Demo succesvol afgerond!"
echo "=============================================="
echo ""
echo "Je kunt de data in de database inspecteren:"
echo "  Host: ${DB_HOST}:${DB_PORT}"
echo "  Database: ${DB_NAME}"
echo "  Schemas: source, staging, silver"
echo ""
