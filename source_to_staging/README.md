# source_to_staging

Deze module is verantwoordelijk voor het verbinden met de 'applicatie-SQL-server' (bijv. Oracle) en het overbrengen
van data hieruit naar de SQL-server waarop je het GGM wil hebben staan, de 
'target-SQL-server' (bijv. Postgres of Microsoft SQL Server).

Hiermee ontstaat op de target-SQL-server een 'brons' (staging) laag met de data uit de applicatie, nog in de vorm zoals deze op de applicatie-SQL-server staat.

In de module 'staging_to_silver' wordt deze data vervolgens omgevormd naar het Gemeentelijk Gegevensmodel (GGM), oftewel 'zilver'.

In de sectie "Configuratie" staat uitgelegd hoe deze module te configureren.

(Voor uitleg van commands om deze module te runnen met configuratie, zie de `README.md` in de root van de repository; sectie "Uitvoeren".)

(Als je deze module wil uitproberen met synthetische data en zonder productie-database, zie de demo-scripts in `source_to_staging/demo/`.)

## Configuratie

`source_to_staging` gebruikt één INI-bestand (`--config`) met de secties
- `[database-source]`, `[database-destination]`, 
, `[settings]` en optioneel `[logging]`.
Een voorbeeld staat in `source_to_staging/config.ini.example`. 
Je kan ook via environment-variables configureren; zie voorbeeld
`source_to_staging/.env.example`. 
Prioriteit bij configuratie is INI > environment variables > standaard-waardes.

Hieronder staat verder toegelicht wat de verschillende opties doen. 
Er staat ook beknopte toelichting in de voorbeeld-configuratiebestanden 
(`source_to_staging/config.ini.example` en `source_to_staging/.env.example`).

### Transfer modes

Je kan verschillende manieren kiezen waarop de data wordt overgebracht
vanuit de applicatie-SQL-server naar de target-SQL-server. Kies de modus in `[settings]` via `TRANSFER_MODE`:

- `SQLALCHEMY_DIRECT`: directe kopie van bron naar doel, met lowercase kolomnamen in staging.
- `SQLALCHEMY_DUMP`: leest via SQLAlchemy, dumpt naar Parquet-bestanden, uploadt daarna deze Parquet-bestanden
- `CONNECTORX_DUMP`: leest via ConnectorX (sneller, gaat soms beter om met data-types), dumpt naar Parquet-bestanden, uploadt daarna Parquet-bestanden.

In principe zouden alle manieren met alle database-types moeten werken, maar mocht je fouten tegenkomen dan zou je kunnen
proberen te switchen naar een andere modus. De 'dump'-varianten kunnen interessant zijn als je bijvoorbeeld
de parquet-bestanden wil gebruiken om een ruwe historie op te bouwen (buiten de actuele data op de target-SQL-server).

 