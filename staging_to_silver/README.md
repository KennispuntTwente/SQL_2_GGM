# staging_to_silver

Deze module verbindt met de SQL-server waarop data uit de applicatie is gedumpt in de eerdere module (source_to_staging),
en vormt deze via SQL-queries om naar de structuur van het gemeentelijk gegevensmodel (GGM)

Van belang is dat dus source_to_staging reeds is uitgevoerd, en ook dat er een database is waar de (lege) tabellen
van het gemeentelijk gegevensmodel op staan (zie map: ggm_selectie).

De module verbindt met de SQL-server en voert queries uit die de 'source'-data ('brons') omvornen naar het GGM ('zilver').
Deze queries zijn gedefinieerd in SQLAlchemy zodat ze op verschillende typen SQL-servers kunnen werken.
De SQL-queries zijn in feite de GGM-mappings, direct ook in de vorm van uitvoerbare code.

## Configuratie

`staging_to_silver` gebruikt één INI-bestand (`--config`) met secties `[database]`, `[settings]` en optioneel `[logging]`.
Een voorbeeld staat in `staging_to_silver/config.ini.example`.

- `[database]` keys: `DRIVER`, `HOST`, `PORT`, `USER`, `PASSWORD`, `DB` (en optioneel `SCHEMA`) – deze corresponderen 1-op-1 met environment variabelen met dezelfde namen.
- `[settings]` bevat o.a. `SOURCE_SCHEMA`, `TARGET_SCHEMA`, `ASK_PASSWORD_IN_CLI`, en optioneel `TABLE_NAME_CASE` en `COLUMN_NAME_CASE`.
	- Dialect-filtering van queries: `QUERY_ALLOWLIST` en/of `QUERY_DENYLIST` (komma/; gescheiden lijst van doeltabellen) om enkel de gewenste mappings uit te voeren. Namen matchen case-insensitief na normalisatie.

### Oracle (optioneel thick‑mode)

- Standaard gebruikt de driver `oracle+oracledb` thin‑mode. Voor thick‑mode (Instant Client) stel je een pad in via `DST_ORACLE_CLIENT_PATH` (in `[settings]` of als env var). Dit wordt vóór het opbouwen van de database‑verbinding geïnitialiseerd.
- Gebruik je een TNS‑alias, zet dan `DST_ORACLE_TNS_ALIAS=True` en vul de alias in bij `DST_HOST` (of `DST_DB`).

### Dialectondersteuning en write modes

- Alle queries draaien binnen één transactie. Het statement `SET CONSTRAINTS ALL DEFERRED` wordt alleen uitgevoerd op PostgreSQL; andere backends slaan dit over.
- Write modes per doel‑tabel: `append` (standaard), `overwrite`, `truncate`, `upsert`.
	- `upsert` is PostgreSQL‑only: op niet‑PostgreSQL backends geeft de pipeline een duidelijke foutmelding. Gebruik daar `append/overwrite/truncate`.
	- Per‑tabel write modes staan in `staging_to_silver/main.py` (dict `write_modes`).

### Queries selecteren

Als je bepaalde queries wel/niet wil draaien, kan je gebruik maken van `QUERY_ALLOWLIST`/`QUERY_DENYLIST` om alleen
bepaalde queries te draaien.

### Configuratie-prioriteit

Prioriteit: INI > ENV > defaults, net als in `source_to_staging`.