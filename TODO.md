* Resolve .env paths relative to module location
Use Path(__file__).parent (or similar) when loading .env files so they are found regardless of the current working directory, ensuring consistent configuration whether run from the repo root, an installed package, or a scheduler working dir.
Make .env loading robust to working directory. Both pipelines only load .env when the current working directory is the repo root. Running python -m sql_to_staging.main from elsewhere skips env loading, which can silently ignore critical configuration. Resolve by constructing the .env path relative to the module file (e.g., Path(__file__).resolve().parent / ".env").

* Clarify supported Python version. pyproject.toml requires Python 3.12.10+, but the codebase (and CI/dev workflows such as the provided Dockerfile) could run on 3.11 as well; this strict pin can block installs on common 3.11 environments. Decide whether 3.11 is supported and either relax the version constraint or update tooling/docs to enforce 3.12 consistently.

* Add a clear check for missing Parquet input directories. upload_parquet.group_parquet_files unconditionally calls os.listdir(input_dir) when no manifest is provided; if the directory is absent, the function raises a raw FileNotFoundError before any validation occurs. A pre-check that raises a user-friendly error (or auto-creates the directory) would improve robustness and diagnostics for misconfigured runs

* OData auth validation gap: odata_to_staging/functions/engine_loaders.py (lines 131-211) sets Basic/Bearer auth without checking for missing credentials, so a blank token produces Authorization: Bearer None, and Basic may send (None, None), leading to opaque 401s. Fail fast when required secrets are absent and surface a clear configuration error.

* Optional row counts are fatal in one path: sql_to_staging/functions/download_parquet.py (lines 205-220) raises RuntimeError if SELECT COUNT(*) fails when using SQLAlchemy, while the ConnectorX path only warns. On sources that disallow COUNT or where it’s expensive, an optional preflight aborts the export. Mirror the warning-only behavior or make the count opt-in.
