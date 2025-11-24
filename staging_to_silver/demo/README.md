# Demo: `staging_to_silver`

Korte demo om de silver-pipeline te draaien op de synthetische stagingtabellen in de lokale Postgres dev database.

## Command

Voer in de projectroot uit, met Docker/Podman geïnstalleerd & actief:

```bash
source .venv/Scripts/activate
bash staging_to_silver/demo/demo.sh
```

> Let op: je moet eerst de `sql_to_staging` demo hebben gedraaid om de benodigde stagingtabellen te vullen.
Dan pas kun je deze `staging_to_silver` demo draaien. Zie: [sql_to_staging/demo/README.md](sql_to_staging/demo/README.md).
