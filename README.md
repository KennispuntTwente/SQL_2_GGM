# ggmpilot

Deze repository bevat code om gegevens uit de applicatie (...) te ontsluiten en te modelleren naar het 
[Gemeentelijk Gegevensmodel (GGM)](https://www.gemeentelijkgegevensmodel.nl/v2.4.0/). 

## Overzicht proces

## Van applicatie naar staging ('source_to_staging')

Door de 'client' (d.w.z., machine waarop Python-code in dit project draait),
wordt verbonden met de applicatie-SQL-server waarin de data van de applicatie staat (in dit geval een 
Oracle-database; zou ook een ander type database kunnen zijn).

De client downloadt de relevante tabellen en dumpt deze naar (tijdelijke) parquet-bestanden
(dit om te kunnen omgaan met eventuele 'larger-than-memory' data).

De client verbindt dan met de target-SQL-server. Dit is de SQL-server waarop het GGM zal staan.
De client uploadt alle gedownloadde tabellen naar een 'staging' (oftewel 'brons') database
binnen de target-SQL-server. Wanneer deze stap is afgerond staat dus de data uit de
applicatie-SQL-server, nog in de originele structuur, nu op de target-SQL-server.

## Van staging naar het GGM ('staging_to_silver')

(...)

## Installatie & gebruik

### Python

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
Via beide bestanden kan je dezelfde instellingen doen. Aangeraden is om één van de twee type bestandne te kiezen
voor het instellen van je configuratie. 

De `.env.example` en `(...).ini.example` bestanden tonen welke instellingen er zijn.
Als je gebruik wil maken van enviroment variables, kan je 1) op de reguliere manier
environment variables instellen op je systeem; of 2) een `.env` bestand aanmaken
naar de structuur van `.env.example` (in dezelfde map). Hetzelfde geldt voor de `(...).ini.example`
bestanden: zet een `(...).ini` bestand neer in dezelfde map met dezelfde structuur.

(Als je verdergaande configuratie wil doen, kan dat door de Python-scripts aan te passen.)

#### Uitvoeren

Vervolgens kan je de Python-scripts uitvoeren. Zie de voorbeelden hieronder:

1. Run source_to_staging (geconfigureerd via environment variables)

```
python -m source_to_staging.main
```

2. Run source_to_staging (geconfigureerd met .ini-bestanden)

```
python -m source_to_staging.main --source-config source_to_staging/source_config.ini --destination-config source_to_staging/destination_config.ini
```

3. Run staging_to_silver (geconfigurerd via environment variables)

```
python -m staging_to_silver.main
```

4. Run staging_to_silver (geconfigurerd via .ini-bestand)
```
python -m staging_to_silver.main --config config.ini
```

### Docker

Installeer [Docker Desktop](https://www.docker.com/products/docker-desktop/). Zorg dat de Docker daemon draait (bijvoorbeeld door Docker Desktop te starten).

(...)

