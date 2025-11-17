import logging
import oracledb
from utils.config.get_config_value import get_config_value

# Cache lookup results to avoid duplicate config reads & warnings when the
# client path is absent (very common outside Oracle deployments). Also guard
# against repeated init_oracle_client calls which oracledb rejects.
_cached_client_paths: dict[str, str | None] = {}
_oracle_client_initialized: bool = False


def initialize_oracle_client(
    config_key: str = "SRC_ORACLE_CLIENT_PATH",
    cfg_parser=None,
    section: str | None = None,
):
    """Initialize Oracle client using a configured path if present.

    Short-circuits when we've already probed this key and found no path, to
    avoid duplicate warnings from repeated get_config_value calls. Also skips
    re-initialization if already initialized successfully.
    """
    logger = logging.getLogger(__name__)

    # If we already attempted this key and found no path, skip re-reading.
    if config_key in _cached_client_paths and not _cached_client_paths[config_key]:
        logger.debug(
            "Oracle client path for %s previously not set; skipping repeat probe.",
            config_key,
        )
        return

    # Determine INI section automatically if not provided
    if section is None:
        if config_key.startswith("SRC_"):
            section = "database-source"
        elif config_key.startswith("DST_"):
            section = "database-destination"
        else:
            section = "database"

    # Fetch (or reuse cached) client path
    oracle_client_path = _cached_client_paths.get(config_key)
    if oracle_client_path is None and config_key not in _cached_client_paths:
        oracle_client_path = get_config_value(
            config_key, section=section, cfg_parser=cfg_parser
        )
        _cached_client_paths[config_key] = oracle_client_path  # cache even if falsy

    # If no path configured, done
    if not oracle_client_path:
        return

    # If already initialized once, don't re-initialize (avoid oracledb error)
    if _oracle_client_initialized:
        logger.debug("Oracle client already initialized; skipping re-init.")
        return

    logger.info("Initializing Oracle client with path: %s", oracle_client_path)
    oracledb.init_oracle_client(lib_dir=oracle_client_path)
    global _oracle_client_initialized
    _oracle_client_initialized = True


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
