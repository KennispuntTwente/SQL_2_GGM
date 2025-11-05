* Packages/dependencies
Potentially unnecessary or suspect deps:
mssql>=1.0.1 seems questionable (commonly pyodbc or pymssql are used; you already have pyodbc).
pandas is declared but not used; consider removing to reduce image size and dependency footprint.
Verify if sqlparse is used; remove if not needed.
Add [build-system] (e.g., requires=["setuptools>=...","wheel"], build-backend="setuptools.build_meta").
Move pytest and any dev-only tooling into a dev/extra group (uv supports this).
Remove unused deps or clearly justify them.
Metadata gaps: description, readme, authors, license (although LICENSE.md exists), and classifiers.
Fill metadata for better distribution/consumption.

* Upsert mode guard on missing PK
Where: main.py (upsert clause)
Issue: Upsert mode derives index_elements from dest_table.primary_key.columns.keys(). If there’s no PK, this becomes an empty list and will error non-obviously.
Recommendation: Detect and raise a concise error: “Upsert requires a primary key on {table}”.

* Analyze current set of queries and based on that generate a synthetic dataset
which can be used for development/testing purposes