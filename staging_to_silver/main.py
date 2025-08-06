import os
from dotenv import load_dotenv

from sqlalchemy import MetaData, Table
from source_to_staging.functions.get_config_value import get_config_value
from source_to_staging.functions.create_sqlalchemy_engine import create_sqlalchemy_engine

from staging_to_silver.functions.queries import ALL as queries

# ─── load .env ────────────────────────────────────────────────────────────────
if os.path.exists("staging_to_silver/.env"):
    print("Loading environment variables…")
    load_dotenv(dotenv_path="staging_to_silver/.env")

# ─── build engine ────────────────────────────────────────────────────────────
engine = create_sqlalchemy_engine(
    driver   = get_config_value("DRIVER",   None),
    username = get_config_value("USERNAME", None),
    password = get_config_value("PASSWORD", None),
    host     = get_config_value("HOST",     None),
    port     = int(get_config_value("PORT", None)),
    database = get_config_value("DB",       None),
)

# ─── read source/target schema from config ──────────────────────────────────
source_schema = get_config_value("SOURCE_SCHEMA", None)  # e.g. "staging"
target_schema = get_config_value("TARGET_SCHEMA", None)  # e.g. "silver"

# ─── reflect destination metadata once ──────────────────────────────────────
metadata_dest = MetaData()
metadata_dest.reflect(bind=engine, schema=target_schema)

# ─── run & load loop ────────────────────────────────────────────────────────
with engine.begin() as conn:
    for name, query_fn in queries.items():
        # 1) build the SELECT from the source schema
        stmt   = query_fn(engine, source_schema=source_schema)
        result = conn.execute(stmt)
        rows   = [dict(r) for r in result.fetchall()]
        print(f"Fetched {len(rows)} rows from {source_schema}.{name}")

        # 2) reflect or lookup the destination table in target schema
        full_dest = f"{target_schema}.{name}"
        if full_dest not in metadata_dest.tables:
            # pull it in on the fly if it wasn’t in our initial reflect
            Table(
                name,
                metadata_dest,
                schema=target_schema,
                autoload_with=engine
            )
        dest_table = metadata_dest.tables[full_dest]

        # 3) append new rows
        conn.execute(dest_table.insert(), rows)
        print(f"Appended {len(rows)} rows into {target_schema}.{name}")
