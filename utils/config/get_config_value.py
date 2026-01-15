import os
import logging
from typing import Any, Callable, Optional, Tuple

# Track which keys we've already warned about this session to avoid log spam
_warned_env_keys: set[str] = set()
_warned_ini_missing: set[tuple[str, str]] = set()  # (section, key)


def _ensure_console_logging():
    """Ensure there's at least one console handler without causing duplicates.

    We attach a minimal StreamHandler only when no handlers exist, and mark it as
    _ggmpilot_managed so our main setup can later replace/remove it cleanly.
    Avoids duplicate console output when setup_logging runs after early config reads.
    """
    root = logging.getLogger()
    if not root.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s [%(name)s] %(message)s")
        )
        setattr(ch, "_ggmpilot_managed", True)
        root.addHandler(ch)


def interpret_value(value):
    """
    Converts string representations of booleans/numbers to actual bools if applicable.
    Otherwise, returns the original string.
    """
    if value is None:
        return None

    val_lower = value.strip().lower()
    if val_lower in ("true", "1", "yes", "on"):
        return True
    elif val_lower in ("false", "0", "no", "off"):
        return False
    return value  # Leave as-is (likely a string)


def _cast_value(
    value: Any,
    cast_type: Optional[Callable[[Any], Any] | type] = None,
    allow_none_if_cast_fails: bool = False,
) -> Any:
    """
    Optionally cast the value to a given type. If casting fails and
    allow_none_if_cast_fails is True, return None; otherwise raise.

    Special handling for booleans from common string forms.
    """
    if value is None:
        return None

    if cast_type is None:
        # Preserve legacy behavior: interpret True/False from strings
        return interpret_value(str(value))

    # Normalize input to string for string-based parsing
    raw = value
    s = str(value).strip()

    try:
        if cast_type is bool:
            # Map common string forms; fall back to Python truthiness for other values
            lowered = s.lower()
            if lowered in ("true", "1", "yes", "on"):
                return True
            if lowered in ("false", "0", "no", "off"):
                return False
            # If already a bool, return as-is
            if isinstance(raw, bool):
                return raw
            # Try numeric coercion to bool if it looks like a number
            try:
                return bool(int(s))
            except Exception:
                return bool(raw)
        elif cast_type is int:
            return int(s)
        elif cast_type is float:
            return float(s)
        elif cast_type is str:
            return str(value)
        else:
            # If a custom callable/type is provided, try calling it
            return cast_type(value)  # type: ignore[misc]
    except Exception:
        if allow_none_if_cast_fails:
            return None
        raise


def get_config_value(
    key: str,
    section: str = "database",
    cfg_parser=None,
    default: Any = None,
    print_value: bool = True,
    section_is_prefix_for_env: bool = False,
    ask_in_command_line: bool = False,
    *,
    cast_type: Optional[Callable[[Any], Any] | type] = None,
    allow_none_if_cast_fails: bool = False,
    silent_if_missing: bool = False,
):
    """
    Get configuration value from INI file if present and non-empty, otherwise from environment variable
    if present and non-empty, otherwise return `default`.

    Priority: INI > ENV > default. Empty strings are treated as missing.
    Interprets boolean-like values as actual booleans.
    Logging: missing INI option or ENV var warnings are emitted at most once per
    key per process to avoid repetitive log spam.

    Args:
        silent_if_missing: If True, suppress warnings when the key is not found
            in INI or ENV. Useful for optional per-entity config keys.
    """
    _ensure_console_logging()

    source: Tuple[str, Any] | None = None

    if ask_in_command_line:
        user_input = input(
            f"Please enter value for {key} (or leave blank for INI/ENV/default): "
        )
        if user_input.strip() != "":
            source = ("CLI", user_input)
        else:
            logging.getLogger(__name__).info(
                "No input provided for %s, falling back to INI/ENV/default.", key
            )

    # Try INI first
    if source is None and cfg_parser and cfg_parser.has_option(section, key):
        logging.getLogger(__name__).debug(
            "Using INI value for %s in section [%s]", key, section
        )
        ini_value = cfg_parser.get(section, key)
        if ini_value.strip() == "":
            # Warn only once per (section, key) per process, unless silent
            if not silent_if_missing:
                warn_key = (section, key)
                if warn_key not in _warned_ini_missing:
                    _warned_ini_missing.add(warn_key)
                    logging.getLogger(__name__).warning(
                        "Warning: %s in section [%s] is not set or empty in INI file (falling back).",
                        key,
                        section,
                    )
        else:
            source = (f"INI[{section}]", ini_value)

    # Fallback to environment variable
    if source is None:
        logging.getLogger(__name__).debug("Using environment variable for %s", key)
        env_key = key
        if section_is_prefix_for_env:
            env_key = f"{section.upper()}_{key.upper()}"
            logging.getLogger(__name__).debug(
                "Applied section prefix to environment variable key: %s", env_key
            )
        env_value = os.environ.get(env_key)
        if env_value is None or env_value.strip() == "":
            # Warn only once per env variable name per process, unless silent
            if not silent_if_missing:
                if env_key not in _warned_env_keys:
                    _warned_env_keys.add(env_key)
                    logging.getLogger(__name__).warning(
                        "Warning: %s is not set or is empty in environment variables (falling back).",
                        env_key,
                    )
        else:
            source = (f"ENV[{env_key}]", env_value)

    # Final fallback to default
    # Finalize value (default or chosen source), apply optional casting, and log
    raw_value = default if source is None else source[1]
    casted = _cast_value(
        raw_value,
        cast_type=cast_type,
        allow_none_if_cast_fails=allow_none_if_cast_fails,
    )
    if print_value:
        src_label = "default" if source is None else source[0]
        logging.getLogger(__name__).info("%s for %s: %s", src_label, key, casted)
    return casted
