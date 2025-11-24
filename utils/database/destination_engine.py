"""Shared destination engine loader.

This centralizes the logic for building the destination SQLAlchemy engine
from configuration. All pipelines should import from here instead of
cross-importing each other.
"""

from __future__ import annotations

import logging
from typing import Any, cast

from utils.config.get_config_value import get_config_value
from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
from utils.database.initialize_oracle_client import initialize_oracle_client


def load_destination_engine(cfg: Any):
    """Create the destination SQLAlchemy engine using [database-destination].

    - Initializes Oracle Instant Client when configured via DST_ORACLE_CLIENT_PATH
    - Supports MSSQL ODBC driver override via DST_MSSQL_ODBC_DRIVER
    - Honors ASK_PASSWORD_IN_CLI for interactive prompts
    """

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
        except Exception as e:  # pragma: no cover - defensive logging only
            logging.getLogger(__name__).warning(
                "Oracle client init failed for destination: %s", e
            )

    driver = cast(
        str,
        get_config_value("DST_DRIVER", section="database-destination", cfg_parser=cfg),
    )

    return create_sqlalchemy_engine(
        driver=driver,
        username=cast(
            str,
            get_config_value(
                "DST_USERNAME",
                section="database-destination",
                cfg_parser=cfg,
                cast_type=str,
            ),
        ),
        password=cast(
            str,
            get_config_value(
                "DST_PASSWORD",
                section="database-destination",
                cfg_parser=cfg,
                print_value=False,
                ask_in_command_line=get_config_value(
                    "ASK_PASSWORD_IN_CLI",
                    section="settings",
                    cfg_parser=cfg,
                    default=False,
                    cast_type=bool,
                ),
                cast_type=str,
            ),
        ),
        host=cast(
            str,
            get_config_value(
                "DST_HOST", section="database-destination", cfg_parser=cfg
            ),
        ),
        port=get_config_value(
            "DST_PORT",
            section="database-destination",
            cfg_parser=cfg,
            cast_type=int,
            allow_none_if_cast_fails=True,
        ),
        database=cast(
            str,
            get_config_value("DST_DB", section="database-destination", cfg_parser=cfg),
        ),
        oracle_tns_alias=get_config_value(
            "DST_ORACLE_TNS_ALIAS",
            section="database-destination",
            cfg_parser=cfg,
            default=False,
            cast_type=bool,
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
        mssql_trust_server_certificate=(
            cast(
                bool,
                get_config_value(
                    "DST_MSSQL_TRUST_SERVER_CERTIFICATE",
                    section="database-destination",
                    cfg_parser=cfg,
                    default=True,
                    cast_type=bool,
                ),
            )
            if ("mssql" in driver.lower() or "sqlserver" in driver.lower())
            else None
        ),
    )


__all__ = ["load_destination_engine"]
