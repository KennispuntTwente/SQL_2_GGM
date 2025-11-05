* Packages/dependencies
Potentially unnecessary or suspect deps:
pandas is declared but not used; consider removing to reduce image size and dependency footprint.
Verify if sqlparse is used; remove if not needed.
Add [build-system] (e.g., requires=["setuptools>=...","wheel"], build-backend="setuptools.build_meta").
Move pytest and any dev-only tooling into a dev/extra group (uv supports this).
Remove unused deps or clearly justify them.
Metadata gaps: description, readme, authors, license (although LICENSE.md exists), and classifiers.
Fill metadata for better distribution/consumption.

* Analyze current set of queries and based on that generate a synthetic dataset
which can be used for development/testing purposes

* MSSQL CREATE DATABASE needs autocommit (will error inside a transaction)
Both upload_parquet and direct_transfer try to create databases on PostgreSQL and MSSQL. Postgres block correctly uses AUTOCOMMIT; MSSQL block does not.
Impact: Error “CREATE DATABASE not allowed within a transaction” with pyodbc.
Evidence:
source_to_staging/functions/upload_parquet.py: for MSSQL block, uses admin_eng.connect() then conn.execute(...) without isolation_level="AUTOCOMMIT".
source_to_staging/functions/direct_transfer.py: in _ensure_database_and_schema for MSSQL, same pattern.
Fix: For MSSQL admin connection, use with admin_eng.connect().execution_options(isolation_level="AUTOCOMMIT") as conn: before executing CREATE DATABASE.

* Avoid heavy COUNT(*) before export unless desired
download_parquet does COUNT(*) upfront for SQLAlchemy path purely for logging.
Evidence: source_to_staging/functions/download_parquet.py tail block where COUNT(*) is issued, then iter_batches is used.
Impact: Slows down huge tables; unnecessary pressure on source systems.
Fix: Make row count optional (e.g., LOG_ROW_COUNT=true|false from settings); default to true

* Unify table name casing for YAML/INI “SRC_TABLES” > file names > staging table names
Current behavior preserves the case from config to filenames to destination table names, while columns are lowercased. On Postgres/unquoted identifiers, unintended case changes can occur.
Evidence: upload_parquet keeps table_name from filenames; columns are lowered, tables are not.
source_to_staging/functions/upload_parquet.py: per-group write stays with base name
Fix: Add a setting (e.g., LOWERCASE_TABLE_NAMES=true|false) and apply it consistently when deriving base table and writing.

* Robust fallback when polars signatures differ
The current TypeError fallback in upload_parquet only drops "schema" and "dtype" keys from write_kwargs, but dtype is nested under engine_options in current code and never removed; and if_table_exists remains.
Evidence: source_to_staging/functions/upload_parquet.py:440–448.
Fix: In fallback, try these attempts in order:
New signature (dtype=..., if_exists=..., schema=...).
New signature without dtype (dtype omitted).
New signature without schema.
Legacy signature (if_table_exists=..., possibly without dtype).
If still failing, re-raise with a helpful hint about polars version.

* Medium – utils/database/execute_sql_folder.py:57 _split_sql_statements ignores PostgreSQL dollar-quoted blocks ($$...$$). Any INIT SQL that defines functions/procedures will be torn apart at the first semicolon, causing syntax errors. Either hand the work to sqlparse.split (already in deps) or extend the tokenizer to honor dollar-quoting.

* Medium – source_to_staging/functions/direct_transfer.py:33 & source_to_staging/functions/upload_parquet.py:182 Autocreation assumes you can hop to an admin DB called "postgres" (and "master" for MSSQL). Managed services (Azure, RDS, AlloyDB) often revoke access to those databases, so the staging run dies before copying anything. Make the admin database configurable (falling back to the current catalog) or skip the step when the hop fails.