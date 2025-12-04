#!/usr/bin/env python3
"""
Load synthetic CSV files directly into an existing database using SQLAlchemy.

Unlike load_csvs_to_db.py, this script does NOT manage Docker containers -
it expects the database to already be running and accessible.

This is designed for use inside Docker containers where the database
is a separate service.

Usage:
  python -m synthetic.load_csvs_to_db_direct \
      --driver postgresql+psycopg2 \
      --host demo-db \
      --port 5432 \
      --user postgres \
      --password postgres \
      --db-name demo \
      --schema source \
      --csv-dir /app/data/synthetic
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def _normalize_schema(schema: str | None, driver: str) -> str | None:
    """Normalize CLI-provided schema value per database driver."""
    if schema is None or schema == "":
        return None
    return schema


def _get_db_type(driver: str) -> str:
    """Infer database type from SQLAlchemy driver string."""
    if driver.startswith("postgresql"):
        return "postgres"
    elif driver.startswith("mssql"):
        return "mssql"
    elif driver.startswith("mysql"):
        return "mysql"
    elif driver.startswith("mariadb"):
        return "mariadb"
    elif driver.startswith("oracle"):
        return "oracle"
    else:
        return "unknown"


def ensure_schema(engine, schema: str | None, db_type: str) -> None:
    """Create schema if it doesn't exist."""
    if not schema:
        return
    
    ddl = None
    if db_type == "postgres":
        ddl = f'CREATE SCHEMA IF NOT EXISTS "{schema}"'
    elif db_type == "mssql":
        ddl = f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}') EXEC('CREATE SCHEMA {schema}')"
    elif db_type in ("mysql", "mariadb"):
        # MySQL treats schema as database; skip
        ddl = None
    elif db_type == "oracle":
        # Oracle uses users as schema; skip
        ddl = None

    if ddl:
        with engine.begin() as conn:
            conn.execute(text(ddl))


def load_csvs(engine, csv_dir: Path, schema: str | None) -> None:
    """Load all CSV files from directory into database tables."""
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
    ap = argparse.ArgumentParser(
        description="Load synthetic CSVs directly into an existing database"
    )
    ap.add_argument(
        "--driver",
        default="postgresql+psycopg2",
        help="SQLAlchemy driver (e.g., postgresql+psycopg2, mssql+pyodbc)",
    )
    ap.add_argument("--host", required=True, help="Database host")
    ap.add_argument("--port", type=int, required=True, help="Database port")
    ap.add_argument("--user", required=True, help="Database user")
    ap.add_argument("--password", required=True, help="Database password")
    ap.add_argument("--db-name", dest="db_name", required=True, help="Database name")
    ap.add_argument("--schema", default=None, help="Target schema for the tables")
    ap.add_argument(
        "--csv-dir",
        type=Path,
        default=Path("data/synthetic"),
        help="Folder containing CSV files",
    )
    args = ap.parse_args()

    # Build SQLAlchemy URL
    db_type = _get_db_type(args.driver)
    
    # Handle MSSQL driver query parameters
    query = {}
    if db_type == "mssql":
        query["driver"] = "ODBC Driver 18 for SQL Server"
        query["TrustServerCertificate"] = "yes"

    url = URL.create(
        drivername=args.driver,
        username=args.user,
        password=args.password,
        host=args.host,
        port=args.port,
        database=args.db_name,
        query=query if query else None,
    )

    print(f"Connecting to {args.driver}://{args.user}:****@{args.host}:{args.port}/{args.db_name}")
    engine = create_engine(url)

    # Normalize schema
    normalized_schema = _normalize_schema(args.schema, args.driver)

    # Ensure schema exists
    ensure_schema(engine, normalized_schema, db_type)

    # Load CSVs
    load_csvs(engine, args.csv_dir, normalized_schema)

    # Print loaded tables
    with engine.connect() as conn:
        if db_type == "postgres":
            list_schema = normalized_schema or "public"
            stmt = text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=:s ORDER BY table_name"
            ).bindparams(s=list_schema)
        elif db_type == "mssql":
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
