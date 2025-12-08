#!/usr/bin/env python3
"""
Load a folder of CSV files (lowercased headers) into a dev database using
our Docker-backed helpers in dev_sql_server.get_connection.

- Creates/starts the requested dev DB container (postgres/mssql/mysql/mariadb/oracle)
- Creates the target schema (if supported) and loads each CSV as a table with the
  file stem as table name (e.g., wvbesl.csv -> wvbesl)
- Uses pandas for convenience (already in project dependencies)

Usage examples:
  # Start MSSQL on default port, create DB 'ggm', and load tables under schema 'staging'
  python scripts/synthetic/load_csvs_to_db.py --db mssql --schema staging --db-name ggm --csv-dir data/synthetic

  # Start Postgres on custom port and load the same
  python scripts/synthetic/load_csvs_to_db.py --db postgres --port 55432 --schema staging --db-name ggm --csv-dir data/synthetic
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection
from utils.database.ensure_db import quote_ident


def _normalize_schema(schema: str | None, db_type: str) -> str | None:
    """Normalize CLI-provided schema value per database.

    - Postgres: empty string -> None (means "public" default schema)
    - Others: return None for empty string to let the DB default apply (e.g., dbo for MSSQL)
    """
    if schema is None:
        return None
    if schema == "":
        return None
    return schema


def ensure_schema(engine, schema: str | None, db_type: str) -> None:
    if not schema:
        return
    ddl = None
    if db_type == "postgres":
        qschema = quote_ident(engine, schema)
        ddl = f"CREATE SCHEMA IF NOT EXISTS {qschema}"
    elif db_type == "mssql":
        from utils.database.ensure_db import mssql_bracket_escape

        esc = mssql_bracket_escape(schema)
        ddl = (
            "IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = :schema) "
            "BEGIN EXEC('CREATE SCHEMA [" + esc + "]'); END"
        )
    elif db_type in ("mysql", "mariadb"):
        # MySQL treats schema as database; assume current DB and create no-op
        ddl = None
    elif db_type == "oracle":
        # Oracle uses users as schema; skip
        ddl = None
    if ddl:
        with engine.begin() as conn:
            if db_type == "mssql":
                conn.execute(text(ddl), {"schema": schema})
            else:
                conn.execute(text(ddl))


def load_csvs(engine, csv_dir: Path, schema: str | None) -> None:
    csvs = sorted(csv_dir.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}")

    for path in csvs:
        table = path.stem
        df = pd.read_csv(path)
        # lower-case columns defensively
        df.columns = [c.lower() for c in df.columns]
        df.to_sql(table, con=engine, schema=schema, if_exists="replace", index=False)
        print(f"Loaded {table} ({len(df)} rows)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Load synthetic CSVs into a dev database")
    ap.add_argument(
        "--db",
        dest="db_type",
        default="mssql",
        choices=["mssql", "postgres", "mysql", "mariadb", "oracle"],
        help="Database type",
    )
    ap.add_argument(
        "--db-name",
        dest="db_name",
        default="ggm",
        help="Database name (where applicable)",
    )
    ap.add_argument("--user", default="sa", help="DB user")
    ap.add_argument("--password", default="SecureP@ss1!24323482349", help="DB password")
    ap.add_argument(
        "--port", type=int, default=None, help="Host port to bind (optional)"
    )
    ap.add_argument("--schema", default="staging", help="Target schema for the tables")
    ap.add_argument(
        "--csv-dir",
        type=Path,
        default=Path("data/synthetic"),
        help="Folder containing CSV files",
    )
    ap.add_argument(
        "--force-refresh",
        action="store_true",
        help="Recreate container/DB (drops data)",
    )
    args = ap.parse_args()

    engine = get_connection(
        db_type=args.db_type,
        db_name=args.db_name,
        user=args.user,
        password=args.password,
        port=args.port,
        force_refresh=args.force_refresh,
        print_tables=False,
    )

    # Treat empty schema as DB default (e.g., public for Postgres)
    normalized_schema = _normalize_schema(args.schema, args.db_type)

    ensure_schema(engine, normalized_schema, args.db_type)
    load_csvs(engine, args.csv_dir, normalized_schema)

    # Print a quick list of tables
    with engine.connect() as conn:
        if args.db_type == "postgres":
            # If no explicit schema was provided, list from public
            list_schema = normalized_schema or "public"
            stmt = text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=:s ORDER BY table_name"
            ).bindparams(s=list_schema)
        elif args.db_type == "mssql":
            stmt = text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=:s ORDER BY table_name"
            ).bindparams(s=normalized_schema or "dbo")
        else:
            stmt = text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE() ORDER BY table_name"
            )
        rows = conn.execute(stmt).fetchall()
        print("Tables:", [r[0] for r in rows])

    print("✔ Synthetic CSVs loaded")


if __name__ == "__main__":
    main()
