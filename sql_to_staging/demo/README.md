# Demo: `sql_to_staging`

Korte demo om de module snel uit te proberen met de meegeleverde synthetische data en een lokale Postgres dev database.

## Optie 1: Draaien in Docker (geen lokale Python nodig)

```bash
bash docker/demo/run_demo.sh
```

Dit draait de volledige pipeline (inclusief `sql_to_staging` EN `staging_to_silver`) in Docker containers.
Zie [docker/demo/README.md](../../docker/demo/README.md) voor meer opties.

## Optie 2: Lokaal draaien (vereist Python)

Voer in de projectroot uit, met Docker/Podman geïnstalleerd & actief:

```bash
source .venv/Scripts/activate
bash sql_to_staging/demo/demo.sh
```

Dit script:
- genereert synthetische CSV-bestanden onder `data/synthetic`,
- start/maakt een Postgres dev database op poort `55432`,
- laadt de CSV’s in schema `staging`,
- runt vervolgens de `sql_to_staging` module met `demo/config.ini`.

> Na het uitvoeren van deze demo kan je ook de `staging_to_silver` demo draaien om de silver-pipeline te testen.
Zie: [staging_to_silver/demo/README.md](../staging_to_silver/demo/README.md).
