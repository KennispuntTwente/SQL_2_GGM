* Packages/dependencies
Potentially unnecessary or suspect deps; investigate/remove
Update authors for pyproject.toml; description; license; README wiring
Enable build system in pyproject.toml
configparser: This is part of the Python standard library (since Python 3.0) and does not need to be installed.
pandas: Only used in load_csvs_to_db.py (test data generation), not in the main pipelines.
docker: Only used in tests and dev_sql_server.

* 1. Refactor & Deduplicate Database Creation Logic (High Priority)
Issue:
There is significant code duplication between direct_transfer.py (function _ensure_database_and_schema) and upload_parquet.py (lines 140-200+). Both contain nearly identical logic for connecting to an admin database (like postgres or master) to create the target database if it doesn't exist.
Recommendation:
Extract this logic into a shared utility function, for example in utils/database/ensure_db.py.
Benefit: Reduces maintenance burden. If you need to change how databases are created (e.g., adding retry logic), you only do it in one place.

* 2. Fix Cross-Module Dependencies (High Priority)
Issue:
The odata_to_staging pipeline imports core functions directly from source_to_staging:
from source_to_staging.functions.engine_loaders import load_destination_engine
from source_to_staging.functions.upload_parquet import upload_parquet
This creates a "tight coupling" where changes to the source_to_staging module could unexpectedly break the odata_to_staging pipeline.
Recommendation:
Move shared functionality to a common location.
Move upload_parquet.py to utils/parquet/ or a shared functions/ package.
Move engine_loaders.py (or the generic load_destination_engine part) to database.

* 4. Make MSSQL Security Configurable (Medium Priority)
Issue:
In create_sqlalchemy_engine.py, the MSSQL connection string hardcodes TrustServerCertificate=yes.
While good for development, this bypasses SSL certificate validation and is a security risk for production environments.
Recommendation:
Make this configurable via your INI settings or environment variables (e.g., MSSQL_TRUST_CERT=True/False), defaulting to True for backward compatibility but allowing False for production.

* 5. Standardize "Engine Loader" Naming (Low Priority)
Issue:
engine_loaders.py contains load_destination_engine, which is generic, and load_source_connection, which is specific to source_to_staging.
Recommendation:
Split these. Keep source-specific loaders in their respective module folders, but move generic destination loaders to database.