# SQL_2_GGM

Deze repository bevat code om gegevens uit diverse SQL-servers te ontsluiten en onder te brengen
in de structuur van het [Gemeentelijk Gegevensmodel (GGM)](https://www.gemeentelijkgegevensmodel.nl/v2.4.0/).

Specifiek bevat deze repository een ontsluiting van data uit de applicatie Centric Suite 4 Sociaal Domein (SSD),
naar tabellen van het GGM over beschikkingen en voorzieningen in het sociaal domein. De modules kunnen echter
geconfigureerd worden om gegevens uit elke andere applicatie met een SQL-server te onsluiten en te modelleren
naar het GGM. 

Omdat deze tool geheel open-source is, kan elke gemeente deze toepassen. Voor gemeenten die dezelfde data
uit SSD willen ontsluiten, is deze tool zo veel als mogelijk 'plug-and-play' gemaakt (d.w.z., niet alleen de mapping wordt
geleverd; ook de technische uitwerking van de mapping in Python-code).

---

**Status van dit project (28/10/2025)**: *dit project is nabij afronding maar nog in ontwikkeling.
Enkele queries in 'staging_to_silver' vereisen bijvoorbeeld mogelijk nog wijzigingen.
Een GitHub-release zal binnenkort worden uitgegeven wanneer bevestigd is dat alle huidige queries functioneren.
In mogelijke toekomstige releases wordt de set queries uitgebreid naar meer tabellen die voorkomen in het GGM en ontsloten kunnen worden uit CSDD.*

## Overzicht

Hieronder staat beschreven hoe data vanuit de applicatie wordt overgebracht naar het GGM.

### Van applicatie naar staging ('source_to_staging')

Door de 'client' (d.w.z., machine waarop Python-code in dit project draait),
wordt verbonden met de applicatie-SQL-server waarin de data van de applicatie staat (in dit geval een 
Oracle-database; zou ook een ander type database kunnen zijn).

De client downloadt de relevante tabellen van de applicatie-SQL-server (is in principe een OracleDB;
maar kan ook een ander type zijn) en uploadt deze tabellen naar de target-SQL-server. De target-SQL-server
is de SQL-server waarop het GGM zal staan (kan verschillende types zijn, bijv., Postgres, Microsft SQL Server,
MySQL, etc.). De upload vindt plaats naar een 'staging' (oftewel 'brons') database
binnen de target-SQL-server. Wanneer deze stap is afgerond staat dus de data uit de
applicatie-SQL-server, nog in de originele structuur, nu op de target-SQL-server.

Bij de download & upload wordt er voor gezorgd dat 'larger-than-memory' data ook verwerkt kan worden.
Dit d.m.v. chunking van de data; chunks worden gestreamd in het werkgeheugen van de client of kunnen
tijdelijk worden gedumpt naar parquet-bestanden op de schijfruimte van de client. Zo kunnen grote hoeveelheden
data worden verwerkt ondanks een beperkt werkgeheugen van de client.

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
(voor de queries, zie map: staging_to_silver/queries).

Nadat de SQL-server de queries heeft verwerkt staat de data in het GGM!

## Installatie & gebruik

Er zijn twee manieren om dit project uit te voeren: met een eigen Python-omgeving, of met behulp van Docker. Docker biedt een virtuele omgeving waarin alle benodigde software (zoals de code en een complete Python-omgeving) al is opgenomen. Docker kan veel gemak bieden, omdat je zelf minder hoeft te installeren en je verzekerd bent van een stabiele, reproduceerbare werkomgeving.

Waar je de code runt kan je vervolgens zelf kiezen. Je dient de code te runnen in een omgeving waarin de client waarop
je de code runt verbinding kan maken met zowel de SQL-server van de applicatie als de SQL-server waarop je het GGM hebt.
Dit zou kunnen op een eigen machine, op een eigen server (on-premises), of bijvoorbeeld in een cloud-omgeving (bijv., Azure).
Je zou bijvoorbeeld een scheduler (oftewel CRON-job) kunnen instellen welke het proces elke nacht draait.

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

1. Run source_to_staging (geconfigureerd via environment variables)

```
python -m source_to_staging.main
```

2. Run source_to_staging (geconfigureerd via .ini-bestand)

```
python -m source_to_staging.main --config source_to_staging/config.ini
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

2) Run source_to_staging met environment variables (in .env):

```bash
# gebruikt standaard PIPELINE=source-to-staging
docker run --rm \
	-v "$(pwd)/data:/app/data" \
	-v "$(pwd)/source_to_staging:/app/source_to_staging" \
	--env-file source_to_staging/.env  \
	ggmpilot:latest
```

3) Run source_to_staging met .ini-config:

```bash
docker run --rm \
	-v "$(pwd)/data:/app/data" \
	-v "$(pwd)/source_to_staging:/app/source_to_staging" \
	ggmpilot:latest source-to-staging \
		--config /app/source_to_staging/config.ini
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
- Oracle: de image gebruikt oracledb in thin‑mode. Voor thick‑mode (Instant Client) mount de client en zet de juiste pad‑variabele in je .env of .ini: SRC_ORACLE_CLIENT_PATH (bron, source_to_staging) of DST_ORACLE_CLIENT_PATH (doel, staging_to_silver).
- Proxy/certificaten: plaats certificaten in een volume en exporteer de juiste env vars (bijv. REQUESTS_CA_BUNDLE) als je die nodig hebt.

## Informatie voor ontwikkelaars

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

De map tests bevat diverse tests in het pytest-framework.

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
