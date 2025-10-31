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

* Direct transfer
Might add a small retry/backoff for transient DB issues during large transfers.

* staging_to_silver/README.md:1 is succinct; add:
Clarify dialect support per query module (or a matrix).
Explain write_modes and how to configure/override them.

