* Packages/dependencies
Potentially unnecessary or suspect deps; investigate/remove
Update authors for pyproject.toml; description; license; README wiring
Enable build system in pyproject.toml

* Schema creation uses raw f-strings without escaping. The SQL folder executor interpolates user-provided schema names directly into CREATE SCHEMA, SET search_path, IF SCHEMA_ID and ALTER USER statements.
Any schema containing quotes, brackets, or malicious text will either break the script or permit SQL injection. Please route these identifiers through quote_ident() / mssql_bracket_escape() (as you do elsewhere) or parameterize the calls before executing them.

* SQL Server cross-database reflection is broken. qualify_schema() concatenates db and schema into a single string (e.g., "OtherDb.dbo"). That string is then passed directly to SQLAlchemy’s Table(..., schema=<value>) when reflecting or truncating silver tables.
SQLAlchemy expects schema to contain only the schema name; embedding the database name causes it to look for a literal schema called "OtherDb.dbo", so every reflection or has_table() check fails as soon as SILVER_DB differs from DST_DB. A more reliable approach is to keep the schema argument to just the schema (e.g., "dbo") and add the database name only when emitting raw SQL (as you already do inside quote_truncate_target).

* OData downloads silently truncate when $count is unavailable
The OData exporter relies on either ROW_LIMIT or a successful count() call to populate remaining. If both are absent (for example when the source does not support $count), remaining stays None. The pagination loop then breaks immediately after the first chunk because the stop condition next_url is None and (remaining is None …) becomes True even though more pages are available; next_url is None whenever the service expects the client to page via $skip/$top. In practice this means only the first page_size rows are ever written for such services.
Fix suggestion: Continue fetching when next_url is None but you’re using skip/top, and only break once the returned page is empty (or when you know you’ve reached the requested row limit).

* INIT_SQL_FOLDER may run against the wrong database without warning
In the MSSQL cross-database scenario, the code attempts to build a dedicated engine for SILVER_DB, but any exception in that block is swallowed and the function silently falls back to the staging engine before executing the SQL scripts.
If the second engine fails to initialize (mis-typed DB name, missing driver, etc.), the init scripts—including optional DELETE_EXISTING_SCHEMA—are executed against the staging database rather than the intended silver database, with no log message explaining the fallback.
Fix suggestion: log the exception (and ideally abort) instead of silently reusing the staging engine, so destructive scripts don’t touch the wrong database.
