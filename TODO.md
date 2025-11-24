* Packages/dependencies
Potentially unnecessary or suspect deps; investigate/remove
Update authors for pyproject.toml; description; license; README wiring
Enable build system in pyproject.toml
configparser: This is part of the Python standard library (since Python 3.0) and does not need to be installed.
pandas: Only used in load_csvs_to_db.py (test data generation), not in the main pipelines.
docker: Only used in tests and dev_sql_server.

* 5. Standardize "Engine Loader" Naming (Low Priority)
Issue:
engine_loaders.py contains load_destination_engine, which is generic, and load_source_connection, which is specific to sql_to_staging.
Recommendation:
Split these. Keep source-specific loaders in their respective module folders, but move generic destination loaders to database.