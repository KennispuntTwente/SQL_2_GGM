# source_to_staging

Deze module is verantwoordelijk voor het verbinden met de applicatie-SQL-server (bijv. Oracle),
het dumpen van specifieke tabellen naar (tijdelijke) Parquet-bestanden,
en vervolgens het uploaden van deze Parquet-bestanden naar tabellen in de
target-SQL-server (bijv. Postgres of SQL Server).

Hiermee ontstaat op de target-SQL-server een 'brons' (staging) laag met de data uit de applicatie,
nog in de vorm zoals deze op de applicatie-SQL-server staat.

In de module 'staging_to_silver' wordt deze data vervolgens omgevormd naar het Gemeentelijk Gegevensmodel (GGM),
oftewel 'zilver'.

## Configuratie (één .ini)

Vanaf nu gebruikt `source_to_staging` één enkele INI met de secties:

- `[database-source]` (keys: `SRC_*`)
- `[database-destination]` (keys: `DST_*`)
- `[settings]` (bijv. `SRC_TABLES`, `SRC_CHUNK_SIZE`)
- `[logging]`

Zie het voorbeeld `source_to_staging/config.ini.example`.

Prioriteit bij configuratie is: .ini > environment variables > default.

### Voorbeeld run

Gebruik met één INI-bestand:

```
python -m source_to_staging.main --config source_to_staging/config.ini
```

Of zonder INI, puur via environment variabelen (bijv. `.env`):

```
python -m source_to_staging.main
```

De smoke tests in `docker/smoke` zijn aangepast om één INI te gebruiken (`docker/config/source_to_staging.ini`).

## Transfer modes

Kies de modus in `[settings]` via `TRANSFER_MODE`:

- `SQLALCHEMY_DIRECT`: geen Parquet; chunked directe kopie van bron naar doel, met lowercase kolomnamen in staging.
- `SQLALCHEMY_DUMP`: lees via SQLAlchemy, dump naar Parquet, upload daarna Parquet.
- `CONNECTORX_DUMP`: lees via ConnectorX (sneller, vaak betere type-fidelity), dump naar Parquet, upload daarna Parquet.

In principe zouden alle manieren met alle database-types moeten werken, maar mocht je fouten tegenkomen dan zou je kunnen
proberen te switchen naar een andere modus. De 'dump'-varianten kunnen interessant zijn als je bijvoorbeeld
de parquet-bestanden wil gebruiken om een ruwe historie op te bouwen (buiten de actuele data op de target-SQL-server).

### Transient errors en retries (alleen direct transfer)

De directe kopie (`SQLALCHEMY_DIRECT`) voert inserts uit in batches. Bij tijdelijke databasefouten (bijv. deadlocks,
time-outs of weggevallen verbinding) probeert de kopie de batch opnieuw met een kleine exponential backoff met jitter.

- Standaard: maximaal 3 retries, start-backoff 0.5s, max-backoff 8s.
- Herproberen gebeurt per batch binnen een transactie; bij een fout wordt de batch-transactie teruggedraaid en blijft de broncursor gewoon doorstreamen.
- Deze instellingen zijn ook als optionele parameters in `direct_transfer(...)` beschikbaar (`max_retries`, `backoff_base_seconds`, `backoff_max_seconds`).

## Parquet dump/upload details

- Bestandsnamen: voor grote tabellen worden part-bestanden geschreven met het patroon `<tabelnaam>_part0000.parquet`, `<tabelnaam>_part0001.parquet`, enzovoort.
- Manifest per run: bij een dump met `SQLALCHEMY_DUMP` of `CONNECTORX_DUMP` wordt een manifest-bestand aangemaakt in de outputmap (standaard `data`). Dit manifest bevat uitsluitend de in deze run aangemaakte parquet-bestanden. De upload-stap gebruikt dit manifest zodat er nooit per ongeluk oude/overgebleven bestanden worden meegepakt.
- Cleanup bij fouten: wanneer `CLEANUP_PARQUET_FILES=True` (default) worden de parquet-bestanden na upload verwijderd. Dit gebeurt ook als er tijdens de upload een fout optreedt; cleanup draait in een `finally`-blok. Het manifest-bestand wordt eveneens opgeschoond.
- Lowercase kolomnamen: alle kolomnamen worden tijdens upload naar lowercase geconverteerd voor consistentie in de staging-laag.

Relevante instellingen in `[settings]`:

- `SRC_TABLES`: kommagescheiden lijst van tabellen om te dumpen.
- `SRC_CHUNK_SIZE`: aantal rijen per chunk tijdens dump/streaming.
- `CLEANUP_PARQUET_FILES`: of parquet-bestanden (en manifest) na upload verwijderd moeten worden (default: `True`).
- `ROW_LIMIT` (optioneel): beperkt het aantal rijen per bron‑tabel voor snelle lokale ontwikkeling (0/leeg = geen limiet).