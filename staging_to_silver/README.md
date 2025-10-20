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

Prioriteit: INI > ENV > defaults, net als in `source_to_staging`.