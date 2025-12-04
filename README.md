# SQL_2_GGM

'SQL_2_GGM' is een open-source Python-tool om data uit diverse
applicaties 1) te ontsluiten en 2) te transformeren
naar structuur van het [Gemeentelijk Gegevensmodel (GGM)](https://www.gemeentelijkgegevensmodel.nl/v2.4.0/). 

Voor het 1) ontsluiten van data bevat dit project twee modules: 'sql_to_staging' en 'odata_to_staging', welke respectievelijk
data ontsluiten uit een SQL-server (diverse types) of een OData-API, en deze data plaatsen in een 'staging' database
op een SQL-server (diverse types) waarop het GGM zal staan.

Voor het 2) transformeren van data is er de module 'staging_to_silver', welke de applicatie-data via SQL-queries transformeert
naar het GGM. Deze SQL-queries worden in SQLAlchemy geschreven, zodat verschillende typen SQL-servers
ondersteund worden (bijv., Oracle, Postgres, Microsoft SQL Server, MySQL, etc.).

Met deze modules wordt een volledige technische uitwerking geleverd van het proces om data uit een applicatie te overbrengen naar het GGM.
In tegenstelling tot het delen van alleen mapping-documenten (die je zelf nog moet implementeren in je eigen ETL-tool), kan code van en voor deze tool direct gebruikt worden. Inzet is om zoveel mogelijk
'plug-and-play' functionaliteit te bieden die compatibel is met diverse SQL-server types, zodat deze tool breed inzetbaar is.
Daarmee kan het GGM gemakkelijker geïmplementeerd worden en wordt verdergaande samenwerking tussen gemeenten mogelijk.

> Specifiek bevat deze repository daarnaast SQL-queries om data uit de applicatie Centric Suite 4 Sociaal Domein (SSD)
te transformeren naar het GGM. De modules kunnen echter geconfigureerd worden om gegevens uit elke andere applicatie
met een SQL-server/OData-API te onsluiten en/of te modelleren naar het GGM.

---

> **Status van dit project (28/10/2025)**: *dit project is nabij afronding maar nog in ontwikkeling.
Enkele queries voor de transformatie van SSD-data in 'staging_to_silver' vereisen bijvoorbeeld mogelijk nog wijzigingen.
Een GitHub-release zal binnenkort worden uitgegeven wanneer bevestigd is dat alle huidige queries functioneren.
In mogelijke toekomstige releases wordt de set queries uitgebreid naar meer tabellen die voorkomen in het GGM en ontsloten kunnen worden uit SSD dan wel andere applicaties.*

## Overzicht

Hieronder staat beschreven hoe data vanuit de applicatie wordt overgebracht naar het GGM.

### Van applicatie naar staging ('sql_to_staging'/'odata_to_staging')

Door de 'client' (d.w.z., machine waarop Python-code in dit project draait),
wordt verbonden met de applicatie-SQL-server of OData-API waarin de data van de applicatie staat (voor SSD is dit een
Oracle-database; zou ook een ander type kunnen zijn).

De client downloadt de relevante tabellen uit de applicatie
en uploadt deze naar de target-SQL-server waarop het GGM zal staan.
(kan verschillende types zijn, bijv., Postgres, Microsft SQL Server,
MySQL, etc.). De upload vindt plaats naar een 'staging' (oftewel 'brons') database
binnen de target-SQL-server. Wanneer deze stap is afgerond staat dus de data uit de applicatie, nog in de originele structuur, nu op de target-SQL-server.

Bij de download & upload wordt er voor gezorgd dat 'larger-than-memory' data ook verwerkt kan worden.
Dit d.m.v. chunking van de data; chunks worden gestreamd in het werkgeheugen van de client of kunnen
tijdelijk worden gedumpt naar parquet-bestanden op de schijfruimte van de client. Zo kunnen grote hoeveelheden
data worden verwerkt ondanks een beperkt werkgeheugen van de client.

> Zie [sql_to_staging/README.md](sql_to_staging/README.md) 
(ontsluiting uit SQL-server) en [odata_to_staging/README.md](odata_to_staging/README.md) (ontsluiting uit OData-API)
voor meer informatie over deze stap.

### Van staging naar het GGM ('staging_to_silver')

