# Docker demo

Met deze demo kun je de volledige pipeline (`sql_to_staging` + `staging_to_silver`) snel uitproberen in Docker containers, met synthetische data.
Hierdoor is geen lokale Python installatie nodig om de demo te draaien; enkel Docker of Podman.

## Quickstart

Vanuit de projectroot:

```bash
bash docker/demo/run_demo.sh
```

Dit doet het volgende:
1. Start een PostgreSQL database-container
2. Genereert synthetische testdata
3. Draait `sql_to_staging` (source → staging)
4. Draait `staging_to_silver` (staging → silver)

### Opties

Je kunt de demo met verschillende opties draaien:

```bash
# Volledige demo met meegeleverde Postgres (standaard)
bash docker/demo/run_demo.sh

# Forceer herbouwen van Docker-image
bash docker/demo/run_demo.sh --build

# Start alleen de database (handig voor ontwikkeling)
bash docker/demo/run_demo.sh --db-only

# Ruim containers en volumes op
bash docker/demo/run_demo.sh --clean

# Gebruik externe database (zie hieronder)
bash docker/demo/run_demo.sh --external
```

Pas de demo aan via environment variables:

| Variabele | Standaard | Beschrijving |
|-----------|-----------|---------------|
| `DEMO_DB_HOST` | `demo-db` | Database host |
| `DEMO_DB_PORT` | `5432` (container) / `55432` (host) | Database poort |
| `DEMO_DB_USER` | `postgres` | Database gebruiker |
| `DEMO_DB_PASSWORD` | `postgres` | Database wachtwoord |
| `DEMO_DB_NAME` | `demo` | Database naam |
| `DEMO_DB_DRIVER` | `postgresql+psycopg2` | SQLAlchemy driver |
| `DEMO_ROWS` | `10` | Aantal synthetische rijen |
| `DEMO_SEED` | `123` | Random seed voor reproduceerbaarheid |

### Voorbeelden

Draaien met meer data:
```bash
DEMO_ROWS=100 bash docker/demo/run_demo.sh
```

Gebruik een andere poort:
```bash
DEMO_DB_PORT=5555 bash docker/demo/run_demo.sh
```

### Je eigen database gebruiken

Om de demo te draaien tegen je eigen database (niet Postgres in Docker), stel je de juiste environment variables in en voeg je de `--external` vlag toe:

```bash
# PostgreSQL op host machine
DEMO_DB_HOST="host.docker.internal" \
DEMO_DB_PORT=5432 \
DEMO_DB_USER=myuser \
DEMO_DB_PASSWORD="mypassword" \
DEMO_DB_NAME=mydb \
bash docker/demo/run_demo.sh --external

# MSSQL Server
DEMO_DB_DRIVER="mssql+pyodbc" \
DEMO_DB_HOST="host.docker.internal" \
DEMO_DB_PORT=1433 \
DEMO_DB_USER=sa \
DEMO_DB_PASSWORD="YourPassword123!" \
DEMO_DB_NAME=mydb \
bash docker/demo/run_demo.sh --external
```

> Let op: `host.docker.internal` verwijst naar de host machine vanuit Docker.

### Stappen overslaan

Je kunt individuele pipeline-stappen overslaan:

```bash
# Synthetische data generatie overslaan (gebruik bestaande CSVs)
SKIP_GENERATE=1 bash docker/demo/run_demo.sh

# CSVs laden overslaan (als source schema al gevuld is)
SKIP_LOAD=1 bash docker/demo/run_demo.sh

# sql_to_staging stap overslaan
SKIP_SQL_TO_STAGING=1 bash docker/demo/run_demo.sh

# staging_to_silver stap overslaan
SKIP_STAGING_TO_SILVER=1 bash docker/demo/run_demo.sh

# Alleen staging_to_silver draaien (veronderstelt dat staging al gevuld is)
SKIP_GENERATE=1 SKIP_LOAD=1 SKIP_SQL_TO_STAGING=1 bash docker/demo/run_demo.sh
```

### Database inspecteren

Na afloop van de demo blijft de database draaien. Verbind met een PostgreSQL client:

```bash
# Met psql (indien geïnstalleerd)
psql -h localhost -p 55432 -U postgres -d demo

# Of via Docker
docker exec -it ggmpilot-demo-db psql -U postgres -d demo
```

Query de schemas:
```sql
-- Lijst schemas
SELECT schema_name FROM information_schema.schemata;

-- Lijst tabellen per schema
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema IN ('source', 'staging', 'silver')
ORDER BY table_schema, table_name;

-- Voorbeelddata uit silver schema
SELECT * FROM silver."CLIENT" LIMIT 10;
```

### Opruimen

```bash
# Stop containers
docker compose -f docker/demo/docker-compose.yml down

# Stop en verwijder alle data
bash docker/demo/run_demo.sh --clean
```
