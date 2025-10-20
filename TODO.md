* Cross-dialect type fidelity with live DBs (Postgres/MSSQL/Oracle/MySQL):
Numeric precision/scale (DECIMAL), timestamp/timezone behavior (especially on Postgres), date/time.
Requires slow, Docker-based tests; you already have infrastructure under test_source_to_staging.py with RUN_SLOW_TESTS and Docker guards.

* Database and schema creation branches in upload_parquet:
CREATE DATABASE/SCHEMA logic for Postgres/MSSQL (currently only hit in slow tests).
Edge cases for special column names and quoting behavior on different RDBMSs