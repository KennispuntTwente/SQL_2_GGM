# staging_to_silver

Deze module verbindt met de SQL-server waarop data uit de applicatie is gedumpt in de eerdere module (source_to_staging),
en vormt deze via SQL-queries om naar de structuur van het gemeentelijk gegevensmodel (GGM)

Van belang is dat dus source_to_staging reeds is uitgevoerd, en ook dat er een database is waar de (lege) tabellen
van het gemeentelijk gegevensmodel op staan (zie map: ggm_selectie).

De module verbindt met de SQL-server en voert queries uit die de 'source'-data ('brons') omvornen naar het GGM ('zilver').
Deze queries zijn gedefinieerd in SQLAlchemy zodat ze op verschillende typen SQL-servers kunnen werken.
De SQL-queries zijn in feite de GGM-mappings, direct ook in de vorm van uitvoerbare code.

## Configuratie


`staging_to_silver` gebruikt één INI-bestand (`--config`) met secties `[database-destination]`, `[settings]` en optioneel `[logging]`.
Een voorbeeld staat in `staging_to_silver/config.ini.example`.

- `[database-destination]` keys: `DST_DRIVER`, `DST_HOST`, `DST_PORT`, `DST_USERNAME`, `DST_PASSWORD`, `DST_DB`, `DST_SCHEMA`.
	- Opmerking: `DST_DB/DST_SCHEMA` bepalen de staging (brons) locatie
	- Het silver (GGM) schema wordt NIET hier ingesteld; gebruik daarvoor `SILVER_DB` en/of `SILVER_SCHEMA` in `[settings]`.
- `[settings]` bevat o.a. `SILVER_SCHEMA`, optioneel `SILVER_DB` (MSSQL), `ASK_PASSWORD_IN_CLI`, en optioneel `SILVER_TABLE_NAME_CASE`/`SILVER_COLUMN_NAME_CASE` en `STAGING_NAME_MATCHING`/`STAGING_TABLE_NAME_CASE`.
	- Dialect-filtering van queries: `QUERY_ALLOWLIST` en/of `QUERY_DENYLIST` (komma/; gescheiden lijst van doeltabellen) om enkel de gewenste mappings uit te voeren. Namen matchen case-insensitief na normalisatie.

### Oracle (optioneel thick‑mode)

- Standaard gebruikt de driver `oracle+oracledb` thin‑mode. Voor thick‑mode (Instant Client) stel je een pad in via `DST_ORACLE_CLIENT_PATH` (in `[settings]` of als env var). Dit wordt vóór het opbouwen van de database‑verbinding geïnitialiseerd.
- Gebruik je een TNS‑alias, zet dan `DST_ORACLE_TNS_ALIAS=True` en vul de alias in bij `DST_HOST` (of `DST_DB`).

### Dialectondersteuning en write modes

- Alle queries draaien binnen één transactie. Het statement `SET CONSTRAINTS ALL DEFERRED` wordt alleen uitgevoerd op PostgreSQL; andere backends slaan dit over.
- Write modes per doel‑tabel: `append` (standaard), `overwrite`, `truncate`, `upsert`.
	- `upsert` is PostgreSQL‑only: op niet‑PostgreSQL backends geeft de pipeline een duidelijke foutmelding. Gebruik daar `append/overwrite/truncate`.
	- Per‑tabel write modes staan in `staging_to_silver/main.py` (dict `write_modes`).

#### Cross‑database (MSSQL)

- Staging staat in `DST_DB.DST_SCHEMA`. Je kunt de doeldatabase specificeren via `SILVER_DB`. Dit resulteert in drie‑delige kwalificatie: `[DB].[SCHEMA].[TABLE]`.
- Voor andere backends:
	- PostgreSQL ondersteunt geen cross‑database queries/tabel‑referenties; `SILVER_DB` wordt genegeerd met een waarschuwing.
	- MySQL/MariaDB zien “database” als “schema”; laat `SILVER_DB` leeg en gebruik `SILVER_SCHEMA` (of laat leeg) passend bij je setup.
	- Oracle gebruikt gebruikers als schema; connect als de juiste gebruiker en laat `SILVER_DB` leeg.

Destructieve init‑stap (`DELETE_EXISTING_SCHEMA`) wordt overgeslagen met een waarschuwing wanneer `SILVER_DB` verschilt van de verbonden database (`DST_DB`).

### Naam- en case-instellingen (bron vs. doel)

Er zijn vier instellingen die met “case” of naam-matching te maken hebben. Ze hebben elk een eigen rol:

