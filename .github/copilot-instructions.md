# Copilot instructions for ggmpilot

Purpose: enable AI agents to work productively in this repo by capturing the real project architecture, workflows, and conventions.

Big picture
- Two-step pipeline to GGM (Gemeentelijk Gegevensmodel):
  1) source_to_staging: move source DB tables into a staging schema, either directly DB→DB or via Parquet dump+load.
  2) staging_to_silver: run SQLAlchemy selects on the DB to populate the GGM silver schema inside a single transaction (Postgres FK constraints deferred).

Anchors in the repo
- Entrypoints: source_to_staging/main.py, staging_to_silver/main.py
- I/O and copy: source_to_staging/functions/{direct_transfer.py,download_parquet.py,upload_parquet.py}
- Silver query loader: staging_to_silver/functions/query_loader.py; queries live in staging_to_silver/queries/*.py
- Config helpers: utils/config/{cli_ini_config.py,get_config_value.py}; engines: utils/database/{create_sqlalchemy_engine.py,create_connectorx_uri.py}
- Logging: utils/logging/setup_logging.py (console always on; INI > ENV; handlers marked _ggmpilot_managed)

Configuration (single INIs; INI > ENV > defaults)
- Samples: source_to_staging/config.ini.example, staging_to_silver/config.ini.example
- source_to_staging [settings]: TRANSFER_MODE=SQLALCHEMY_DIRECT|CONNECTORX_DUMP|SQLALCHEMY_DUMP; SRC_TABLES; SRC_CHUNK_SIZE
- Oracle + CONNECTORX: set SRC_CONNECTORX_ORACLE_CLIENT_PATH to Instant Client dir when needed
- staging_to_silver [settings]: SOURCE_SCHEMA (default staging), TARGET_SCHEMA (default silver), TABLE_NAME_CASE (default upper), COLUMN_NAME_CASE (optional)

Source → staging modes
- SQLALCHEMY_DIRECT: functions/direct_transfer.py streams rows in chunks with server-side cursors; auto-creates DB/schema; creates/truncates tables per write_mode (default replace); lowercases destination columns.
- CONNECTORX_DUMP or SQLALCHEMY_DUMP: download_parquet(...) writes chunked parts like Table_part0000.parquet; upload_parquet(...) groups parts, auto-creates DB/schema, and lowercases columns.

Staging → silver execution
- Queries export: a module defines __query_exports__ = {"DEST_TABLE": builder}; builder(engine, source_schema) → sqlalchemy.select with labels matching destination columns.
- Loader: load_queries(table_name_case, column_name_case, extra_modules, scan_package) normalizes table keys and optionally relabels projected column labels; rejects duplicate DEST_TABLE keys.
- Runtime: one DB transaction; on Postgres: SET CONSTRAINTS ALL DEFERRED; destination tables reflected and columns matched case-insensitively to the select’s label order.
- Write modes (per table in main.py): append | overwrite | truncate | upsert (upsert is PostgreSQL-only via on_conflict_do_update).

Developer workflows
- Run pipelines (PowerShell examples):
  - python -m source_to_staging.main --config source_to_staging/config.ini
  - python -m staging_to_silver.main --config staging_to_silver/config.ini
- Tests: python -m pytest -q; set RUN_SLOW_TESTS=1 to include Docker-based integration tests (Docker Desktop required; MSSQL needs ODBC Driver 18; Oracle may need Instant Client)
- Smoke: bash docker/smoke/run_all.sh (use Git Bash/WSL on Windows).

Guardrails and patterns
- Preserve streaming/chunking semantics and column-lowercasing in upload paths; direct_transfer should keep bounded memory and cross-dialect-safe type coercion.
- Keep staging_to_silver single-transaction behavior and case-insensitive column mapping; gate PostgreSQL-only features.
- Use logging, not print; keep console logging enabled by default and INI-over-ENV precedence.
- To add a silver mapping: create staging_to_silver/queries/MyTable.py with __query_exports__ and return a select whose labels match the silver table columns.