Op dit punt staat de data in de structuur van de applicatie ('brons') op de SQL-server.
Op  deze SQL-server staat ook de (lege) tabellenstructuur van het GGM ('silver'). 
Om de GGM-tabellenstructuur aan te maken, voer je zelf de SQL-code zoals deze uit de
DDL van Delft gegenereerd wordt (zie map: ggm_selectie en/of map: ggm).

De client verbindt in deze stap met de SQL-server en geeft opdracht tot queries.
Die queries worden vewerkt door de SQL-server. De queries zijn uitgewerkt
in SQLAlchemy; dit is Python-code die erg lijkt op SQL, die vertaald kan worden
naar de verschillende SQL-dialecten die er zijn (bijv., Postgres heeft een net andere
versie van SQL dan bijv. Microsoft SQL Server; door de queries met SQLAlchemy te schrijven
kunnen we gemakkelijk werken met diverse SQL-server-types) 
(voor de queries voor SSD, zie map: staging_to_silver/queries).

Nadat de SQL-server de queries heeft verwerkt staat de data in het GGM!

> Zie [staging_to_silver/README.md](staging_to_silver/README.md) voor meer informatie over deze stap.

## Installatie & gebruik

Er zijn twee manieren om dit project uit te voeren: met een eigen Python-omgeving, of met behulp van Docker. Docker biedt een virtuele omgeving waarin alle benodigde software (zoals de code en een complete Python-omgeving) al is opgenomen. Docker kan veel gemak bieden, omdat je zelf minder hoeft te installeren en je verzekerd bent van een stabiele, reproduceerbare werkomgeving.

Waar je de code runt kan je vervolgens zelf kiezen. Je dient de code te runnen in een omgeving waarin de client waarop
je de code runt verbinding kan maken met zowel de SQL-server van de applicatie als de SQL-server waarop je het GGM hebt.
Dit zou kunnen op een eigen machine, op een eigen server (on-premises), of bijvoorbeeld in een cloud-omgeving (bijv., Azure).
Je zou bijvoorbeeld een scheduler (oftewel CRON-job) kunnen instellen welke het proces elke nacht draait.

> Tip: wil je de code gemakkelijk uitproberen zonder te verbinden met een productie-database? Zie dan
de demo-scripts: [sql_to_staging/demo/README.md](sql_to_staging/demo/README.md) en
[staging_to_silver/demo/README.md](staging_to_silver/demo/README.md). Hierbij wordt synthetische data gegenereerd,
geladen, en getransformeerd naar het GGM (in een ontwikkel-database in Docker/Podman; maar je kan de scripts ook aanpassen
om een andere database te gebruiken).

### Snel starten met Docker (geen lokale Python nodig)

De snelste manier om de volledige pipeline uit te proberen zonder Python lokaal te installeren:

```bash
bash docker/demo/run_demo.sh
```

Dit start een PostgreSQL database, genereert synthetische data, en draait zowel `sql_to_staging` als `staging_to_silver`.
Zie [docker/demo/README.md](docker/demo/README.md) voor configuratie-opties (bijv. verbinden met je eigen database).

### Vanuit eigen Python-omgeving

#### Installatie

Installeer eerst '[uv](https://docs.astral.sh/uv/)'. 'uv' is een tool voor het beheren van Python-omgevingen en packages.
Run dan `uv sync` in deze map om de benodigde Python-omgeving en packages te installeren naar de lockfile (zie: [uv.lock](uv.lock)).

```
uv sync
```

Zorg daarna dat je in je IDE (bijv. VSCode) de Python-interpreter hebt ingesteld die hoort bij de '.venv' die door `uv sync` is aangemaakt
(gebruik in VSCode: CTRL+SHIFT+P, dan 'Python: Select Interpreter').

#### Virtual environment activeren

Bij gebruik moet je de virtual environment van dit project geactiveerd hebben. In sommige IDEs gaat dat automatisch.
Als de virtual environment geactiveerd is, zie je '(ggmpilot)' in je terminal staan. Mocht je je virtual environment 
moeten activeren, run dan:

```
.venv\Scripts\activate
```

#### Configuratie

Je kan instellingen voor modules op twee manieren doen: via environment variables & via de .ini-bestanden.
Via beide bestanden kan je dezelfde instellingen doen.