- Bron (staging) matching tijdens reflectie:
	- `STAGING_NAME_MATCHING` – hoe we staging tabel‑/kolomnamen opzoeken:
		- `auto` (standaard): case‑insensitief zoeken met veilige fallbacks. Werkt robuust op Postgres/MSSQL waar casing kan verschillen (bijv. `wvbesl` en `WVBESL`).
		- `strict`: vereist exacte namen.
	- `STAGING_TABLE_NAME_CASE` – (optioneel) voorkeurscase bij het kiezen tussen meerdere kandidaten voor een brontabelnaam. Waarden: `upper` | `lower` | leeg (geen voorkeur). Dit is alléén een tiebreaker; in `auto` blijft matching case‑insensitief.
	- `STAGING_COLUMN_NAME_CASE` – (optioneel) voorkeurscase bij het opzoeken van bronkolommen. Waarden: `upper` | `lower` | leeg. In `auto` blijft matching case‑insensitief, maar exacte hits volgens de voorkeur krijgen voorrang.

- Doel (GGM) normalisatie tijdens laden:
	- `SILVER_TABLE_NAME_CASE` – normaliseert de sleutels van de geladen mappings (de namen van de GGM-doeltabellen) wanneer we de query-builders laden. Veelal `upper` zodat de mapping‑sleutels overeenkomen met de GGM‑DDL (BESCHIKKING, CLIENT, …).
	- `SILVER_COLUMN_NAME_CASE` – (optioneel) past de labels van de geselecteerde kolommen aan (upper/lower). Dit beïnvloedt alléén de aliasnamen in de SELECT‑projectie, niet de brontabelkolommen.
	- `SILVER_NAME_MATCHING` – bepaalt hoe kolommen van de doeltabel worden gematcht bij het bouwen van de INSERT ... SELECT:
		- `auto` (standaard): case‑insensitief matchen van doeltabel‑kolomnamen.
		- `strict`: vereis exacte namen.

Samengevat:
- `STAGING_NAME_MATCHING`/`STAGING_TABLE_NAME_CASE` en `STAGING_COLUMN_NAME_CASE` bepalen hoe wij de BRON (staging) tabellen/kolommen terugvinden tijdens reflectie en joins.
- `SILVER_TABLE_NAME_CASE`/`SILVER_COLUMN_NAME_CASE` en `SILVER_NAME_MATCHING` beïnvloeden hoe wij de DOEL‑kant (GGM) aanspreken en presenteren.

Alle vier staan onder `[settings]` in de `.ini` of in `.env`.

### Queries selecteren

Als je bepaalde queries wel/niet wil draaien, kan je gebruik maken van `QUERY_ALLOWLIST`/`QUERY_DENYLIST` om alleen
bepaalde queries te draaien.

### Configuratie-prioriteit

Prioriteit: INI > ENV > defaults, net als in `source_to_staging`.

### Sneller ontwikkelen met een rij‑limiet

Voor lokale ontwikkeling kun je een subset van de data verwerken door in `[settings]` `ROW_LIMIT` te zetten.
Dit limiet wordt toegepast op elke mapping (`SELECT … LIMIT n` of equivalent per dialect). Laat leeg of zet `0` om te uitschakelen.

## Optioneel: GGM‑tabellen aanmaken via SQL‑scripts

Je kunt vóór het uitvoeren van de mappings de GGM‑doeltabellen aanmaken door een map met `.sql`‑bestanden uit te voeren (bijv. de bestanden in `ggm_selectie/`). Dit is handig voor een snelle start of lokale demo.

Instellingen (sectie `[settings]`):

- `INIT_SQL_FOLDER` – pad naar een map met `.sql`‑bestanden. Als ingesteld, worden de scripts uitgevoerd vóór de mappings.
- `INIT_SQL_SUFFIX_FILTER` – standaard `True`. Als `True`, worden alleen bestanden met suffix `_<dialect>.sql` uitgevoerd, bv. `*_postgres.sql` voor PostgreSQL en `*_mssql.sql` voor SQL Server. Zet op `False` om alle `*.sql` te draaien.
- Schema voor de init‑scripts: we gebruiken altijd `SILVER_SCHEMA` (en waar van toepassing ook `SILVER_DB` op MSSQL). Voor PostgreSQL wordt het schema aangemaakt (indien nodig) en `search_path` daarop gezet. Voor MSSQL wordt het schema (best‑effort) aangemaakt en de default schema voor de huidige gebruiker gezet.
- `DELETE_EXISTING_SCHEMA` – standaard `False`. Als `True`, worden bestaande objecten in `SILVER_SCHEMA` eerst verwijderd. Op PostgreSQL gebeurt dit door het schema te droppen en opnieuw aan te maken (`DROP SCHEMA ... CASCADE`). Op andere backends reflecteren we de tabellen en droppen we ze in afhankelijkheidsvolgorde.

Opmerking:
- Oracle: schema's komen overeen met gebruikers; connect daarom als de gewenste gebruiker, of kwalificeer objectnamen expliciet. Bij MySQL/MariaDB is "schema" gelijk aan de database; zorg dat je met de juiste database verbonden bent.