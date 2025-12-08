import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.schema import CreateSchema

from utils.database.identifiers import quote_ident, mssql_bracket_escape

logger = logging.getLogger("utils.database.ensure_db")


def ensure_database_and_schema(
    engine: Engine,
    schema: str | None,
    *,
    admin_database: str | None = None,
) -> None:
    """Ensure destination database (where applicable) and schema exist.

    This centralizes the logic previously duplicated in:
    - sql_to_staging.functions.direct_transfer._ensure_database_and_schema
    - sql_to_staging.functions.upload_parquet (inline section)
    """
    dialect = engine.dialect.name.lower()

    # 1) Ensure database exists (Postgres/MSSQL)
    db_name = engine.url.database
    if db_name:
        if dialect == "postgresql":
            # Allow overriding the admin DB name; default to vendor default.
            admin_db = admin_database or "postgres"
            try:
                admin_url = engine.url.set(database=admin_db)
                admin_eng = create_engine(admin_url)
                try:
                    with admin_eng.connect() as conn:
                        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
                        exists = conn.execute(
                            text("SELECT 1 FROM pg_database WHERE datname = :db"),
                            {"db": db_name},
                        ).scalar()
                        if not exists:
                            qdb = quote_ident(engine, db_name)
                            conn.execute(text(f"CREATE DATABASE {qdb}"))
                finally:
                    admin_eng.dispose()
            except Exception as e:  # pragma: no cover - environment specific
                # On managed services, access to the admin DB can be blocked; skip gracefully.
                logger.warning(
                    "Skipping database auto-creation; failed to connect to admin database %r: %s",
                    admin_db,
                    e,
                )
        elif dialect in ("mssql", "sql server"):
            admin_db = admin_database or "master"
            try:
                admin_url = engine.url.set(database=admin_db)
                admin_eng = create_engine(admin_url)
                try:
                    with admin_eng.connect() as conn:
                        # Ensure CREATE DATABASE runs outside an explicit transaction
                        # to avoid pyodbc error: "CREATE DATABASE not allowed within a transaction".
                        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
                        # Prefer parameter for DB_ID input and safely quoted identifier for CREATE DATABASE
                        qdb = quote_ident(engine, db_name)
                        conn.execute(
                            text(
                                f"""
                        IF DB_ID(:db) IS NULL
                        BEGIN
                            CREATE DATABASE {qdb};
                        END
                        """
                            ),
                            {"db": db_name},
                        )
                finally:
                    admin_eng.dispose()
            except Exception as e:  # pragma: no cover - environment specific
                logger.warning(
                    "Skipping database auto-creation; failed to connect to admin database %r: %s",
                    admin_db,
                    e,
                )

    # 2) Ensure schema exists
    if schema:
        from sqlalchemy import text as _text  # avoid shadowing

        with engine.begin() as conn:
            if dialect == "postgresql":
                qschema = quote_ident(engine, schema)
                conn.execute(_text(f"CREATE SCHEMA IF NOT EXISTS {qschema}"))
            elif dialect in ("mssql", "sql server"):
                esc = mssql_bracket_escape(schema)
                safe_schema = schema.replace("'", "''")
                conn.execute(
                    _text(
                        f"""
                    IF SCHEMA_ID(N'{safe_schema}') IS NULL
                    BEGIN
                        EXEC(N'CREATE SCHEMA [{esc}]');
                    END
                    """
                    )
                )
            elif dialect == "oracle":
                # Oracle uses users as schemas; assume exists / has perms
                logger.info(
                    "Skipping schema creation on Oracle (schema=%s). Schemas map to users; ensure the target user/schema exists and has privileges.",
                    schema,
                )
            elif dialect in ("mysql", "mariadb"):
                # MySQL doesn't support schemas outside of databases
                logger.info(
                    "Skipping schema creation on %s (schema=%s). MySQL/MariaDB do not have separate schemas; use the database name instead.",
                    dialect,
                    schema,
                )
            elif dialect == "sqlite":
                # SQLite has no schema namespace; skip
                logger.info(
                    "Skipping schema creation on SQLite (schema=%s). SQLite has no schema namespaces; using the main database.",
                    schema,
                )
            else:
                try:
                    conn.execute(CreateSchema(schema))
                except ProgrammingError as e:
                    if "already exists" not in str(e).lower():
                        raise
