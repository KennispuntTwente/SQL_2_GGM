# staging_to_silver

Deze module verbindt met de SQL-server waarop data uit de applicatie is gedumpt in de eerdere module (sql_to_staging),
en vormt deze via SQL-queries om naar de structuur van het gemeentelijk gegevensmodel (GGM). 

De module verbindt met de SQL-server en voert queries uit die de 'source'-data ('brons') omvornen naar het GGM ('zilver').
Deze queries zijn gedefinieerd in SQLAlchemy zodat ze op verschillende typen SQL-servers kunnen werken.
De SQL-queries zijn in feite de GGM-mappings, direct ook in de vorm van uitvoerbare code.

Van belang is dat dus sql_to_staging reeds is uitgevoerd, en ook dat er een database is waar de (lege) tabellen
van het gemeentelijk gegevensmodel op staan (zie map: ggm_selectie). Deze module kan eventueel ook de SQL-code uitvoeren
om GGM-tabellen aan te maken (zie sectie: "GGM-tabellen automatisch aanmaken").

> Tip: de GGM-DDL (SQL-code om de tabellen aan te maken) is te vinden in de map `ggm_selectie/`. Je kan deze aanpassen naar
wens, bijv., door bepaalde tabellen of kolommen te verwijderen die je niet nodig hebt. In ons project hebben we er met name
voor gekozen om constraints te verwijderen, zodat data geladen kan worden zonder dat deze per se aan alle constraints hoeft te voldoen.
In de stap richting een 'gold' laag kunnen deze constraints eventueel alsnog worden afgedwongen.

In sectie "Configuratie" wordt uitgelegd hoe deze module te configureren. In sectie "Queries schrijven" wordt uitgelegd
hoe je zelf queries kan schrijven om data uit de applicatie te ontsluiten naar het GGM.

(Voor uitleg van commands om deze module te runnen met configuratie, zie de `README.md` in de root van de repository; sectie "Uitvoeren".)

(Als je deze module wil uitproberen met synthetische data en zonder productie-database, zie de demo-scripts in `staging_to_silver/demo/`.)

## Configuratie

`staging_to_silver` gebruikt één INI-bestand (`--config`) met secties `[database-destination]`, `[settings]` en optioneel `[logging]`.
Een voorbeeld staat in `staging_to_silver/config.ini.example`.
Je kan ook via environment-variables configureren; zie voorbeeld
`staging_to_silver/.env.example`. 
Prioriteit bij configuratie is INI > environment variables > standaard-waardes.

Hieronder staat verder toegelicht wat de verschillende opties doen. 
Er staat ook beknopte toelichting in de voorbeeld-configuratiebestanden 
(`staging_to_silver/config.ini.example` en `staging_to_silver/.env.example`).

### Wegschrijfmodus ('write mode')

Je kan op verschillende manieren de uit 'staging' geselecteerde
data toevoegen aan de tabellen in 'silver': 

- `overwrite` (standaard): wist eerst alle bestaande rijen uit de doeltabel (DELETE) en laadt daarna de nieuwe set; volledig transactieel en triggert eventuele delete/insert‑triggers.
- `append`: voegt nieuwe rijen toe zonder bestaande rijen te wijzigen; kan duplicaten geven als je mapping niet incrementeel is.
- `truncate`: leegt de doeltabel met TRUNCATE TABLE (of DELETE op SQLite) en laadt daarna opnieuw; meestal sneller, reset vaak identity/tellingen en activeert doorgaans geen rij‑triggers.
- `upsert` (alleen voor Postgres): insert‑of‑update op basis van de primaire sleutel (ON CONFLICT DO UPDATE); vereist een primaire sleutel op de doeltabel.

### Databases & schema's

Verschillende SQL-server-types gaan verschillend om met wat “database” en “schema” betekenen.
Per type wordt het hier uitgelegd alsmede hoe zich dit verhoudt tot de opties voor deze module:

- SQL Server (MSSQL)
	- Database = logische database (`DST_DB`); schema = namespace binnen die database (`DST_SCHEMA`).
	- Staging en silver worden aangesproken als `[DB].[SCHEMA].[TABLE]`.
	- Je kunt de doeldatabase voor silver apart zetten met `SILVER_DB`; de kwalificatie wordt dan `[SILVER_DB].[SILVER_SCHEMA].[TABLE]`. Als `SILVER_DB` leeg is, gebruiken we `DST_DB`.
	- Bij initialisatie (met `INIT_SQL_FOLDER`) maken/gebruiken we `SILVER_SCHEMA` (in `SILVER_DB` indien gezet).

- PostgreSQL
	- Database = cluster‑database; schema = namespace binnen die database.
	- Cross‑database is niet mogelijk; `SILVER_DB` wordt genegeerd (we gebruiken altijd de verbonden database `DST_DB`) en er wordt een waarschuwing gelogd.
	- Gebruik `SILVER_SCHEMA` voor het schema; dit wordt indien nodig aangemaakt en als `search_path` ingesteld tijdens initialisatie.

