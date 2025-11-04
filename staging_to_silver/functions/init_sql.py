import logging
from typing import cast

from utils.config.get_config_value import get_config_value
from utils.database.execute_sql_folder import (
    execute_sql_folder,
    drop_schema_objects,
)
from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine


def run_init_sql(
    engine,
    cfg,
    *,
    dialect_name: str,
    database: str,
    silver_db: str,
    silver_schema: str | None,
) -> None:
    """
    Optionally initialize the silver schema by executing SQL files and/or dropping
    existing objects, encapsulating the logic currently in main.py.

    Responsibilities:
    - Read INIT_SQL_FOLDER and related settings from cfg
    - Handle DELETE_EXISTING_SCHEMA with legacy DROP_EXISTING_GGM fallback
    - If requested, drop existing objects in the silver schema (with MSSQL cross-DB guard)
    - For MSSQL with separate SILVER_DB, create a dedicated engine for running init SQL
    - Execute SQL scripts from INIT_SQL_FOLDER with optional suffix filtering
    """
    log = logging.getLogger("staging_to_silver")

    init_sql_folder = cast(
        str,
        get_config_value(
            "INIT_SQL_FOLDER", section="settings", cfg_parser=cfg, default=""
        ),
    )
    init_sql_suffix_filter = get_config_value(
        "INIT_SQL_SUFFIX_FILTER",
        section="settings",
        cfg_parser=cfg,
        default=True,
        cast_type=bool,
    )

    # Support new key DELETE_EXISTING_SCHEMA with a fallback to legacy DROP_EXISTING_GGM (deprecated)
    delete_existing = get_config_value(
        "DELETE_EXISTING_SCHEMA",
        section="settings",
        cfg_parser=cfg,
        default=False,
        cast_type=bool,
    )
    if not delete_existing:
        legacy_drop = get_config_value(
            "DROP_EXISTING_GGM",
            section="settings",
            cfg_parser=cfg,
            default=False,
            cast_type=bool,
        )
        if legacy_drop:
            delete_existing = True

    # Pre-drop on same-DB targets (avoid for SQLite/no schema). For MSSQL cross-DB, warn and skip here.
    if delete_existing and (silver_schema or ""):
        if (
            silver_db
            and (dialect_name == "mssql")
            and (silver_db.lower() != (database or "").lower())
        ):
            logging.getLogger(__name__).warning(
                "DELETE_EXISTING_SCHEMA is not supported when SILVER_DB (%s) != DST_DB (%s); skipping drop.",
                silver_db,
                database,
            )
        else:
            logging.getLogger(__name__).info(
                "Dropping existing objects in schema %r before initialization",
                silver_schema,
            )
            drop_schema_objects(engine, silver_schema or None)

    if not init_sql_folder:
        return

    logging.getLogger(__name__).info("Executing SQL scripts from %s", init_sql_folder)

    # If MSSQL and a separate SILVER_DB is specified, run INIT SQL against that DB
    engine_for_init = engine
    try:
        if (
            dialect_name == "mssql"
            and silver_db
            and silver_db.lower() != (database or "").lower()
        ):
            # Re-read connection details for creating an engine targeting SILVER_DB
            driver = cast(
                str,
                get_config_value(
                    "DST_DRIVER", section="database-destination", cfg_parser=cfg
                ),
            )
            username = cast(
                str,
                get_config_value(
                    "DST_USERNAME", section="database-destination", cfg_parser=cfg
                ),
            )
            password = cast(
                str,
                get_config_value(
                    "DST_PASSWORD",
                    section="database-destination",
                    cfg_parser=cfg,
                    print_value=False,
                    ask_in_command_line=bool(
                        get_config_value(
                            "ASK_PASSWORD_IN_CLI",
                            section="settings",
                            cfg_parser=cfg,
                            default=False,
                        )
                    ),
                ),
            )
            host = cast(
                str,
                get_config_value(
                    "DST_HOST", section="database-destination", cfg_parser=cfg
                ),
            )
            port = get_config_value(
                "DST_PORT",
                section="database-destination",
                cfg_parser=cfg,
                cast_type=int,
                allow_none_if_cast_fails=True,
            )
            _ = cast(
                str,
                get_config_value(
                    "DST_DB", section="database-destination", cfg_parser=cfg
                ),
            )

            engine_for_init = create_sqlalchemy_engine(
                driver=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                database=silver_db,
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
            log.info(
                "INIT_SQL_FOLDER will run against MSSQL target database %s (separate from DST_DB=%s)",
                silver_db,
                database,
            )
    except Exception:
        # Fallback to the main engine if creating a second engine fails
        engine_for_init = engine

    # If explicitly requested, drop existing objects in the INIT target schema
    # when initializing against a separate MSSQL SILVER_DB to avoid re-run DDL collisions.
    if (
        delete_existing
        and silver_schema
        and dialect_name == "mssql"
        and silver_db
        and silver_db.lower() != (database or "").lower()
    ):
        logging.getLogger(__name__).info(
            "Dropping existing objects in schema %r on target DB %s before initialization",
            silver_schema,
            silver_db,
        )
        drop_schema_objects(engine_for_init, silver_schema)

    execute_sql_folder(
        engine_for_init,
        init_sql_folder,
        suffix_filter=init_sql_suffix_filter,
        schema=(silver_schema or None),
    )
