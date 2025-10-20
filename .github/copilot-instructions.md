# Copilot instructions for ggmpilot

Goal: make agents productive quickly in this repo by explaining the architecture, workflows, and concrete conventions used here.

## Big picture
- Two-step data pipeline to the Gemeentelijk Gegevensmodel (GGM):
  1) source_to_staging: extract tables from a source DB and stream-export to Parquet, then load into a target DB staging schema.
  2) staging_to_silver: run SQLAlchemy select-queries that transform staging into the GGM silver schema, executing on the DB server inside a single transaction.
- Design principles:
  - Stream/chunk data to avoid high memory use (chunked Parquet parts like name_part0000.parquet).
  - Execute transforms on the destination RDBMS for performance and to respect FK constraints (constraints are deferred in Postgres).
  - Configuration via INI or environment variables; INI takes precedence.

## Key modules and files
- Entrypoints: `source_to_staging/main.py`, `staging_to_silver/main.py`.
- Parquet I/O: `source_to_staging/functions/download_parquet.py`, `source_to_staging/functions/upload_parquet.py`.
- Query loading and normalization: `staging_to_silver/functions/query_loader.py` and queries in `staging_to_silver/queries/*.py`.
- Config helpers: `utils/config/cli_ini_config.py`, `utils/config/get_config_value.py`.
- Engine/URI builders: `utils/database/create_sqlalchemy_engine.py`, `utils/database/create_connectorx_uri.py`.
- Logging: `utils/logging/setup_logging.py` (console + optional rotating file logging via INI/ENV).
- Smoke runs: `docker/smoke/**` and `docker/smoke/run_all.sh`.

## Configuration conventions
- Values can come from `.env` files in module folders or from INI files passed via CLI. Priority: INI > ENV > defaults (`get_config_value`).
- source_to_staging INI samples: `source_to_staging/source_config.ini.example`, `source_to_staging/destination_config.ini.example`.
- staging_to_silver INI sample: `staging_to_silver/config.ini.example`.
- Common keys: drivers (e.g., postgresql+psycopg2, mssql+pyodbc, oracle+oracledb), host/port/user/password/db, schemas.

### Logging configuration
- Configure logging in entrypoints with `setup_logging(app_name, cfg_parsers=[...])`.
- Defaults: console logging at INFO; optional rotating file logging can be enabled via INI `[logging]` or environment variables. Precedence: INI > ENV.
- Supported keys (under `[logging]` or as ENV):
  - `LOG_LEVEL` = DEBUG|INFO|WARNING|ERROR (default INFO)
  - `LOG_TO_FILE` = true|false (default false)
  - `LOG_FILE` = path (default `logs/<app_name>.log`)
  - `LOG_ROTATE_BYTES` = max bytes per file (default 5_000_000)
  - `LOG_BACKUP_COUNT` = number of rotated files (default 3)
  - `LOG_FORMAT` = optional format string
- Example `[logging]` in INI:
  - `LOG_LEVEL=INFO`
  - `LOG_TO_FILE=True`
  - `LOG_FILE=logs/staging_to_silver.log`
  - `LOG_ROTATE_BYTES=5000000`
  - `LOG_BACKUP_COUNT=3`

Conventions:
- Prefer `logging.getLogger(__name__)` with `.debug/.info/.warning/.error` instead of `print()` in library code.
- Console output should remain informative; don’t remove console handler. Use INFO for key milestones, DEBUG for noisy details.
- Example INIs in this repo already include a `[logging]` section you can copy.

Testing & internals:
- `tests/test_logging_setup.py` validates console/file logging and INI-over-ENV precedence.
- The logging setup marks its handlers with `_ggmpilot_managed` to avoid clobbering external handlers (e.g., pytest caplog) on reconfigure. Preserve this behavior if you modify logging.

