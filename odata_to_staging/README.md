# odata_to_staging

Deze module haalt data uit een OData-service en laadt deze in een 
'target-SQL-server' (bijv. Postgres of Microsoft SQL Server) waarop je het GGM wil hebben staan.

Hiermee ontstaat op de target-SQL-server een 'brons' (staging) laag met de data uit de OData-service, nog in de vorm zoals deze in de OData-service staat.

In de module 'staging_to_silver' wordt deze data vervolgens omgevormd naar het Gemeentelijk Gegevensmodel (GGM), oftewel 'zilver'.

In de sectie "Configuratie" staat uitgelegd hoe deze module te configureren.

(Voor uitleg van commands om deze module te runnen met configuratie, zie de `README.md` in de root van de repository; sectie "Uitvoeren".)

(Als je deze module wil uitproberen met synthetische data en zonder productie-database, zie de demo-scripts in `odata_to_staging/demo/`.)

## Configuratie

`odata_to_staging` gebruikt één INI-bestand (`--config`).
Een voorbeeld staat in `odata_to_staging/config.ini.example`.
Je kan ook via environment-variables configureren; zie voorbeeld
`odata_to_staging/.env.example`.
Prioriteit bij configuratie is INI > environment variables > standaard-waardes.

In de voorbeeld-configuratiebestanden 
(`odata_to_staging/config.ini.example` en `odata_to_staging/.env.example`)
staan toelichtingen bij de verschillende opties.
