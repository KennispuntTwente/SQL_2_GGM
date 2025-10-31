import os
import logging
from typing import cast
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, text

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
from utils.database.initialize_oracle_client import initialize_oracle_client
from utils.database.execute_sql_folder import (
    execute_sql_folder,
    drop_schema_objects,
)

from staging_to_silver.functions.query_loader import load_queries
from staging_to_silver.functions.guards import (
    should_defer_constraints,
    validate_upsert_supported,
    parse_name_list,
    filter_queries,
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
# Initialize Oracle Instant Client if a destination path is configured in INI/ENV
dst_oracle_client_path = get_config_value(
    "DST_ORACLE_CLIENT_PATH",
    section="database-destination",
    cfg_parser=cfg,
    default=None,
)
if dst_oracle_client_path:
    try:
        initialize_oracle_client("DST_ORACLE_CLIENT_PATH", cfg_parser=cfg)
        logging.getLogger(__name__).info("Oracle client initialized (destination)")
    except Exception as e:
        logging.getLogger(__name__).warning(
            "Oracle client init failed for destination: %s", e
        )

ask_password_in_cli = bool(
    get_config_value(
        "ASK_PASSWORD_IN_CLI", section="settings", cfg_parser=cfg, default=False
    )
)
driver = cast(
    str, get_config_value("DST_DRIVER", section="database-destination", cfg_parser=cfg)
)
username = cast(
    str,
    get_config_value("DST_USERNAME", section="database-destination", cfg_parser=cfg),
)
host = cast(
    str, get_config_value("DST_HOST", section="database-destination", cfg_parser=cfg)
)
port = int(
    cast(
        str,
        get_config_value("DST_PORT", section="database-destination", cfg_parser=cfg),
    )
)
database = cast(
    str, get_config_value("DST_DB", section="database-destination", cfg_parser=cfg)
)
password = cast(
    str,
    get_config_value(
        "DST_PASSWORD",
        section="database-destination",
        cfg_parser=cfg,
        print_value=False,
        ask_in_command_line=ask_password_in_cli,
    ),
)

engine = create_sqlalchemy_engine(
    driver=driver,
    username=username,
    password=password,
    host=host,
    port=port,
    database=database,
    oracle_tns_alias=bool(
        get_config_value(
            "DST_ORACLE_TNS_ALIAS",
            section="database-destination",
            cfg_parser=cfg,
            default=False,
        )
    ),
    mssql_odbc_driver=(
        cast(
            str,
            get_config_value(
                "DST_MSSQL_ODBC_DRIVER",
                section="database-destination",
                cfg_parser=cfg,
                default="ODBC Driver 18 for SQL Server",
            ),
        )
        if ("mssql" in driver.lower() or "sqlserver" in driver.lower())
        else None
    ),
)

# ─── Read source/target schema from config ─────────────────────────────────────
source_schema = cast(
    str,
    get_config_value(
        "SOURCE_SCHEMA", section="settings", cfg_parser=cfg, default="staging"
    ),
)
target_schema = cast(
    str,
    get_config_value(
        "TARGET_SCHEMA", section="settings", cfg_parser=cfg, default="silver"
    ),
)

# ─── Optional: pre-init silver schema via SQL scripts / cleanup ───────────────
init_sql_folder = cast(
    str,
    get_config_value(
        "INIT_SQL_FOLDER", section="settings", cfg_parser=cfg, default=""
    ),
)
init_sql_suffix_filter = bool(
    get_config_value(
        "INIT_SQL_SUFFIX_FILTER",
        section="settings",
        cfg_parser=cfg,
        default=True,
    )
)
init_sql_schema = cast(
    str,
    get_config_value(
        "INIT_SQL_SCHEMA",
        section="settings",
        cfg_parser=cfg,
        default=(target_schema or ""),
    ),
)
# Support new key DELETE_EXISTING_SCHEMA with a fallback to legacy DROP_EXISTING_GGM (deprecated)
delete_existing = bool(
    get_config_value(
        "DELETE_EXISTING_SCHEMA",
        section="settings",
        cfg_parser=cfg,
        default=False,
    )
)
if not delete_existing:
    legacy_drop = bool(
        get_config_value(
            "DROP_EXISTING_GGM",
            section="settings",
            cfg_parser=cfg,
            default=False,
        )
    )
    if legacy_drop:
        logging.getLogger(__name__).warning(
            "Config key DROP_EXISTING_GGM is deprecated; use DELETE_EXISTING_SCHEMA instead."
        )
        delete_existing = True

if delete_existing and (target_schema or ""):  # avoid for SQLite/no schema
    logging.getLogger(__name__).info(
        "Dropping existing objects in schema %r before initialization", target_schema
    )
    drop_schema_objects(engine, target_schema or None)

if init_sql_folder:
    logging.getLogger(__name__).info(
        "Executing SQL scripts from %s", init_sql_folder
    )
    execute_sql_folder(
        engine,
        init_sql_folder,
        suffix_filter=init_sql_suffix_filter,
        schema=(init_sql_schema or None),
    )

# ─── Read case-normalization settings ─────────────────────────────────────────
table_name_case = get_config_value(
    "TABLE_NAME_CASE", section="settings", cfg_parser=cfg, default=None
)
column_name_case = get_config_value(
    "COLUMN_NAME_CASE", section="settings", cfg_parser=cfg, default=None
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

# ─── Execute queries to go from staging (dump) to silver (GGM) ─────────────────────

# Queries laden zoals gedefinieerd in staging_to_silver/queries/*.py
queries = load_queries(
    package="staging_to_silver.queries",
    table_name_case=table_name_case or "upper",  # default historical behavior
    column_name_case=column_name_case,
)

# Optional: filter queries by allow/deny list from configuration
allow_cfg = cast(
    str,
    get_config_value("QUERY_ALLOWLIST", section="settings", cfg_parser=cfg, default=""),
)
deny_cfg = cast(
    str,
    get_config_value("QUERY_DENYLIST", section="settings", cfg_parser=cfg, default=""),
)

# Normalize allow/deny to the same case as the keys in `queries`
allow = parse_name_list(allow_cfg)
deny = parse_name_list(deny_cfg)
if allow:
    # If table_name_case coerces to UPPER by default, recommend users list UPPER too;
    # we still match case-insensitively in filter_queries.
    pass

selected = filter_queries(queries, allowlist=allow or None, denylist=deny or None)
skipped = set(queries.keys()) - set(selected.keys())
if skipped:
    log.info("Skipping queries (filtered): %s", ", ".join(sorted(skipped)))
queries = selected

# Optional developer row limit: limit rows produced by each mapping (0/blank disables)
row_limit_cfg = get_config_value("ROW_LIMIT", section="settings", cfg_parser=cfg, default="")
try:
    dev_row_limit = int(str(row_limit_cfg)) if str(row_limit_cfg).strip() != "" else None
except Exception:
    dev_row_limit = None

# All work happens **on the SQL server** and **inside one transaction**
# Executing everything on the SQL server, we avoid issues with data volumes & performance
# Executing everything in one transaction, we avoid issues with foreign key constraints

with engine.begin() as conn:  # single, atomic transaction
    # Optional but useful when FK dependencies exist (PostgreSQL only)
    if should_defer_constraints(engine):
        conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))

    for name, query_fn in queries.items():
        # 1) build the SELECT statement that extracts from the source schema
        select_stmt = query_fn(engine, source_schema=source_schema)
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
            schema=(target_schema or None),
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
        log.debug("Reordered destination columns: %s", [col.name for col in dest_cols])

        # 3) determine how we load into the destination
        mode = write_modes_ci.get(name.lower(), "append").lower()
        full_name = f"{target_schema}.{name}" if target_schema else name

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
