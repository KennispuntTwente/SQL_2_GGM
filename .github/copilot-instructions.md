# Copilot instructions for ggmpilot

Purpose: equip AI coding agents to be immediately productive in this repo by capturing the real architecture, workflows, and project‑specific conventions.

## Running Python
- Important: This projects uses a virtual environment managed by 'uv'. All Python commands should be run with the venv active.
Run `source .venv/Scripts/activate` (Windows bash) or `source .venv/bin/activate` (Linux/Mac) from the repo root to activate,
and only then run Python commands (e.g., `python -m ...`, `pip install ...`, `pytest`, etc.).

## Big picture
- Two-step pipeline to the Gemeentelijk Gegevensmodel (GGM):
  1) source_to_staging: copy source DB tables into a staging schema (streamed chunks or Parquet dump+load).
  2) staging_to_silver: execute SQLAlchemy SELECTs on the DB to populate the GGM “silver” schema inside a single transaction (PostgreSQL defers FK constraints).
- Scale & safety: all transfers are chunked/streamed; Parquet paths keep memory bounded; destination DB/schema auto-created for Postgres/MSSQL; staging columns are lowercased for consistency.

## Repo anchors
- Entrypoints: `source_to_staging/main.py`, `staging_to_silver/main.py`.
- I/O and copy: `source_to_staging/functions/{direct_transfer.py, download_parquet.py, upload_parquet.py}`.
- Silver query loader: `staging_to_silver/functions/query_loader.py`; queries live in `staging_to_silver/queries/*.py`.
- Config helpers: `utils/config/{cli_ini_config.py, get_config_value.py}`; engines: `utils/database/{create_sqlalchemy_engine.py, create_connectorx_uri.py}`.
- Logging: `utils/logging/setup_logging.py` (console always on; INI > ENV; handlers marked `_ggmpilot_managed`).
- Smoke/CI: Docker Compose in `docker/smoke`; example INIs in `docker/config`.

## Configuration (single INIs; INI > ENV > defaults)
- `source_to_staging`: one INI with sections `[database-source]`, `[database-destination]`, `[settings]`, `[logging]` (see `source_to_staging/config.ini.example`).
  - `[settings]`: `TRANSFER_MODE=SQLALCHEMY_DIRECT|CONNECTORX_DUMP|SQLALCHEMY_DUMP`, `SRC_TABLES`, `SRC_CHUNK_SIZE`, `CLEANUP_PARQUET_FILES`, `ASK_PASSWORD_IN_CLI`.
  - Oracle: set `SRC_ORACLE_CLIENT_PATH` (source_to_staging) or `DST_ORACLE_CLIENT_PATH` (staging_to_silver) for thick‑mode (Instant Client). TNS alias supported via `SRC_ORACLE_TNS_ALIAS=True` / `DST_ORACLE_TNS_ALIAS=True`.
- `staging_to_silver`: one INI with sections `[database-destination]`, `[settings]`, optional `[logging]` (see `staging_to_silver/config.ini.example`).
  - `[settings]`: `SILVER_SCHEMA` (default silver), optional `SILVER_DB` (MSSQL cross‑database only), `TABLE_NAME_CASE` (default upper), `COLUMN_NAME_CASE` (optional), `ASK_PASSWORD_IN_CLI`.
- Python: `pyproject.toml` targets Python ≥ 3.12.10; dependencies include SQLAlchemy 2.x, ConnectorX, polars/pyarrow, psycopg2, pyodbc, oracledb.

## Source → staging
- Modes
  - SQLALCHEMY_DIRECT: streams rows via server‑side cursors; bounded memory; auto‑creates DB/schema; creates/truncates per `write_mode` (default replace); destination column names lowercased.
  - SQLALCHEMY_DUMP | CONNECTORX_DUMP: `download_parquet(...)` writes chunked `Table_part0000.parquet`; `upload_parquet(...)` groups parts by base name, auto‑creates DB/schema, coerces decimals across parts, and lowercases columns before load.
- Cross‑dialect typing: `direct_transfer._coerce_generic_type` and `upload_parquet` apply dialect‑aware types (e.g., Oracle NUMBER(1)→Boolean, MSSQL DATETIME2(6), Oracle TIMESTAMP/NUMBER for float/decimal).

## Staging → silver
- Query contract: a module exports `__query_exports__ = {"DEST_TABLE": builder}` where `builder(engine, source_schema)` returns a SQLAlchemy `select` whose labels match the destination column names and order. Example: `staging_to_silver/queries/Client.py`.
- Loader: `load_queries(table_name_case, column_name_case, extra_modules, scan_package)` normalizes destination table keys and can relabel projected column labels; rejects duplicate DEST_TABLE keys.
- Runtime: one DB transaction; on PostgreSQL: `SET CONSTRAINTS ALL DEFERRED`. Destination tables are reflected and destination columns are matched case‑insensitively to the select’s label order.
- Write modes: configured per table in `staging_to_silver/main.py` via `write_modes` (case‑insensitive keys). Supported: `append` (default), `overwrite`, `truncate`, `upsert` (PostgreSQL‑only via `on_conflict_do_update`).

## Developer workflows
- Run pipelines (Windows bash examples):
  - `python -m source_to_staging.main --config source_to_staging/config.ini`
  - `python -m staging_to_silver.main --config staging_to_silver/config.ini`
- Tests: `pytest` (fast by default). Set `RUN_SLOW_TESTS=1` to include Docker‑backed integration tests for multiple DBs. See markers in `pytest.ini`.
- Smoke via Docker Compose: `bash docker/smoke/run_all.sh` runs staged services sequentially; INIs under `docker/config`.
- Tips: for Dockerized runs, use `host.docker.internal` to reach host DBs; Parquet dumps go to `./data` (mount if you want to persist); for MSSQL via ODBC, ensure msodbcsql driver; Oracle thin by default, thick via Instant Client + `SRC_ORACLE_CLIENT_PATH`/`DST_ORACLE_CLIENT_PATH`.

## Guardrails and patterns
- Preserve streaming/chunking semantics and column‑lowercasing in all upload paths.
- Keep `staging_to_silver` single‑transaction behavior and case‑insensitive dest‑column mapping; gate PostgreSQL‑only features (e.g., upsert).
- Use structured logging (`setup_logging`), not print; keep console logging enabled by default; INI overrides ENV.
- To add a silver mapping: create `staging_to_silver/queries/MyTable.py` with `__query_exports__` and return a `select` whose labels match the silver table’s columns.