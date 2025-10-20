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
- `[settings]` (bijv. `SRC_TABLES`, `SRC_CHUNK_SIZE`, `SRC_CONNECTORX`)
- `[logging]`

Zie het voorbeeld `source_to_staging/config.ini.example`.

Belangrijk: de key-namen blijven gelijk aan de bestaande environment variabelen (bijv. `SRC_DRIVER`,
`DST_DB`, etc.). Prioriteit blijft: INI > ENV > default. `.env` in `source_to_staging/` blijft ondersteund.

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

- `SQLALCHEMY_DUMP`: lees via SQLAlchemy, dump naar Parquet, upload daarna Parquet.
- `CONNECTORX_DUMP`: lees via ConnectorX (sneller, vaak betere type-fidelity), dump naar Parquet, upload daarna Parquet.
- `SQLALCHEMY_DIRECT`: geen Parquet; chunked directe kopie van bron naar doel, met lowercase kolomnamen in staging.

Opmerking bij `SQLALCHEMY_DIRECT`:
- Voorkomt type/precisie issues door Parquet roundtrip te vermijden.
- Chunk-grootte via `SRC_CHUNK_SIZE`.
- Standaard schrijfmodus is `replace` (tabel per run opnieuw aanmaken); aanpasbaar in code indien nodig.