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
Je kan ook via environment-variables configureren; zie voorbeeld
`staging_to_silver/.env.example`. 

Prioriteit bij configuratie is INI > ENV > defaults, net als in `source_to_staging`.

### Oracle (optioneel thick‑mode)

- Standaard gebruikt de driver `oracle+oracledb` thin‑mode. Voor thick‑mode (Instant Client) stel je een pad in via `DST_ORACLE_CLIENT_PATH` (in `[settings]` of als env var). Dit wordt vóór het opbouwen van de database‑verbinding geïnitialiseerd.
- Gebruik je een TNS‑alias, zet dan `DST_ORACLE_TNS_ALIAS=True` en vul de alias in bij `DST_HOST` (of `DST_DB`).

### Dialectondersteuning en write modes

- Alle queries draaien binnen één transactie. Het statement `SET CONSTRAINTS ALL DEFERRED` wordt alleen uitgevoerd op PostgreSQL; andere backends slaan dit over.
- Write modes per doel‑tabel: `append`, `overwrite` (standaard), `truncate`, `upsert`.
	- Standaard is de schrijfmodus per tabel `overwrite` wanneer je niets opgeeft.
	- `upsert` is PostgreSQL‑only: op niet‑PostgreSQL backends geeft de pipeline een duidelijke foutmelding. Gebruik daar `append/overwrite/truncate`.
	- Per‑tabel write modes configureer je via:
		1) Sectie `[write-modes]` in je `.ini`, met regels als `TABEL = append|overwrite|truncate|upsert`
		2) Of via de sleutel `WRITE_MODES` onder `[settings]` of als env var, met lijstnotatie: `WRITE_MODES = TABEL1=append, TABEL2=truncate; TABEL3=overwrite`
	- Matching is case‑insensitief; ongeldige waarden worden genegeerd met een waarschuwing.
	- Zie `staging_to_silver/config.ini.example` en `.env.example` voor voorbeelden.

### Cross‑database (MSSQL)

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

### Sneller testen/ontwikkelen met een rij‑limiet

Voor lokale ontwikkeling kun je een subset van de data verwerken door in `[settings]` `ROW_LIMIT` te zetten.
Dit limiet wordt toegepast op elke mapping (`SELECT … LIMIT n` of equivalent per dialect). Laat leeg of zet `0` om te uitschakelen.

### Optioneel: GGM‑tabellen automatisch aanmaken

Je kunt vóór het uitvoeren van de mappings de GGM‑doeltabellen aanmaken door een map met `.sql`‑bestanden uit te voeren (bijv. de bestanden in `ggm_selectie/`). Dit is handig voor een snelle start of lokale demo.

Instellingen (sectie `[settings]`):

- `INIT_SQL_FOLDER` – pad naar een map met `.sql`‑bestanden. Als ingesteld, worden de scripts uitgevoerd vóór de mappings.
- `INIT_SQL_SUFFIX_FILTER` – standaard `True`. Als `True`, worden alleen bestanden met suffix `_<dialect>.sql` uitgevoerd, bv. `*_postgres.sql` voor PostgreSQL en `*_mssql.sql` voor SQL Server. Zet op `False` om alle `*.sql` te draaien.
- Schema voor de init‑scripts: we gebruiken altijd `SILVER_SCHEMA` (en waar van toepassing ook `SILVER_DB` op MSSQL). Voor PostgreSQL wordt het schema aangemaakt (indien nodig) en `search_path` daarop gezet. Voor MSSQL wordt het schema (best‑effort) aangemaakt en de default schema voor de huidige gebruiker gezet.
- `DELETE_EXISTING_SCHEMA` – standaard `False`. Als `True`, worden bestaande objecten in `SILVER_SCHEMA` eerst verwijderd. Op PostgreSQL gebeurt dit door het schema te droppen en opnieuw aan te maken (`DROP SCHEMA ... CASCADE`). Op andere backends reflecteren we de tabellen en droppen we ze in afhankelijkheidsvolgorde.

Opmerking:
- Oracle: schema's komen overeen met gebruikers; connect daarom als de gewenste gebruiker, of kwalificeer objectnamen expliciet. Bij MySQL/MariaDB is "schema" gelijk aan de database; zorg dat je met de juiste database verbonden bent.

## Queries schrijven (GGM-mappings)

Dit is de minimale en robuuste manier om een mapping‑query te definiëren. Het doel is dat je query bestandloos, case‑bestendig en dialect‑neutraal blijft, terwijl de loader alles netjes naar de doeltabellen projecteert.

### In het kort

- Plaats je module in `staging_to_silver/queries/YourTable.py`.
- Exporteer een dict `__query_exports__ = {"DEST_TABLE": builder}`.
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

### Kolomnamen en case

- Label je kolommen altijd met de doeltabel‑namen. De pipeline kan labels optioneel normaliseren via `SILVER_COLUMN_NAME_CASE` (`upper|lower`).
- Het matchen naar de doeltabel gebeurt in `main.py`:
	- De loader leest jouw labelvolgorde, zoekt de corresponderende doelkolommen (case‑insensitief tenzij `SILVER_NAME_MATCHING=strict`) en bouwt `INSERT ... SELECT`.
	- Ontbreekt een kolom in de doeltabel, dan volgt een duidelijke foutmelding met de beschikbare kolommen.

### Tips & valkuilen

- Selecteer alleen de kolommen die je wilt laden; ontbrekende doorkolommen moeten op de doeltabel defaults of `NULL` toelaten.
- Gebruik `cast(literal(None), Type).label("DOELKOL")` om verplichte doorkolommen tijdelijk te vullen wanneer bronwaarden ontbreken.
- Houd joins klein en reflecteer alleen benodigde tabellen: `reflect_tables` accepteert een smalle lijst met basisnamen.
- In `STAGING_NAME_MATCHING=strict` moeten tabel‑ en kolomnamen exact kloppen; handig om inconsistenties in staging te detecteren.
- `upsert` als write‑mode is alleen voor PostgreSQL en vereist een primaire sleutel op de doeltabel.