- MySQL/MariaDB
	- “Database” en “schema” zijn synoniemen; objecten worden als `database.table` aangesproken.
	- Verbind met de juiste database via `DST_DB`. Laat `SILVER_DB` leeg.
	- Gebruik `SILVER_SCHEMA` om (effectief) de doeldatabase te benoemen (gelijk aan de database‑naam), of laat leeg om de standaard database te gebruiken.

- Oracle
	- Schema = gebruiker; objecten staan onder de ingelogde gebruiker.
	- Verbind als de juiste gebruiker en laat `SILVER_DB` leeg.
	- `SILVER_SCHEMA` kun je gebruiken om expliciet een ander schema te kwalificeren (mits je rechten hebt); standaard gebruiken we de huidige gebruiker.

Destructieve init‑stap (`DELETE_EXISTING_SCHEMA`) wordt overgeslagen met een waarschuwing wanneer `SILVER_DB` verschilt van de verbonden database (`DST_DB`).

### Naam- en case-instellingen

Bij het aanmaken van tabellen kan het op sommige SQL-server-types voorkomen dat deze, mogelijk onverwacht,
tabel- en kolomnamen in upper-/lowercase zetten. Daarom kan de model soepel omgaan  met tabel- en kolomnamen:
er kan eerst worden gezocht naar een exacte match, en dan naar een match die niet de exacte case volgt.

Samengevat:
- `STAGING_NAME_MATCHING`/`STAGING_TABLE_NAME_CASE` en `STAGING_COLUMN_NAME_CASE` bepalen hoe wij de staging ('brons') tabellen/kolommen terugvinden in de queries (d.w.z., selectie van data)
- `SILVER_TABLE_NAME_CASE`/`SILVER_COLUMN_NAME_CASE` en `SILVER_NAME_MATCHING` beïnvloeden waar wij het doel (GGM-tabellen/'silver') vinden (d.w.z., waar de geselecteerde data wordt geplaatst)

### Queries selecteren

Je kan bepalen van waar queries worden geladen met de settings `QUERY_PATHS`. Standaard is dit `staging_to_silver/queries/cssd/`.
Als je een eigen/extra map met queries wil gebruiken, kun je die hier toevoegen (komma-gescheiden lijst van paden).

Als je bepaalde queries wel/niet wil draaien, kan je verder nog gebruik maken van `QUERY_ALLOWLIST`/`QUERY_DENYLIST` om alleen
bepaalde queries te draaien.

### Sneller testen/ontwikkelen met een rij‑limiet ('row limit')

Voor lokale ontwikkeling kun je een subset van de data verwerken door in `[settings]` `ROW_LIMIT` te zetten.
Deze limiet wordt toegepast op elke mapping (`SELECT … LIMIT n` of equivalent per dialect). Laat leeg of zet `0` om te uitschakelen.

### GGM‑tabellen automatisch aanmaken (vooraf SQL-code uitvoeren)

Je kunt vóór het uitvoeren van de mappings de GGM‑doeltabellen aanmaken door een map met `.sql`‑bestanden uit te voeren (bijv. de bestanden in `ggm_selectie/`). 
Hiermee kan de module ook de GGM-tabellen aanmaken, als ze nog niet bestaan op je server.

Instellingen hiervoor (sectie `[settings]`):
- `INIT_SQL_FOLDER` – pad naar een map met `.sql`‑bestanden. Als ingesteld, worden de scripts uitgevoerd vóór de mappings.
- `INIT_SQL_SUFFIX_FILTER` – standaard `True`. Als `True`, worden alleen bestanden met suffix `_<dialect>.sql` uitgevoerd, bv. `*_postgres.sql` voor PostgreSQL en `*_mssql.sql` voor SQL Server. Zet op `False` om alle `*.sql` te draaien.
- Schema voor de init‑scripts: we gebruiken altijd `SILVER_SCHEMA` (en waar van toepassing ook `SILVER_DB` op MSSQL). Voor PostgreSQL wordt het schema aangemaakt (indien nodig) en `search_path` daarop gezet. Voor MSSQL wordt het schema (best‑effort) aangemaakt en de default schema voor de huidige gebruiker gezet.
- `DELETE_EXISTING_SCHEMA` – standaard `False`. Als `True`, worden bestaande objecten in `SILVER_SCHEMA` eerst verwijderd. Op PostgreSQL gebeurt dit door het schema te droppen en opnieuw aan te maken (`DROP SCHEMA ... CASCADE`). Op andere backends reflecteren we de tabellen en droppen we ze in afhankelijkheidsvolgorde.

Opmerking:
- Oracle: schema's komen overeen met gebruikers; connect daarom als de gewenste gebruiker, of kwalificeer objectnamen expliciet. Bij MySQL/MariaDB is "schema" gelijk aan de database; zorg dat je met de juiste database verbonden bent.

## Queries schrijven (GGM-mappings)

Als je zelf queries wil schrijven om data vanuit de applicatie te 'mappen' naar het GGM, kan dat met SQLAlchemy.
We gebruiken enkele custom functies bovenop SQLAlchemy om bijvoorbeeld te zorgen dat tabel- en kolomnamen goed worden
gematcht tussen verschillende SQL-server-types. Daarnaast moeten de queries in een bepaald format staan zodat
ze goed kunnen worden ingeladen door deze module.

