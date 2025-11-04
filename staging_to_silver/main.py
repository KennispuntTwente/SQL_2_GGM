import os
import logging
from typing import cast
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, text

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value

from staging_to_silver.functions.engine_loaders import load_destination_engine
from staging_to_silver.functions.init_sql import run_init_sql

from staging_to_silver.functions.queries_setup import prepare_queries
from staging_to_silver.functions.schema_qualifier import qualify_schema
from staging_to_silver.functions.guards import (
    should_defer_constraints,
    validate_upsert_supported,
)
from utils.logging.setup_logging import setup_logging

# ─── Load .env & .ini from command line ────────────────────────────────────────
if os.path.exists("staging_to_silver/.env"):
    load_dotenv(dotenv_path="staging_to_silver/.env")

args, cfg = load_single_ini_config()

# Configure logging and keep console output
setup_logging(app_name="staging_to_silver", cfg_parsers=[cfg])
log = logging.getLogger("staging_to_silver")

# ─── Build connection to database ──────────────────────────────────────────────
engine = load_destination_engine(cfg)

# Note: staging location comes from [database-destination] → DST_DB/DST_SCHEMA.

# ─── Read staging/target schema from config ────────────────────────────────────

# Staging lives in the connected destination DB (unless overridden per‑backend)
staging_database = cast(
    str, get_config_value("DST_DB", section="database-destination", cfg_parser=cfg)
)
staging_schema = cast(
    str,
    get_config_value(
        "DST_SCHEMA", section="database-destination", cfg_parser=cfg, default="staging"
    ),
)

# Get target (silver) schema & database
silver_schema = cast(
    str,
    get_config_value(
        "SILVER_SCHEMA", section="settings", cfg_parser=cfg, default="silver"
    ),
)
silver_db = cast(
    str,
    get_config_value("SILVER_DB", section="settings", cfg_parser=cfg, default=""),
)

# Compute dialect-specific schema qualifier used for SQLAlchemy Table reflection
dialect_name = engine.dialect.name.lower()
staging_schema_for_sa = qualify_schema(
    dialect_name, staging_database, staging_schema, default_schema="dbo"
)
silver_schema_for_sa = qualify_schema(
    dialect_name, silver_db, silver_schema, default_schema="dbo"
)

# Warnings for unsupported cross-DB config on non-MSSQL
if silver_db and dialect_name != "mssql":
    log.warning(
        "SILVER_DB is set but backend %s does not support cross-database references; SILVER_DB will be ignored.",
        dialect_name,
    )

# ─── Optional: pre-init silver schema via SQL scripts / cleanup ───────────────
run_init_sql(
    engine,
    cfg,
    dialect_name=dialect_name,
    database=staging_database,
    silver_db=silver_db,
    silver_schema=silver_schema,
)

# ─── Staging name matching behavior for reflection/column lookup ──────────────
# Controls how staging table & column names are matched inside the query builders.
# STAGING_NAME_MATCHING: "auto" (default, case-insensitive) | "strict" (exact names only)
staging_name_matching = str(
    get_config_value(
        "STAGING_NAME_MATCHING", section="settings", cfg_parser=cfg, default="auto"
    )
).strip()
os.environ["STAGING_NAME_MATCHING"] = staging_name_matching

# STAGING_TABLE_NAME_CASE: optional preference when matching staging table names.
# Values: "upper" | "lower" | empty (no preference)
staging_table_name_case = str(
    get_config_value(
        "STAGING_TABLE_NAME_CASE", section="settings", cfg_parser=cfg, default=""
    )
).strip()
if staging_table_name_case:
    os.environ["STAGING_TABLE_NAME_CASE"] = staging_table_name_case

# SILVER_NAME_MATCHING: how to match destination (GGM) column names
# Values: "auto" (default, case-insensitive) | "strict" (exact names only)
silver_name_matching = (
    str(
        get_config_value(
            "SILVER_NAME_MATCHING", section="settings", cfg_parser=cfg, default="auto"
        )
    )
    .strip()
    .lower()
    or "auto"
)

# ─── Reflect destination metadata lazily ──────────────────────────────────────
metadata_dest = MetaData()

# ─── Define write‑modes per destination (GGM) table ─────────────────────────────
write_modes = {
    "BESCHIKTE_VOORZIENING": "append",
    "ANOTHER_TABLE": "overwrite",
    "YET_ANOTHER": "upsert",
    # … add / override as required
}
write_modes_ci = {k.lower(): v for k, v in write_modes.items()}

