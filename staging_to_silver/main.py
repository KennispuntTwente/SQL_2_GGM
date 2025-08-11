import os
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, text

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine

from staging_to_silver.functions.queries import queries

# ─── Load .env & .ini from command line ────────────────────────────────────────
if os.path.exists("staging_to_silver/.env"):
    print("Loading environment variables…")
    load_dotenv(dotenv_path="staging_to_silver/.env")

args, cfg = load_single_ini_config()

# ─── Build connection to database ──────────────────────────────────────────────
engine = create_sqlalchemy_engine(
    driver=get_config_value("DRIVER", cfg_parser=cfg),
    username=get_config_value("USER", cfg_parser=cfg),
    password=get_config_value("PASSWORD", cfg_parser=cfg, print_value=False),
    host=get_config_value("HOST", cfg_parser=cfg),
    port=int(get_config_value("PORT", cfg_parser=cfg)),
    database=get_config_value("DB", cfg_parser=cfg),
)

# ─── Read source/target schema from config ─────────────────────────────────────
source_schema = get_config_value(
    "SOURCE_SCHEMA", section="settings", cfg_parser=cfg, default="staging"
)
target_schema = get_config_value(
    "TARGET_SCHEMA", section="settings", cfg_parser=cfg, default="silver"
)

# ─── Fill engine with data for testing (optional) ─────────────────────────────
if get_config_value("TEST_MODE", cfg_parser=cfg, default=False):
    from ggm_dev_server.get_connection import get_connection
    from staging_to_silver.functions.test_silver_to_staging import fill_engine_with_data

    engine = get_connection(
        db_type="postgres",
        db_name=get_config_value("DB", cfg_parser=cfg),
        user=get_config_value("USER", cfg_parser=cfg),
        password=get_config_value("PASSWORD", cfg_parser=cfg, print_value=False),
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

# Append means that the table is loaded with new data, without deleting existing rows
# Overwrite means that the table is emptied before loading new data
# Upsert means that existing rows are updated, and new rows are inserted
# Truncate means that the table is emptied before loading new data, but does not fire triggers

# ─── Execute queries to go from staging (dump) to silver (GGM) ─────────────────────

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
        dest_cols = [dest_table.columns[col_name] for col_name in select_col_order]
        print(f"Reordered destination columns: {[col.name for col in dest_cols]}")

        # 3) determine how we load into the destination
        mode = write_modes.get(name, "append").lower()
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
            # On PostgreSQL – adjust index_elements to your PK/UK definition
            upsert_stmt = insert_from_select.on_conflict_do_update(
                index_elements=list(dest_table.primary_key.columns.keys()),
                set_={
                    c.name: insert_from_select.excluded[c.name]
                    for c in dest_table.columns
                    if not c.primary_key
                },
            )
            conn.execute(upsert_stmt)
            print(f"Upserted → {full_name}")

        else:
            raise ValueError(f"Unsupported write‑mode '{mode}' for {full_name}")

    print("✔︎ All queries executed successfully")
