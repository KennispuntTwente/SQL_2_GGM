import oracledb
from source_to_staging.functions.get_config_value import get_config_value

def initialize_oracle_client(config_key="SRC_CONNECTORX_ORACLE_CLIENT_PATH", cfg_parser=None):
    """
    Initialize the Oracle client using a path specified in configuration.

    Parameters:
    - config_key (str): The key to fetch the Oracle client path from config.
    - cfg_parser: Configuration parser object passed to get_config_value (if needed).
    """
    oracle_client_path = get_config_value(config_key, cfg_parser=cfg_parser)
    if oracle_client_path:
        print(f"Initializing Oracle client with path: {oracle_client_path}")
        oracledb.init_oracle_client(lib_dir=oracle_client_path)
