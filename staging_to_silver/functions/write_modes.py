import logging
from typing import Dict, cast

from utils.config.get_config_value import get_config_value


SUPPORTED_MODES = {"append", "overwrite", "truncate", "upsert"}


def _parse_write_modes_from_list(value: str) -> Dict[str, str]:
    """Parse a comma/semicolon/space-separated list of table=mode pairs.

    Example: "A=append, B = truncate; C=overwrite" -> {"a":"append", "b":"truncate", "c":"overwrite"}
    Invalid entries are ignored with a warning.
    """
    log = logging.getLogger("staging_to_silver")
    out: Dict[str, str] = {}
    if not value:
        return out
    # split on comma/semicolon/whitespace
    tokens = value.replace(";", " ").replace(",", " ").split()
    for tok in tokens:
        if "=" not in tok:
            log.warning("Ignoring WRITE_MODES token without '=': %s", tok)
            continue
        k, v = tok.split("=", 1)
        k = k.strip()
        v = v.strip().lower()
        if not k or not v:
            continue
        out[k.lower()] = v
    return out


def load_write_modes(cfg, default_mode: str = "overwrite") -> Dict[str, str]:
    """Load per-table write modes from configuration.

    Priority & merge rules:
      1) [write-modes] section in INI (case-insensitive keys) → wins over list
      2) settings key WRITE_MODES (ENV/INI), list like "TAB1=append, TAB2=truncate"

    - Modes are validated against SUPPORTED_MODES; unsupported are ignored with a warning
    - Unspecified tables default to `default_mode` in the caller
    - Returned dict maps lowercased table name → mode (lowercased)
    """
    log = logging.getLogger("staging_to_silver")

    write_modes_ci: Dict[str, str] = {}

    # 1) INI section [write-modes]
    try:
        if cfg.has_section("write-modes"):
            for tbl, mode in cfg.items("write-modes"):
                m = (mode or "").strip().lower()
                if m and m in SUPPORTED_MODES:
                    write_modes_ci[tbl.lower()] = m
                elif m:
                    log.warning(
                        "Ignoring unsupported write-mode '%s' for table '%s' in [write-modes] (supported: %s)",
                        m,
                        tbl,
                        ", ".join(sorted(SUPPORTED_MODES)),
                    )
    except Exception:
        # cfg may be empty parser when no INI file is provided
        pass

    # 2) settings WRITE_MODES, merge without overriding explicit section entries
    write_modes_list = cast(
        str,
        get_config_value(
            "WRITE_MODES", section="settings", cfg_parser=cfg, default=""
        ),
    )
    for tbl, mode in _parse_write_modes_from_list(write_modes_list).items():
        if mode not in SUPPORTED_MODES:
            log.warning(
                "Ignoring unsupported write-mode '%s' for table '%s' in WRITE_MODES (supported: %s)",
                mode,
                tbl,
                ", ".join(sorted(SUPPORTED_MODES)),
            )
            continue
        write_modes_ci.setdefault(tbl, mode)

    # Note: the default is applied by callers when a table isn't present here.
    if default_mode not in SUPPORTED_MODES:
        log.warning(
            "Provided default_mode '%s' is not supported; falling back to 'overwrite'",
            default_mode,
        )
        default_mode = "overwrite"

    return write_modes_ci
