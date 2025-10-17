# source_to_staging

Deze module is verantwoordelijk voor het verbinden met de applicatie-SQL-server (bijv., Oracle database),
het dumpen van specifieke tabellen naar (tijdelijke) parquet-bestanden,
en vervolgens het uploaden van deze parquet-bestanden naar tabellen in de
target-SQL-server (bijv., Postgres/Microsoft SQL server).

Hiermee komt op de target-SQL-server een 'brons'-laag te staan met de data uit de applicatie,
nog in de vorm zoals deze op de applicatie-SQL-server staat.

In de module 'silver_to_staging' wordt deze data vervolgens omgevormd naar het gemeentelijk gegevensmodel,
ofwel 'zilver'.