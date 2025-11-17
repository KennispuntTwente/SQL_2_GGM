* Packages/dependencies
Potentially unnecessary or suspect deps; investigate/remove
Update authors for pyproject.toml; description; license; README wiring
Enable build system in pyproject.toml

* direct_transfer.py & upload_parquet.py: don't blindly lowercase column names by default?

* Oracle client initialization: initialize_oracle_client re-reads config via get_config_value, which again emits the warning noted above whenever the client path isn’t configured (very common outside Oracle). Consider short-circuiting when the initial probe already returned falsy to avoid duplicate noisy warnings.

* Declaratieregel mapping never projects the required primary key. staging_to_silver/queries/Declaratieregel.py (line 5) only emits BEDRAG/IS_VOOR_BESCHIKKING_ID/etc. while the shipped DDL defines DECLARATIEREGEL_ID as PRIMARY KEY NOT NULL (ggm_selectie/Sociaal_Domein_Beschikking_en_Voorziening__Domain_Objects_postgres.sql (line 92)). Inserts will fail as soon as the join produces any rows, which is currently masked by the synthetic generator purposely breaking the join (synthetic/generate_synthetic_data.py (line 158)) and by the Docker example adding a trigger to fabricate IDs (synthetic/examples/one_liner_postgres.sh (line 39)). Fix the query to derive a deterministic ID (e.g., reuse szukhis.uniekwvdos), drop the trigger workaround, and extend tests so DECLARATIEREGEL actually receives data.

* The documented end-to-end pipeline destroys the freshly loaded source database before it is used. Both the README helper script (synthetic/examples/one_liner_postgres.sh (line 29)) and the slow integration test (tests/test_example_pipeline_postgres.py (line 64)) call get_connection(..., force_refresh=True, db_name="ggm") immediately after loading data into source. force_refresh=True tears down the Docker container/volume, so the source database disappears and later source_to_staging fails to connect. The integration test never runs in CI (guarded by RUN_SLOW_TESTS), so the regression goes unnoticed. Keep the first container alive (skip force_refresh), or reload the source data after provisioning ggm, or use two separate containers.

* Custom mappings silently disappear on import failures. In staging_to_silver/functions/query_loader.py (line 198) every exception coming from a user-provided file (QUERY_PATHS) is swallowed and the file is skipped without any logging. A single syntax error therefore drops an entire table without warning. Log the exception (including the file path) and either re-raise or at least propagate a warning so users know why a mapping is missin