De `.env.example` en `config.ini.example` bestanden tonen welke instellingen er zijn.
Als je gebruik wil maken van enviroment variables, kan je 1) op de reguliere manier
environment variables instellen op je systeem; of 2) een `.env` bestand aanmaken
naar de structuur van `.env.example` (in dezelfde map). Hetzelfde geldt voor de `config.ini.example`
bestanden: zet een `config.ini` bestand neer in dezelfde map met dezelfde structuur.

Prioriteit bij configuratie is: .ini > environment variables > standaardwaarden. 
Aangeraden wordt om één manier van configuratie te kiezen (.ini of environment variables).

(Als je verdergaande configuratie wil doen, kan dat door de Python-scripts aan te passen.
Zie ook sectie 'Een eigen versie van dit project gebruiken'). 

#### Uitvoeren

Vervolgens kan je de Python-scripts uitvoeren. Zie de voorbeelden hieronder:

1. Run sql_to_staging (geconfigureerd via environment variables)

```
python -m sql_to_staging.main
```

2. Run sql_to_staging (geconfigureerd via .ini-bestand)

```
python -m sql_to_staging.main --config sql_to_staging/config.ini
```

3. Run staging_to_silver (geconfigurerd via environment variables)

```
python -m staging_to_silver.main
```

4. Run staging_to_silver (geconfigurerd via .ini-bestand)
```
python -m staging_to_silver.main --config staging_to_silver/config.ini
```

### Vanuit Docker

Deze repository bevat een Dockerfile die beide modules kan draaien via één image.

Installeer eerst Docker (of alternatief: Podman) en zorg dat de Docker-daemon draait (bijv., door Docker Desktop te starten).

1) Build de image

```bash
docker build -t ggmpilot:latest .
```

2) Run sql_to_staging met environment variables (in .env):

```bash
# gebruikt standaard PIPELINE=source-to-staging
docker run --rm \
	-v "$(pwd)/data:/app/data" \
	-v "$(pwd)/sql_to_staging:/app/sql_to_staging" \
	--env-file sql_to_staging/.env  \
	ggmpilot:latest
```

3) Run sql_to_staging met .ini-config:

```bash
docker run --rm \
	-v "$(pwd)/data:/app/data" \
	-v "$(pwd)/sql_to_staging:/app/sql_to_staging" \
	ggmpilot:latest source-to-staging \
		--config /app/sql_to_staging/config.ini
```

4) Run staging_to_silver met environment variables (in .env):

```bash
docker run --rm \
	-v "$(pwd)/staging_to_silver:/app/staging_to_silver" \
	--env-file staging_to_silver/.env \
	ggmpilot:latest staging-to-silver
```

5) Run staging_to_silver met .ini-config:

```bash
docker run --rm \
	-v "$(pwd)/staging_to_silver:/app/staging_to_silver" \
	ggmpilot:latest staging-to-silver \
	-- -c /app/staging_to_silver/config.ini
```

Tips/opmerkingen:
- SQL-server op de host benaderen: gebruik in je configuratie `host.docker.internal` als hostnaam 
(anders wordt geprobeerd om een SQL-server binnen de Docker-image te benaderen, wat dan mislukt)
- Bestanden bewaren: parquet-dumps worden standaard in /app/data geschreven; mount die map lokaal met -v "$(pwd)/data:/app/data" als je de bestanden wil bewaren (en zet optie 'CLEANUP_PARQUET_FILES' uit)
- SQL Server (pyodbc): deze image bevat unixODBC maar niet de Microsoft ODBC driver (msodbcsql17/msodbcsql18). Voeg deze zelf toe of maak een afgeleide image wanneer je mssql via ODBC gebruikt.
- Oracle: de image gebruikt oracledb in thin‑mode. Voor thick‑mode (Instant Client) mount de client en zet de juiste pad‑variabele in je .env of .ini: SRC_ORACLE_CLIENT_PATH (bron, sql_to_staging) of DST_ORACLE_CLIENT_PATH (doel, staging_to_silver).
- Proxy/certificaten: plaats certificaten in een volume en exporteer de juiste env vars (bijv. REQUESTS_CA_BUNDLE) als je die nodig hebt.

## Informatie voor ontwikkelaars

