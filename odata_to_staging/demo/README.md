# Demo: `odata_to_staging`

Korte demo om een klein stukje data vanaf een OData-endpoint (bijv. Northwind) in de lokale Postgres dev database te laden.

## Command

Voer in de projectroot uit (met geactiveerde virtualenv):

```bash
bash odata_to_staging/demo/demo.sh
```

Dit script:
- zorgt dat de Postgres dev database op poort `55432` draait,
- gebruikt `demo/config.ini` om de OData-bron en de Postgres-doelconfiguratie te lezen,
- laadt een selectie van OData-tabellen in het schema `odata_staging`.
