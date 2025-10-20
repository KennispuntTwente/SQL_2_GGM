* Cross-dialect type fidelity with live DBs (Postgres/MSSQL/Oracle/MySQL):
	- Validate DECIMAL precision/scale roundtrip (e.g., DECIMAL(38, 10), DECIMAL(18, 2))
	- Validate timestamp/timezone behavior (UTC vs local; Postgres TIMESTAMP/TIMESTAMPTZ)
	- Validate DATE and TIME semantics across dialects
	- Exercise both paths: ConnectorX (when supported) and SQLAlchemy Engine
	- Use slow, Docker-based tests (set `RUN_SLOW_TESTS=1`), leveraging `tests/test_source_to_staging.py`
	- Acceptance: Values and nulls preserved; no loss of precision beyond backend limits; consistent string formatting for date/time when needed
	- Add per-DB focused tests, reusing `ggm_dev_server.get_connection` and schema setup

* Database and schema creation branches in upload_parquet:
CREATE DATABASE/SCHEMA logic for Postgres/MSSQL (currently only hit in slow tests).
Edge cases for special column names and quoting behavior on different RDBMSs