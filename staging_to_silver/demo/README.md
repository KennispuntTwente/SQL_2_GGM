# Demo: `staging_to_silver`

Korte demo om de silver-pipeline te draaien op de synthetische stagingtabellen in de lokale Postgres dev database.

## Optie 1: Draaien in Docker (geen lokale Python nodig)

```bash
bash docker/demo/run_demo.sh
```

Dit draait de volledige pipeline (inclusief `sql_to_staging` EN `staging_to_silver`) in Docker containers.
Zie [docker/demo/README.md](../../docker/demo/README.md) voor meer opties.

Om alleen `staging_to_silver` te draaien (als staging al gevuld is):

```bash
SKIP_GENERATE=1 SKIP_LOAD=1 SKIP_SQL_TO_STAGING=1 bash docker/demo/run_demo.sh
```

## Optie 2: Lokaal draaien (vereist Python)

Voer in de projectroot uit, met Docker/Podman geïnstalleerd & actief:

```bash
source .venv/Scripts/activate
bash staging_to_silver/demo/demo.sh
```

> Let op: je moet eerst de `sql_to_staging` demo hebben gedraaid om de benodigde stagingtabellen te vullen.
Dan pas kun je deze `staging_to_silver` demo draaien. Zie: [sql_to_staging/demo/README.md](sql_to_staging/demo/README.md).
