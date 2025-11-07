"""
Execute a folder of SQL scripts against a target database connection.

Features:
- Optional filtering by filename suffix (e.g., *_postgres.sql, *_mssql.sql) based on engine dialect
- Optional schema handling (create/search_path/default schema where supported)
- Light SQL pre-processing for PostgreSQL (CREATE TABLE -> CREATE TABLE IF NOT EXISTS)
- Option to drop existing GGM objects in a schema before running scripts

Notes:
- We intentionally use the DB-API cursor (engine.raw_connection) to allow multi-statement SQL files.
- We keep behavior close to dev_sql_server._run_sql_scripts but reuse SQLAlchemy engines.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.schema import MetaData
import sqlparse


_CREATE_TBL_RE = re.compile(
    r"""\bCREATE\s+TABLE\b(?!\s+IF\s+NOT\s+EXISTS)""", re.IGNORECASE
)


def _dbtype_from_engine(engine: Engine) -> str:
    name = engine.dialect.name.lower()
    # Normalize common variants
    if name in {"postgresql", "postgres"}:
        return "postgres"
    if name in {"mssql", "sql server", "sqlserver"}:
        return "mssql"
    if name in {"mysql"}:
        return "mysql"
    if name in {"mariadb"}:
        return "mariadb"
    if name in {"oracle"}:
        return "oracle"
    if name in {"sqlite"}:
        return "sqlite"
    return name


def _preprocess_sql(sql_text: str, db_type: str) -> str:
    """Make CREATE TABLE idempotent for PostgreSQL; passthrough for others."""
    if db_type == "postgres":
        return _CREATE_TBL_RE.sub("CREATE TABLE IF NOT EXISTS", sql_text)
    return sql_text


def _split_sql_statements(sql_text: str, db_type: str) -> list[str]:
    """Split SQL text into executable statements.

    - Honors GO batch separators (MSSQL) on a line by itself
    - Honors Oracle '/' on a line by itself as a block terminator (not executed)
    - Uses sqlparse.split for semicolon-based splitting which respects quotes,
      PostgreSQL dollar-quoted blocks ($$...$$ / $tag$...$tag$), and compound statements
    - Keeps it simple (no custom DELIMITER support beyond what's handled by sqlparse)
    """
    # Normalize newlines
    lines = sql_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    # First, break on GO or / (oracle) boundaries
    # Store tuples of (chunk_text, is_oracle_block)
    chunks: list[tuple[str, bool]] = []
    buf: list[str] = []
    for raw in lines:
        line = raw.strip()
        if line.upper() == "GO" and db_type == "mssql":
            if buf:
                chunks.append(("\n".join(buf), False))
                buf = []
            continue
        if line == "/" and db_type == "oracle":
            if buf:
                # Mark this chunk as an Oracle PL/SQL block (treat atomically)
                chunks.append(("\n".join(buf), True))
                buf = []
            continue
        buf.append(raw)
    if buf:
        chunks.append(("\n".join(buf), False))

    # For each chunk, split using sqlparse which respects dollar-quoted blocks
    stmts: list[str] = []
    for s, is_oracle_block in chunks:
        if db_type == "oracle" and is_oracle_block:
            # Treat whole PL/SQL block as a single statement (internal semicolons allowed)
            stmt = s.strip()
            if stmt:
                # IMPORTANT: Do NOT strip the trailing semicolon from PL/SQL blocks.
                # Anonymous blocks require the final ';' after END; removing it leads to
                # ORA-06550 / PLS-00103 (EOF when expecting ';'). We only trim whitespace.
                stmts.append(stmt)
            continue

        # sqlparse.split retains statement boundaries and handles quoted/dollar-quoted strings
        parts = sqlparse.split(s)
        for part in parts:
            stmt = part.strip()
            if not stmt:
                continue
            # Remove trailing semicolons to avoid driver-specific issues
            stmt = stmt.rstrip(" \t\r\n;")
            if stmt:
                stmts.append(stmt)

    return [st for st in stmts if st]


def _files_to_run(folder: Path, db_type: str, suffix_filter: bool) -> list[Path]:
    all_sql = sorted(folder.glob("*.sql"))
    if not suffix_filter:
        return all_sql
    suffix = f"_{db_type}.sql"
    return [p for p in all_sql if p.name.lower().endswith(suffix)]


def execute_sql_folder(
    engine: Engine,
    sql_folder: str | Path,
    *,
    suffix_filter: bool = True,
    schema: Optional[str] = None,
) -> None:
    """Execute .sql files in a folder against the given engine.

    Parameters
    - engine: SQLAlchemy Engine
    - sql_folder: path containing .sql files
    - suffix_filter: if True, only run files ending with _<dbtype>.sql (e.g., _postgres.sql)
    - schema: optional target schema; created or set as default where supported
    """
    folder = Path(sql_folder)
    log = logging.getLogger(__name__)

    if not folder.exists():
        log.warning("SQL folder does not exist – nothing to do: %s", folder)
        return

    db_type = _dbtype_from_engine(engine)

    # Discover files
    run_files = _files_to_run(folder, db_type=db_type, suffix_filter=suffix_filter)
    log.info("Found %d SQL file(s) to execute in %s", len(run_files), folder.resolve())
    for f in run_files:
        log.info("   • %s", f.name)
    if not run_files:
        return

    # Use raw DB-API connection for multi-statement execution
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()

        # Prepare schema if requested
        if schema:
            if db_type == "postgres":
                cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
                raw.commit()
                cur.execute(f'SET search_path TO "{schema}", public')
            elif db_type == "mssql":
                # Create schema explicitly and commit before running any scripts
                try:
                    cur.execute(
                        f"IF SCHEMA_ID(N'{schema}') IS NULL EXEC('CREATE SCHEMA [{schema}]')"
                    )
                    raw.commit()
                except Exception as exc:
                    raw.rollback()
                    log.warning(
                        "Could not create schema %r on MSSQL (continuing): %s",
                        schema,
                        exc,
                    )
                # Setting default schema for the current user is best-effort and not required
                # for schema-qualified statements; skip noisy errors
                try:
                    cur.execute("SELECT CURRENT_USER")
                    row = cur.fetchone()
                    if row and row[0]:
                        username = row[0]
                        try:
                            cur.execute(
                                f"ALTER USER [{username}] WITH DEFAULT_SCHEMA=[{schema}]"
                            )
                            raw.commit()
                        except Exception:
                            raw.rollback()
                            # Keep quiet; schema-qualified DDL/DML will still work
                except Exception:
                    # If CURRENT_USER fails for some reason, continue silently
                    pass
            elif db_type in {"mysql", "mariadb"}:
                # Schema == database; warn if provided
                log.warning(
                    "MySQL/MariaDB: schema handling is database-scoped; ensure you are connected to the desired database."
                )
            elif db_type == "oracle":
                log.warning(
                    "Oracle: schemas map to users; connect as that user or qualify objects explicitly."
                )

        for file in run_files:
            sql = file.read_text(encoding="utf-8")
            sql = _preprocess_sql(sql, db_type)
            statements = _split_sql_statements(sql, db_type)
            try:
                for stmt in statements:
                    cur.execute(stmt)
                raw.commit()
                log.info("Executed: %s (%d statement(s))", file.name, len(statements))
            except Exception as exc:
                raw.rollback()
                log.error("Error executing %s: %s", file.name, exc)
                raise
    finally:
        try:
            raw.close()
        except Exception:
            pass


def drop_schema_objects(engine: Engine, schema: Optional[str]) -> None:
    """Drop existing tables (and related objects) for the given schema.

    Behavior by backend:
    - PostgreSQL: DROP SCHEMA <schema> CASCADE; CREATE SCHEMA <schema>
    - MSSQL / MySQL / MariaDB / SQLite: reflect tables in schema and drop_all in dependency order
    - Oracle: warn (schemas map to users); reflection drop is attempted without schema
    """
    log = logging.getLogger(__name__)
    db_type = _dbtype_from_engine(engine)

    if not schema and db_type != "sqlite":
        log.warning("No schema provided to drop; skipping.")
        return

    if db_type == "postgres":
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        log.info("Recreated schema %s on PostgreSQL", schema)
        return

    # Fallback: reflect and drop in dependency order
    md = MetaData()
    try:
        md.reflect(bind=engine, schema=schema)
    except Exception as exc:
        log.warning("Reflection failed for schema %r: %s", schema, exc)
        md.reflect(bind=engine)  # try without schema

    if not md.tables:
        log.info("No tables found to drop in schema %r", schema)
        return

    with engine.begin() as conn:
        md.drop_all(bind=conn)
    log.info("Dropped %d table(s) in schema %r", len(md.tables), schema)