# Append means that the table is loaded with new data, without deleting existing rows
# Overwrite means that the table is emptied before loading new data
# Upsert means that existing rows are updated, and new rows are inserted
# Truncate means that the table is emptied before loading new data, but does not fire triggers

## ─── Execute queries to go from staging (dump) to silver (GGM) ───────────────

# Load and filter queries based on configuration
queries = prepare_queries(cfg)

# Optional developer row limit: limit rows produced by each mapping (0/blank disables)
dev_row_limit = get_config_value(
    "ROW_LIMIT",
    section="settings",
    cfg_parser=cfg,
    cast_type=int,
    allow_none_if_cast_fails=True,
)

# All work happens **on the SQL server** and **inside one transaction**
# Executing everything on the SQL server, we avoid issues with data volumes & performance
# Executing everything in one transaction, we avoid issues with foreign key constraints

with engine.begin() as conn:  # single, atomic transaction
    # Optional but useful when FK dependencies exist (PostgreSQL only)
    if should_defer_constraints(engine):
        conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))

    for name, query_fn in queries.items():
        # 1) build the SELECT statement that extracts from the staging schema
        select_stmt = query_fn(engine, source_schema=staging_schema_for_sa)
        if dev_row_limit and dev_row_limit > 0:
            try:
                select_stmt = select_stmt.limit(dev_row_limit)
            except Exception:
                # If a query is non-limitable (e.g. contains certain constructs), skip limiting
                log.warning("ROW_LIMIT could not be applied to mapping %s", name)

        # Get the column names from the select statement
        select_col_order = [col.name for col in select_stmt.selected_columns]

        # 2) reflect (or cache‑lookup) the destination table definition
        dest_table = Table(
            name,
            metadata_dest,
            schema=(silver_schema_for_sa or None),
            autoload_with=engine,
            extend_existing=True,
        )

        # Get the actual Column objects from the destination table
        # Matching behavior is controlled by SILVER_NAME_MATCHING
        dest_cols_map_ci = {c.name.lower(): c for c in dest_table.columns}
        dest_cols = []
        for col_name in select_col_order:
            # Try exact first
            try:
                dest_cols.append(dest_table.columns[col_name])
                continue
            except KeyError:
                pass

            # Fallback to case-insensitive only if auto-mode
            if silver_name_matching != "strict":
                ci = dest_cols_map_ci.get(col_name.lower())
                if ci is not None:
                    dest_cols.append(ci)
                    continue

            # Not found under current policy
            raise KeyError(
                f"Destination column '{col_name}' not found in table {dest_table.fullname}. "
                f"Available: {[c.name for c in dest_table.columns]}"
            )
        log.debug("Reordered destination columns: %s", [col.name for col in dest_cols])

        # 3) determine how we load into the destination
        mode = write_modes_ci.get(name.lower(), "append").lower()
        if silver_db and dialect_name == "mssql":
            full_name = f"{silver_db}.{silver_schema or 'dbo'}.{name}"
        else:
            full_name = f"{silver_schema}.{name}" if silver_schema else name

        # 4a) pre‑action for destructive modes
        if mode == "overwrite":
            conn.execute(text(f"DELETE FROM {full_name}"))
        elif mode == "truncate":
            if engine.dialect.name.lower() == "sqlite":
                conn.execute(text(f"DELETE FROM {full_name}"))
            else:
                conn.execute(text(f"TRUNCATE TABLE {full_name}"))

        # 4b) build INSERT … from SELECT
        insert_from_select = dest_table.insert().from_select(dest_cols, select_stmt)

        if mode in {"append", "overwrite", "truncate"}:
            conn.execute(insert_from_select)
            log.info("Loaded → %s [%s]", full_name, mode)

        elif mode == "upsert":
            # NOTE: The following upsert logic uses PostgreSQL-specific SQLAlchemy features.
            # This will only work with PostgreSQL databases. For other databases, you must implement
            # a database-agnostic upsert or handle upserts differently.
            # On PostgreSQL – adjust index_elements to your PK/UK definition
            validate_upsert_supported(engine)
            upsert_stmt = insert_from_select.on_conflict_do_update(  # type: ignore[attr-defined]
                index_elements=list(dest_table.primary_key.columns.keys()),
                set_={
                    c.name: insert_from_select.excluded[c.name]  # type: ignore[attr-defined]
                    for c in dest_table.columns
                    if not c.primary_key
                },
            )
            conn.execute(upsert_stmt)
            log.info("Upserted → %s", full_name)

        else:
            raise ValueError(f"Unsupported write‑mode '{mode}' for {full_name}")

    log.info("✔︎ All queries executed successfully")
