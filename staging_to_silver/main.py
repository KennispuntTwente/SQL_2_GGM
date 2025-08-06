import os
from dotenv import load_dotenv

from sqlalchemy import MetaData, Table, text
from source_to_staging.functions.get_config_value import get_config_value
from source_to_staging.functions.create_sqlalchemy_engine import create_sqlalchemy_engine
from staging_to_silver.functions.queries import queries

# ─── Load .env ────────────────────────────────────────────────────────────────
if os.path.exists("staging_to_silver/.env"):
    print("Loading environment variables…")
    load_dotenv(dotenv_path="staging_to_silver/.env")

# TODO: load .ini config file if provided via CLI argument

# ─── Build connection to database ──────────────────────────────────────────────
engine = create_sqlalchemy_engine(
    driver   = get_config_value("DRIVER",   None),
    username = get_config_value("USERNAME", None),
    password = get_config_value("PASSWORD", None),
    host     = get_config_value("HOST",     None),
    port     = int(get_config_value("PORT", None)),
    database = get_config_value("DB",       None),
)

# ─── Read source/target schema from config ─────────────────────────────────────
source_schema = get_config_value("SOURCE_SCHEMA", None)  # e.g. "staging"
target_schema = get_config_value("TARGET_SCHEMA", None)  # e.g. "silver"

# ─── Reflect destination metadata lazily ──────────────────────────────────────
metadata_dest = MetaData()

# ─── Define write‑modes per destination (GGM) table ─────────────────────────────
write_modes = {
    "BESCHIKTE_VOORZIENING": "append",
    "ANOTHER_TABLE"       : "overwrite",
    "YET_ANOTHER"         : "upsert",
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

        # 2) reflect (or cache‑lookup) the destination table definition
        dest_table = Table(
            name,
            metadata_dest,
            schema=target_schema,
            autoload_with=engine,
            extend_existing=True,
        )
        dest_cols = [c.name for c in dest_table.columns]

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
                set_={c.name: insert_from_select.excluded[c.name]
                      for c in dest_table.columns if not c.primary_key}
            )
            conn.execute(upsert_stmt)
            print(f"Upserted → {full_name}")

        else:
            raise ValueError(f"Unsupported write‑mode '{mode}' for {full_name}")

    print("✔︎ All queries executed successfully")