Hieronder staat uitgelegd hoe je zelf je queries kan schrijven. Je kan ook naar de voorbeelden in de map `staging_to_silver/queries/cssd` kijken.

### Basis

Het doel is dat je query bestandloos, case‑bestendig en dialect‑neutraal blijft, terwijl de loader alles netjes naar de doeltabellen projecteert.

- Plaats je query in een bestand als `staging_to_silver/queries/cssd/YourTable.py` (of in een eigen submap voor een andere applicatie).
- Exporteer hierin een dict `__query_exports__ = {"DEST_TABLE": builder}`.
	- `DEST_TABLE` is de doeltabelnaam zoals in GGM. De loader normaliseert de sleutel met `SILVER_TABLE_NAME_CASE` (standaard `upper`).
- `builder(engine, source_schema=None) -> sqlalchemy.sql.Select`
	- Bouw een SQLAlchemy `select(...)` en label alle projecties met de doeltabel‑kolomnamen in de gewenste volgorde.
	- De loader reflecteert de doeltabel en matcht kolommen case‑insensitief (tenzij `SILVER_NAME_MATCHING=strict`). De insert gebruikt de volgorde van jouw labels.
	- Je mag een subset van kolommen laden (mits de rest defaults/nulls heeft); de kolomlijst aan de INSERT wordt exact afgeleid van de labels in jouw select.

### Helpers bovenop SQLAlchemy

Importeer de case‑bewuste helpers:

- `reflect_tables(engine, source_schema, base_names)`
	- Reflecteert de genoemde brontabellen naar een `MetaData`, met tolerantie voor case‑verschillen. Respecteert:
		- `STAGING_NAME_MATCHING` = `auto` (case‑insensitief) | `strict` (exact).
		- `STAGING_TABLE_NAME_CASE` als voorkeur bij meerdere varianten (`upper`/`lower`).
- `get_table(metadata, source_schema, base_name, required_cols=[...])`
	- Zoekt één `Table` met case‑insensitieve fallback en optionele voorkeur op kolom‑set (handig als er meerdere gelijkende tabellen bestaan). Respecteert dezelfde opties als hierboven en `STAGING_COLUMN_NAME_CASE` bij kolomresolutie.
- `col(table, "kolomnaam")`
	- Haalt een kolom op met case‑insensitieve matching en voorkeur (`STAGING_COLUMN_NAME_CASE=upper|lower`). In `strict` modus is een exacte hit vereist.

Deze helpers zorgen ervoor dat je query’s op PostgreSQL, SQL Server, SQLite (voor shapetests) en andere backends blijven werken zonder te vechten met naamgeving/casing in de staging.

### Voorbeeld: eenvoudige mapping

```
from sqlalchemy import select, cast, literal, String
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col

def build_client(engine, source_schema=None):
		# 1) Reflecteer alleen wat je nodig hebt
		metadata = reflect_tables(engine, source_schema, ["szclient"])
		szclient = get_table(metadata, source_schema, "szclient", required_cols=["clientnr", "ind_gezag"]) 

		# 2) Projecteer naar doelnamen; labels bepalen de insert‑kolommen en volgorde
		return select(
				col(szclient, "clientnr").label("RECHTSPERSOON_ID"),
				col(szclient, "ind_gezag").label("GEZAGSDRAGERGEKEND_ENUM_ID"),
				cast(literal(None), String(80)).label("CODE"),
		).select_from(szclient)

__query_exports__ = {"CLIENT": build_client}
```

### Voorbeeld: joins en dialect‑specifiek gedrag

Gebruik waar nodig `engine.dialect.name` om kleine verschillen af te handelen en `Column.op("...")` voor vendor‑operators:

```
from sqlalchemy import select, and_, or_, func, cast, Date, literal
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col

def _local_date_amsterdam(ts_col, engine):
		d = (engine.dialect.name or "").lower()
		if d == "mssql":
				return cast(ts_col.op("AT TIME ZONE")("UTC").op("AT TIME ZONE")("W. Europe Standard Time"), Date)
		elif d.startswith("postgres"):
				return cast(func.timezone("Europe/Amsterdam", func.timezone("UTC", ts_col)), Date)
		else:
				return cast(ts_col, Date)

def build_beschikte_voorziening(engine, source_schema=None):
		md = reflect_tables(engine, source_schema, ["wvind_b", "szregel"]) 
		wvind_b = get_table(md, source_schema, "wvind_b")
		szregel = get_table(md, source_schema, "szregel")

		return (
				select(
						_local_date_amsterdam(col(wvind_b, "dd_begin"), engine).label("datumstart"),
						col(wvind_b, "volume").label("omvang"),
						func.concat(col(wvind_b, "besluitnr"), col(wvind_b, "volgnr_ind")).label("beschikte_voorziening_id"),
						literal(None).label("code"),
				)
				.select_from(wvind_b)
				.outerjoin(szregel, col(wvind_b, "kode_regeling") == col(szregel, "kode_regeling"))
		)

__query_exports__ = {"BESCHIKTE_VOORZIENING": build_beschikte_voorziening}
```
