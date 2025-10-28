import logging
import oracledb
from utils.config.get_config_value import get_config_value


def initialize_oracle_client(
    config_key: str = "SRC_ORACLE_CLIENT_PATH", cfg_parser=None
):
    """
    Initialize the Oracle client using a path specified in configuration.

    Parameters:
    - config_key (str): The key to fetch the Oracle client path from config.
    - cfg_parser: Configuration parser object passed to get_config_value (if needed).
    """
    # Read the configured client path for the provided key (INI > ENV)
    oracle_client_path = get_config_value(config_key, cfg_parser=cfg_parser)
    if oracle_client_path:
        logging.getLogger(__name__).info(
            "Initializing Oracle client with path: %s", oracle_client_path
        )
        oracledb.init_oracle_client(lib_dir=oracle_client_path)


def try_init_oracle_client() -> bool:
    """
    Best-effort initialization of the Oracle Instant Client for SQLAlchemy paths.

    Checks environment variables (no INI parser available here) for either
    destination or source keys, preferring destination when present:
      - DST_ORACLE_CLIENT_PATH
      - SRC_ORACLE_CLIENT_PATH

    Returns True on successful initialization, False otherwise. Exceptions are
    caught and logged.
    """
    # Prefer destination key for staging_to_silver; fall back to source key
    client_path_dst = get_config_value("DST_ORACLE_CLIENT_PATH")
    client_path_src = get_config_value("SRC_ORACLE_CLIENT_PATH")
    chosen_key: str | None = None

    if client_path_dst:
        chosen_key = "DST_ORACLE_CLIENT_PATH"
    elif client_path_src:
        chosen_key = "SRC_ORACLE_CLIENT_PATH"
    else:
        return False  # nothing configured in ENV

    try:
        initialize_oracle_client(chosen_key, cfg_parser=None)
        logging.getLogger(__name__).info(
            "Oracle Instant Client initialized successfully"
        )
        return True
    except Exception as exc:
        logging.getLogger(__name__).exception(
            "Failed to initialize Oracle Instant Client: %s", exc
        )
        return False
