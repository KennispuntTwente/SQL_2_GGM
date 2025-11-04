import logging
from typing import Any, Optional, cast

from utils.config.get_config_value import get_config_value
from utils.database.create_connectorx_uri import create_connectorx_uri
from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
from utils.database.initialize_oracle_client import initialize_oracle_client


def load_source_connection(cfg: Any, transfer_mode: str):
    """Create a source connection based on TRANSFER_MODE.

    Returns either a SQLAlchemy Engine (for SQLALCHEMY_* modes)
    or a ConnectorX URI (for CONNECTORX_DUMP).
    Also initializes Oracle Instant Client when configured.
    """
    src_driver = cast(
        str, get_config_value("SRC_DRIVER", section="database-source", cfg_parser=cfg)
    )
    src_username = cast(
        Optional[str],
        get_config_value("SRC_USERNAME", section="database-source", cfg_parser=cfg),
    )
    src_password = cast(
        Optional[str],
        get_config_value(
            "SRC_PASSWORD",
            section="database-source",
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
    src_host = cast(
        Optional[str],
        get_config_value("SRC_HOST", section="database-source", cfg_parser=cfg),
    )
    src_port = int(
        str(get_config_value("SRC_PORT", section="database-source", cfg_parser=cfg))
    )
    src_db = cast(
        Optional[str],
        get_config_value("SRC_DB", section="database-source", cfg_parser=cfg),
    )

    # Initialize Oracle client for SOURCE if configured
    try:
        if get_config_value(
            "SRC_ORACLE_CLIENT_PATH",
            section="database-source",
            cfg_parser=cfg,
            default=None,
        ):
            initialize_oracle_client("SRC_ORACLE_CLIENT_PATH", cfg_parser=cfg)
    except Exception as e:
        logging.getLogger(__name__).warning(
            "Oracle client init failed for source: %s", e
        )

    if transfer_mode == "SQLALCHEMY_DIRECT":
        # Force SQLAlchemy engine for direct copy mode
        return create_sqlalchemy_engine(
            driver=src_driver,
            username=cast(str, src_username),
            password=cast(str, src_password),
            host=cast(str, src_host),
            port=src_port,
            database=cast(str, src_db),
            oracle_tns_alias=bool(
                get_config_value(
                    "SRC_ORACLE_TNS_ALIAS",
                    section="database-source",
                    cfg_parser=cfg,
                    default=False,
                )
            ),
            mssql_odbc_driver=(
                cast(
                    str,
                    get_config_value(
                        "SRC_MSSQL_ODBC_DRIVER",
                        section="database-source",
                        cfg_parser=cfg,
                        default="ODBC Driver 18 for SQL Server",
                    ),
                )
                if "mssql" in src_driver.lower() or "sqlserver" in src_driver.lower()
                else None
            ),
        )
    elif transfer_mode == "CONNECTORX_DUMP":
        # Use ConnectorX URI
        uri = create_connectorx_uri(
            driver=src_driver,
            username=src_username,
            password=src_password,
            host=src_host,
            port=src_port,
            database=src_db,
            alias=bool(
                get_config_value(
                    "SRC_ORACLE_TNS_ALIAS",
                    section="database-source",
                    cfg_parser=cfg,
                    default=False,
                )
            ),
        )

        # If Oracle client path is set, initialize it for ConnectorX (source-specific key)
        oracle_client_path = get_config_value(
            "SRC_ORACLE_CLIENT_PATH", section="database-source", cfg_parser=cfg
        )
        if oracle_client_path:
            try:
                initialize_oracle_client(cfg_parser=cfg)
            except Exception as e:
                logging.getLogger(__name__).warning("Oracle client init failed: %s", e)
        # If driver contains "oracle" and no client configured, warn for possible issues
        elif "oracle" in src_driver.lower():
            logging.getLogger(__name__).warning(
                "Using CONNECTORX & Oracle, but no Oracle client path (SRC_ORACLE_CLIENT_PATH) is set; "
                "ConnectorX may not work correctly with Oracle. Download Instant Client and set the path "
                "(e.g., C:\\oracle\\instantclient_21_18)."
            )
        return uri
    else:  # SQLALCHEMY_DUMP
        return create_sqlalchemy_engine(
            driver=src_driver,
            username=cast(str, src_username),
            password=cast(str, src_password),
            host=cast(str, src_host),
            port=src_port,
            database=cast(str, src_db),
            oracle_tns_alias=bool(
                get_config_value(
                    "SRC_ORACLE_TNS_ALIAS",
                    section="database-source",
                    cfg_parser=cfg,
                    default=False,
                )
            ),
            mssql_odbc_driver=(
                cast(
                    str,
                    get_config_value(
                        "SRC_MSSQL_ODBC_DRIVER",
                        section="database-source",
                        cfg_parser=cfg,
                        default="ODBC Driver 18 for SQL Server",
                    ),
                )
                if "mssql" in src_driver.lower() or "sqlserver" in src_driver.lower()
                else None
            ),
        )


def load_destination_engine(cfg: Any):
    """Create the destination SQLAlchemy engine using [database-destination] settings.

    Also initializes Oracle Instant Client when configured.
    """
    # Initialize Oracle client for DESTINATION if configured
    try:
        if get_config_value(
            "DST_ORACLE_CLIENT_PATH",
            section="database-destination",
            cfg_parser=cfg,
            default=None,
        ):
            initialize_oracle_client("DST_ORACLE_CLIENT_PATH", cfg_parser=cfg)
    except Exception as e:
        logging.getLogger(__name__).warning(
            "Oracle client init failed for destination: %s", e
        )

    dst_driver = cast(
        str,
        get_config_value("DST_DRIVER", section="database-destination", cfg_parser=cfg),
    )
    return create_sqlalchemy_engine(
        driver=dst_driver,
        username=cast(
            str,
            get_config_value(
                "DST_USERNAME", section="database-destination", cfg_parser=cfg
            ),
        ),
        password=cast(
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
        ),
        host=cast(
            str,
            get_config_value(
                "DST_HOST", section="database-destination", cfg_parser=cfg
            ),
        ),
        port=int(
            str(
                get_config_value(
                    "DST_PORT", section="database-destination", cfg_parser=cfg
                )
            )
        ),
        database=cast(
            str,
            get_config_value("DST_DB", section="database-destination", cfg_parser=cfg),
        ),
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
            if ("mssql" in dst_driver.lower() or "sqlserver" in dst_driver.lower())
            else None
        ),
    )
