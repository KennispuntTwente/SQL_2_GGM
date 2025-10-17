import os
from typing import cast
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, text

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine

from staging_to_silver.functions.query_loader import load_queries

# ─── Load .env & .ini from command line ────────────────────────────────────────
if os.path.exists("staging_to_silver/.env"):
    print("Loading environment variables…")
    load_dotenv(dotenv_path="staging_to_silver/.env")

args, cfg = load_single_ini_config()

# ─── Build connection to database ──────────────────────────────────────────────
ask_password_in_cli = bool(
    get_config_value("ASK_PASSWORD_IN_CLI", section="settings", cfg_parser=cfg, default=False)
)
driver = cast(str, get_config_value("DRIVER", cfg_parser=cfg))
username = cast(str, get_config_value("USER", cfg_parser=cfg))
host = cast(str, get_config_value("HOST", cfg_parser=cfg))
port = int(cast(str, get_config_value("PORT", cfg_parser=cfg)))
database = cast(str, get_config_value("DB", cfg_parser=cfg))
password = cast(
    str,
    get_config_value(
        "PASSWORD", cfg_parser=cfg, print_value=False, ask_in_command_line=ask_password_in_cli
    ),
)

engine = create_sqlalchemy_engine(
    driver=driver,
    username=username,
    password=password,
    host=host,
    port=port,
    database=database,
)

# ─── Read source/target schema from config ─────────────────────────────────────
source_schema = cast(
    str, get_config_value("SOURCE_SCHEMA", section="settings", cfg_parser=cfg, default="staging")
)
target_schema = cast(
    str, get_config_value("TARGET_SCHEMA", section="settings", cfg_parser=cfg, default="silver")
)

# ─── Read case-normalization settings ─────────────────────────────────────────
dest_table_case = get_config_value(
    "DESTINATION_TABLE_CASE", section="settings", cfg_parser=cfg, default=None
)
if not dest_table_case:
    # Legacy fallback
    dest_table_case = get_config_value(
        "TABLE_NAME_CASE", section="settings", cfg_parser=cfg, default=None
    )

column_name_case = get_config_value(
    "COLUMN_NAME_CASE", section="settings", cfg_parser=cfg, default=None
)

# ─── Fill engine with data for testing (optional) ─────────────────────────────
if get_config_value("TEST_MODE", cfg_parser=cfg, default=False):
    from ggm_dev_server.get_connection import get_connection
    from staging_to_silver.functions.test_silver_to_staging import fill_engine_with_data

    engine = get_connection(
        db_type="postgres",
        db_name=database,
        user=username,
        password=password,
        force_refresh=True,
        sql_folder="./ggm_selectie",
        sql_suffix_filter=True,
        sql_schema=target_schema,
    )
    fill_engine_with_data(engine, schema=source_schema, date_mode="timestamp")

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

# ─── Execute queries to go from staging (dump) to silver (GGM) ─────────────────────

# Queries laden zoals gedefinieerd in staging_to_silver/queries/*.py
queries = load_queries(
    package="staging_to_silver.queries",
    table_name_case=dest_table_case or "upper",  # default historical behavior
    column_name_case=column_name_case,
)

# All work happens **on the SQL server** and **inside one transaction**
# Executing everything on the SQL server, we avoid issues with data volumes & performance
# Executing everything in one transaction, we avoid issues with foreign key constraints

with engine.begin() as conn:  # single, atomic transaction
    # Optional but useful when FK dependencies exist (PostgreSQL only)
    conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))

    for name, query_fn in queries.items():
        # 1) build the SELECT statement that extracts from the source schema
        select_stmt = query_fn(engine, source_schema=source_schema)

        # Get the column names from the select statement
        select_col_order = [col.name for col in select_stmt.selected_columns]

        # 2) reflect (or cache‑lookup) the destination table definition
        dest_table = Table(
            name,
            metadata_dest,
            schema=target_schema,
            autoload_with=engine,
            extend_existing=True,
        )

        # Get the actual Column objects from the destination table
        # Use case-insensitive matching to be resilient to different DB identifier casing
        dest_cols_map_ci = {c.name.lower(): c for c in dest_table.columns}
        dest_cols = []
        for col_name in select_col_order:
            try:
                dest_cols.append(dest_table.columns[col_name])
            except KeyError:
                ci = dest_cols_map_ci.get(col_name.lower())
                if ci is None:
                    raise KeyError(
                        f"Destination column '{col_name}' not found in table {dest_table.fullname}. "
                        f"Available: {[c.name for c in dest_table.columns]}"
                    )
                dest_cols.append(ci)
        print(f"Reordered destination columns: {[col.name for col in dest_cols]}")

        # 3) determine how we load into the destination
        mode = write_modes_ci.get(name.lower(), "append").lower()
        full_name = f"{target_schema}.{name}"

        # 4a) pre‑action for destructive modes
        if mode == "overwrite":
            conn.execute(text(f"DELETE FROM {full_name}"))
        elif mode == "truncate":
            conn.execute(text(f"TRUNCATE TABLE {full_name}"))

        # 4b) build INSERT … from SELECT
        insert_from_select = dest_table.insert().from_select(dest_cols, select_stmt)

        if mode in {"append", "overwrite", "truncate"}:
            conn.execute(insert_from_select)
            print(f"Loaded → {full_name} [{mode}]")

        elif mode == "upsert":
            # NOTE: The following upsert logic uses PostgreSQL-specific SQLAlchemy features.
            # This will only work with PostgreSQL databases. For other databases, you must implement
            # a database-agnostic upsert or handle upserts differently.
            # On PostgreSQL – adjust index_elements to your PK/UK definition
            upsert_stmt = insert_from_select.on_conflict_do_update(  # type: ignore[attr-defined]
                index_elements=list(dest_table.primary_key.columns.keys()),
                set_={
                    c.name: insert_from_select.excluded[c.name]  # type: ignore[attr-defined]
                    for c in dest_table.columns
                    if not c.primary_key
                },
            )
            conn.execute(upsert_stmt)
            print(f"Upserted → {full_name}")

        else:
            raise ValueError(f"Unsupported write‑mode '{mode}' for {full_name}")

    print("✔︎ All queries executed successfully")
