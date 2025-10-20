import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Iterable, Optional

from utils.config.get_config_value import get_config_value


def _coerce_level(level_str: str | None, default: int = logging.INFO) -> int:
    if not level_str:
        return default
    try:
        return getattr(logging, str(level_str).upper())
    except AttributeError:
        return default


def setup_logging(
    app_name: str = "ggmpilot",
    cfg_parsers: Optional[Iterable] = None,
    always_console: bool = True,
) -> None:
    """
    Configure root logging with:
    - Always-on console handler (INFO by default)
    - Optional rotating file handler when enabled via config/env

    Configuration keys (INI [logging] section or environment variables):
      - LOG_LEVEL: DEBUG|INFO|WARNING|ERROR (default INFO)
      - LOG_TO_FILE: true|false (default false)
      - LOG_FILE: path to log file (default logs/<app_name>.log)
      - LOG_ROTATE_BYTES: integer max bytes per file (default 5_000_000)
      - LOG_BACKUP_COUNT: integer number of backups to keep (default 3)
      - LOG_FORMAT: optional custom format string

    Notes:
      - INI values take precedence over environment variables (cfg_parsers order is respected).
      - Console logging remains enabled regardless of file logging settings when always_console=True.
    """

    # Combine config parsers into a simple lookup order
    cfg_parsers = list(cfg_parsers or [])

    # Resolve values with INI > ENV > defaults
    def cfg(key: str, default=None):
        # Try each parser in order, then env, then default
        for parser in cfg_parsers:
            val = get_config_value(
                key,
                section="logging",
                cfg_parser=parser,
                default=None,
                print_value=False,
            )
            if val is not None and val != "":
                return val
        # Fallback to env (unprefixed)
        env_val = os.environ.get(key)
        return env_val if env_val not in (None, "") else default

    log_level = _coerce_level(str(cfg("LOG_LEVEL", "INFO")))
    ltf_raw = cfg("LOG_TO_FILE", False)
    log_to_file = str(ltf_raw).strip().lower() in ("true", "1", "on", "yes")
    log_file = str(cfg("LOG_FILE", os.path.join("logs", f"{app_name}.log")))
    rotate_bytes = int(str(cfg("LOG_ROTATE_BYTES", 5_000_000)))
    backup_count = int(str(cfg("LOG_BACKUP_COUNT", 3)))
    fmt = cfg(
        "LOG_FORMAT",
        "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    )

    root = logging.getLogger()
    root.setLevel(log_level)

    # Remove only handlers previously added by this setup (preserve external ones like pytest caplog)
    for h in list(root.handlers):
        if getattr(h, "_ggmpilot_managed", False):
            root.removeHandler(h)

    formatter = logging.Formatter(str(fmt))

    # Console handler (always on by default)
    if always_console:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        setattr(ch, "_ggmpilot_managed", True)
        root.addHandler(ch)

    # Optional rotating file handler
    if log_to_file:
        try:
            os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        except Exception:
            # If directory creation fails, fall back to cwd
            log_file = os.path.basename(log_file)
        fh = RotatingFileHandler(
            log_file,
            maxBytes=rotate_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        setattr(fh, "_ggmpilot_managed", True)
        root.addHandler(fh)

    # Useful banner when reconfiguring
    logger = logging.getLogger(__name__)
    logger.debug(
        "logging configured level=%s console=%s file=%s",
        logging.getLevelName(log_level),
        always_console,
        log_file if log_to_file else None,
    )