## Source → staging specifics
- Two connection modes:
  - SQLAlchemy Engine for general DBs. Has known issue that it may not preserve data types perfectly when round-tripping (e.g., Oracle NUMBER → float).
  - ConnectorX URI for fast extraction; Oracle may require Instant Client with `SRC_CONNECTORX_ORACLE_CLIENT_PATH`. Is preferred to SQLAlchemy for speed & type fidelity.
- Extraction: `download_parquet(connection, tables, output_dir, chunk_size, schema)` streams data into numbered Parquet parts per table.
- Load: `upload_parquet(engine, schema, input_dir, cleanup)`
  - Auto-creates destination DB (Postgres/MSSQL) and schema if missing.
  - Lowercases column names on write for consistency.
  - Groups files by logical base name; respects chunk naming `_part\d+` (see tests for edge cases).

## Staging → silver specifics
- Queries are Python modules exporting a mapping: `__query_exports__ = {"DEST_TABLE": builder}` where `builder(engine, source_schema=...) -> sqlalchemy.select`.
- Loader: `load_queries(table_name_case, column_name_case, extra_modules, scan_package)` scans `staging_to_silver/queries` and optionally extra modules, normalizes table keys and projected column labels, and rejects duplicates.
- Execution (see `staging_to_silver/main.py`):
  - One DB transaction; Postgres constraints deferred.
  - Destination tables reflected; selected column order is matched case-insensitively to destination columns.
  - Write modes per table via `write_modes` map: append|overwrite|truncate|upsert (upsert is PostgreSQL-only via `on_conflict_do_update`).

## Developer workflows
- Environment: project targets Python 3.12+. Install with uv, then select the `.venv` interpreter in your IDE.
  - Install: `uv sync`
- Run pipelines:
  - `python -m source_to_staging.main` or with INIs: `python -m source_to_staging.main --source-config source_to_staging/source_config.ini --destination-config source_to_staging/destination_config.ini`
  - `python -m staging_to_silver.main` or with INI: `python -m staging_to_silver.main --config staging_to_silver/config.ini`
- Tests (Windows-friendly; see `AGENTS.md`):
  - Fast: `./.venv/Scripts/python -m pytest -q`
  - Enable slow, Docker-based integration tests: set `RUN_SLOW_TESTS=1` and ensure Docker Desktop is running; MSSQL tests require ODBC Driver 18; Oracle tests may require Instant Client path.
- Docker smoke runs:
  - One-shot both: `bash docker/smoke/run_all.sh` (or run compose services in `docker/smoke/docker-compose.yml`, though
  this may not exit cleanly and agents can get stuck on running this).

## Patterns and examples
- Add a new silver mapping:
  - Create `staging_to_silver/queries/MyTable.py` with:
    - `__query_exports__ = {"MYTABLE": def builder(engine, source_schema): ... return select(...labels matching silver columns...)}`.
    - Use `engine` for dialect-specific constructs if needed but prefer portable SQLAlchemy.
    - Loader will uppercase table key by default and optionally relabel columns per `COLUMN_NAME_CASE`.
    - See `tests/test_query_loader.py` for normalization behavior and duplicate detection.
- Add a new source table to extract:
  - Add to `SRC_TABLES` in source INI or env; Parquet files will be written under `data/` as `Table_part0000.parquet`, etc.; upload groups them automatically.

## External dependencies notes
- Driver naming determines engine creation (see `create_sqlalchemy_engine.py`).
- MSSQL requires a system ODBC driver (Driver 18 recommended). Oracle can run thin mode, but ConnectorX often needs Instant Client path.

## Guardrails for changes
- Preserve chunked streaming semantics in `download_parquet` and column-lowercasing in `upload_parquet`.
- Maintain single-transaction behavior and column order mapping in `staging_to_silver/main.py`.
- When extending write modes or adding DB-specific behavior, keep cross-DB compatibility; guard PostgreSQL-only features.
- Keep logging console output enabled by default and configurable via `[logging]`/ENV; avoid reintroducing raw `print()` in production paths. Maintain handler marking (`_ggmpilot_managed`) to keep pytest caplog working and prevent duplicate handlers.
