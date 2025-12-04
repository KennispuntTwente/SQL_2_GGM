#!/bin/bash
set -euo pipefail

# ============================================================================
# GGM Docker-demo - run_demo.sh
# ============================================================================
# Run de volledige ggmpilot-demo in Docker-containers. 
# Geen lokale Python-installatie nodig
#
# Gebruiksaanwijzing:
#   bash docker/demo/run_demo.sh                    # Volledige demo met meegeleverde Postgres
#   bash docker/demo/run_demo.sh --db-only          # Alleen de database starten
#   bash docker/demo/run_demo.sh --build            # Forceer herbouwen van Docker-image
#   bash docker/demo/run_demo.sh --clean            # Ruim containers en volumes op
#   bash docker/demo/run_demo.sh --external         # Gebruik externe database (stel env vars in)
#
# Environment variables:
#   DEMO_DB_HOST       - Database host (default: demo-db / host.docker.internal for --external)
#   DEMO_DB_PORT       - Database port (default: 5432)
#   DEMO_DB_USER       - Database gebruiker (default: postgres)
#   DEMO_DB_PASSWORD   - Database wachtwoord (default: postgres)
#   DEMO_DB_NAME       - Database naam (default: demo)
#   DEMO_DB_DRIVER     - SQLAlchemy driver (default: postgresql+psycopg2)
#   DEMO_ROWS          - Aantal synthetische rijen (default: 10)
#   DEMO_SEED          - Random seed voor reproduceerbaarheid (default: 123)
#
# Voorbeelden:
#   # Draaien met meer synthetische data
#   DEMO_ROWS=100 bash docker/demo/run_demo.sh
#
#   # Verbinden met externe MSSQL database
#   DEMO_DB_DRIVER="mssql+pyodbc" \
#   DEMO_DB_HOST="host.docker.internal" \
#   DEMO_DB_PORT=1433 \
#   DEMO_DB_USER=sa \
#   DEMO_DB_PASSWORD="YourPassword123!" \
#   DEMO_DB_NAME=mydb \
#   bash docker/demo/run_demo.sh --external
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

# Argumenten parsen
BUILD_FLAG=""
DB_ONLY=0
CLEAN=0
EXTERNAL=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --db-only)
            DB_ONLY=1
            shift
            ;;
        --clean)
            CLEAN=1
            shift
            ;;
        --external)
            EXTERNAL=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--build] [--db-only] [--clean] [--external]"
            exit 1
            ;;
    esac
done

cd "${PROJECT_ROOT}"

# Clean up
if [[ "${CLEAN}" == "1" ]]; then
    echo "Opruimen van demo-containers en volumes..."
    docker compose -f "${COMPOSE_FILE}" down -v --remove-orphans 2>/dev/null || true
    echo "✓ Opruimen voltooid"
    exit 0
fi

# Alleen database starten
if [[ "${DB_ONLY}" == "1" ]]; then
    echo "Demo-database wordt gestart..."
    docker compose -f "${COMPOSE_FILE}" up ${BUILD_FLAG} -d demo-db
    echo ""
    echo "Database draait op poort ${DEMO_DB_PORT:-55432}"
    echo "  Host: localhost:${DEMO_DB_PORT:-55432}"
    echo "  Gebruiker: ${DEMO_DB_USER:-postgres}"
    echo "  Wachtwoord: ${DEMO_DB_PASSWORD:-postgres}"
    echo "  Database: ${DEMO_DB_NAME:-demo}"
    echo ""
    echo "Om te stoppen: docker compose -f ${COMPOSE_FILE} down"
    exit 0
fi

# Externe database modus
if [[ "${EXTERNAL}" == "1" ]]; then
    echo "=============================================="
    echo "ggmpilot Demo - Externe database modus"
    echo "=============================================="
    echo ""
    echo "Externe database gebruiken:"
    echo "  Driver: ${DEMO_DB_DRIVER:-postgresql+psycopg2}"
    echo "  Host: ${DEMO_DB_HOST:-host.docker.internal}:${DEMO_DB_PORT:-5432}"
    echo "  Database: ${DEMO_DB_NAME:-demo}"
    echo ""
    
    docker compose -f "${COMPOSE_FILE}" ${BUILD_FLAG} run --rm demo-app-external
    exit $?
fi

# Full demo mode (with bundled Postgres)
echo "=============================================="
echo "GGM Docker-demo - Volledige pipeline in Docker"
echo "=============================================="
echo ""
echo "Dit:"
echo "  1. Start een PostgreSQL database-container"
echo "  2. Genereert synthetische testdata"
echo "  3. Draait sql_to_staging (source → staging)"
echo "  4. Draait staging_to_silver (staging → silver)"
echo ""

# Start database first
echo "Database wordt gestart..."
docker compose -f "${COMPOSE_FILE}" up ${BUILD_FLAG} -d demo-db
echo "Wachten tot database gezond is..."
sleep 2

# Run the demo app
echo ""
docker compose -f "${COMPOSE_FILE}" ${BUILD_FLAG} run --rm demo-app
exit_code=$?

echo ""
if [[ "${exit_code}" == "0" ]]; then
    echo "=============================================="
    echo "Demo succesvol afgerond!"
    echo "=============================================="
    echo ""
    echo "De database draait nog steeds. Je kunt verbinden met:"
    echo "  Host: localhost:${DEMO_DB_PORT:-55432}"
    echo "  User: ${DEMO_DB_USER:-postgres}"
    echo "  Password: ${DEMO_DB_PASSWORD:-postgres}"
    echo "  Database: ${DEMO_DB_NAME:-demo}"
    echo "  Schemas: source, staging, silver"
    echo ""
    echo "Om de database te stoppen:"
    echo "  docker compose -f ${COMPOSE_FILE} down"
    echo ""
    echo "Om alles volledig op te ruimen (inclusief data):"
    echo "  bash docker/demo/run_demo.sh --clean"
else
    echo "Demo mislukt met exit code ${exit_code}"
fi

exit ${exit_code}
