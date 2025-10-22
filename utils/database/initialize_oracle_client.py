import logging
import oracledb
from utils.config.get_config_value import get_config_value


def initialize_oracle_client(
    config_key="SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=None
):
    """
    Initialize the Oracle client using a path specified in configuration.

    Parameters:
    - config_key (str): The key to fetch the Oracle client path from config.
    - cfg_parser: Configuration parser object passed to get_config_value (if needed).
    """
    oracle_client_path = get_config_value(config_key, cfg_parser=cfg_parser)
    if oracle_client_path:
        logging.getLogger(__name__).info(
            "Initializing Oracle client with path: %s", oracle_client_path
        )
        oracledb.init_oracle_client(lib_dir=oracle_client_path)
        
def try_init_oracle_client() -> bool:
    # Only initialize if a path is configured; otherwise no-op
    client_path = get_config_value("SRC_CONNECTORX_ORACLE_CLIENT_PATH")
    if not client_path:
        return False
    try:
        initialize_oracle_client("SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=None)
        logging.getLogger(__name__).info("Oracle Instant Client initialized successfully")
        return True
    except Exception as exc:
        logging.getLogger(__name__).exception(
            "Failed to initialize Oracle Instant Client for ConnectorX: %s", exc
        )
        return False