### Uitvoeren met synthetische data

Wil je de code uitvoeren zonder dat je een applicatie-SQL-server hebt met data?
Dan kan je synthetische data genereren met de module in de map `synthetic`.
Zie de [sql_to_staging/demo/README.md](sql_to_staging/demo/README.md), [staging_to_silver/demo/README.md](staging_to_silver/demo/README.md),
en [synthetic/README.md](synthetic/README.md) voor voorbeelden van demo-scripts die synthetische data genereren, laden, en verwerken.
Ook [odata_to_staging/demo/README.md](odata_to_staging/demo/README.md) bevat een demo-script voor die module.

### Een eigen versie van dit project gebruiken

Dit project is zoveel mogelijk ingericht om een 'plug-and-play' toepassing van het GGM te zijn;
het is geschikt voor meerdere typen databases, en bevat code voor de volledige conversie van
gegevens uit de applicatie naar de structuur van het GGM. 

Desondanks kan het nodig zijn om aanpassingen te doen aan deze code. Bijvoorbeeld,
als je een andere (grotere, of juist kleinere) selectie tabellen wil overbrengen naar
het GGM. Of als jouw gemeente op bepaalde manier afwijkt van de structuur van het GGM.

In dat soort situaties is het gewenst om met 'git' (= software voor versiebeheer,
die wijzigingen in bestanden bijhoudt) een eigen 'clone' (dan wel 'fork') te maken
van deze repository. In die eigen versie kan je dan wijzigingen maken welke je
bijhoudt met git. Als er later updates worden gedaan aan dit project, kan je die updates,
ook met git, weer samenvoegen met jouw versie van dit project. Zo kan je dus 
een eigen, afwijkende versie hebben maar toch ook updates van dit project meekrijgen. 

### Tests

Om de kwaliteit van de code te verifiëren & te bewaken, bevat dit project tests.
Tests worden automatisch gerund op GitHub Actons (zie map: .github/workflows).
Daarnaast kan je tests ook in je eigen ontwikkeomgeving uitvoeren; zie uitleg hieronder.

#### pytest (slow & fast tests)

De map `tests/` en `.../tests/` (in submappen bevatten diverse tests in het pytest-framework.

Enkele tests (`test_integration_*.py`; gemarkeerd als 'slow') vereisen
dat je Docker (dan wel Podman) beschikbaar hebt op je machine (er worden namelijk
diverse database-types gerund in Docker). De Docker-daemon moet dus draaien op je machine.
Omdat deze tests traag zijn, is daarnaast ook nodig 
dat je de environment variables `RUN_SLOW_TESTS=1` bevatten (anders worden ze geskipt).

#### Docker Compose (smoke test)

De Docker-image wordt getest d.m.v. enkele 'smoke' runs in Docker Compose.
Zie hiervoor de map: docker. Om alle smoke test in één keer te runnen, 
kan je het volgende commando runnen (bash):

```bash
docker/smoke/run_all.sh
```

## Contact & team

Heb je vragen over dit project? Loop je tegen problemen aan? Of wil je samenwerken?
Neem contact op! De volgende organisaties & personen zijn betrokken bij dit project: 

**Kennispunt Twente**: 
- Luka Koning (l.koning@kennispunttwente.nl)
- Jos Quist (j.quist@kennispunttwente.nl)
- Hüseyin Seker (h.seker@kennispunttwente.nl)

**Gemeente Rijssen-Holten**: 
- Fabian Klaster (f.klaster@rijssen-holten.nl)
- Rien ten Hove (r.tenhove@rijssen-holten.nl)
- Joop Voortman (j.voortman@rijssen-holten.nl)

**Gemeente Oldenzaal**: 
- Joost Barink (j.barink@oldenzaal.nl)
- Odylia Luttikhuis (o.luttikhuis@oldenzaal.nl)

---

Voor technische vragen: neem contact op met Luka Koning en Joost Barink. Je mag ons mailen, maar kan ook een issue openen in de [GitHub-repository](https://github.com/KennispuntTwente/SQL_2_GGM/issues).

Voor vragen inzake (gemeentelijke) samenwerking: neem contact op met Jos Quist, Fabian Klaster en Joost Barink. Hiervoor graag per mail contact opnemen.
