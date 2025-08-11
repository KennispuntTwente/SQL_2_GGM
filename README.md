# ggmpilot

Deze repository bevat de code voor onze pilot met het GGM. Dit is nog een work-in-progress (WIP).

## Installatie

### Python & packages

Installeer eerst '[uv](https://docs.astral.sh/uv/)'. 'uv' is een tool voor het beheren van Python-omgevingen en packages.
Run dan `uv sync` in deze map om de benodigde Python-omgeving en packages te installeren naar de lockfile (zie: [uv.lock](uv.lock)).

``` bash
uv sync
```

Zorg daarna dat je in je IDE (bijv. VSCode) de Python-interpreter hebt ingesteld die hoort bij de '.venv' die door `uv sync` is aangemaakt.

Alle scripts in deze repisotry zijn ingesteld op de project root als werkmap. Dit betekent dat je de scripts moet runnen vanuit de project root, of dat je de werkmap in je IDE moet instellen op de project root. (Als je bijv. een script uitvoert in de map source_to_staging, en hierbij de werkmap source_to_staging wordt aangenomen in plaats van de project root, dan krijg je een foutmelding omdat de imports niet gevonden kunnen worden.)

### Docker

Om een development-database te maken, is installatie van Docker nodig. Installeer bijvoorbeeld [Docker Desktop](https://www.docker.com/products/docker-desktop/). Zorg dat de Docker daemon draait (bijvoorbeeld door Docker Desktop te starten).

## Gebruik

### GGM-development-database draaien

[ggm_dev_server/get_connection.py](ggm_dev_server/get_connection.py) bevat de functie get_connection() die een development-databaes binnen een Docker-container kan aanmaken en hiermee kan verbinden. Hierbij kan een map met SQL-scripts worden opgegeven, welke zullen worden uitgevoerd bij het aanmaken van de database. Hiermee kan de database geinitialiseerd worden met de tabellen van het GGM. [ggm_dev_server/sql](ggm_dev_server/sql) bevat de SQL-scripts die tabellen van het GGM aanmaken; is nu nog WIP om deze geschikt te maken voor onze pilot.

### Tijdelijke documentatie: source_to_staging runnen

Activeer de virtual env:
```
.venv\Scripts\activate
```

Run script met verwijzing naar .ini-bestanden (source, destination), bijv.:
```
python -m source_to_staging.main --source-config source_to_staging/source_config.ini.example --destination-config source_to_staging/destination_config.ini.example

```

Voor Rien; van SvhSD naar brons:
```
python -m source_to_staging.main --source-config h:/python/secrets/bron_svhsd.ini --destination-config h:/python/secrets/doel_dhw_brons.ini
```

Voor Rien; van brons naar zilver:
```
python -m staging_to_silver.main --config h:/python/secrets/Brons_Zilver.ini`
```