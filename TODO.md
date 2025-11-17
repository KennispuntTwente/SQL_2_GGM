* Packages/dependencies
Potentially unnecessary or suspect deps; investigate/remove
Update authors for pyproject.toml; description; license; README wiring
Enable build system in pyproject.toml

* Declaratieregel mapping never projects the required primary key. staging_to_silver/queries/Declaratieregel.py (line 5) only emits BEDRAG/IS_VOOR_BESCHIKKING_ID/etc. while the shipped DDL defines DECLARATIEREGEL_ID as PRIMARY KEY NOT NULL (ggm_selectie/Sociaal_Domein_Beschikking_en_Voorziening__Domain_Objects_postgres.sql (line 92)). Inserts will fail as soon as the join produces any rows, which is currently masked by the synthetic generator purposely breaking the join (synthetic/generate_synthetic_data.py (line 158)) and by the Docker example adding a trigger to fabricate IDs (synthetic/examples/one_liner_postgres.sh (line 39)). Fix the query to derive a deterministic ID (e.g., reuse szukhis.uniekwvdos), drop the trigger workaround, and extend tests so DECLARATIEREGEL actually receives data.