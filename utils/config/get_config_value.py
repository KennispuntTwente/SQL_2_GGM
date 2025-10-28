import os
import logging


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


def get_config_value(
    key,
    section="database",
    cfg_parser=None,
    default=None,
    print_value=True,
    section_is_prefix_for_env=False,
    ask_in_command_line=False,
):
    """
    Get configuration value from INI file if present and non-empty, otherwise from environment variable
    if present and non-empty, otherwise return `default`.

    Priority: INI > ENV > default. Empty strings are treated as missing.
    Interprets boolean-like values as actual booleans.
    """
    _ensure_console_logging()

    if ask_in_command_line:
        user_input = input(
            f"Please enter value for {key} (or leave blank for INI/ENV/default): "
        )
        if user_input.strip() != "":
            if print_value:
                logging.getLogger(__name__).info(
                    "Using command line input for %s: %s",
                    key,
                    interpret_value(user_input),
                )
            return interpret_value(user_input)
        else:
            logging.getLogger(__name__).info(
                "No input provided for %s, falling back to INI/ENV/default.", key
            )

    # Try INI first
    if cfg_parser and cfg_parser.has_option(section, key):
        logging.getLogger(__name__).debug(
            "Using INI value for %s in section [%s]", key, section
        )
        ini_value = cfg_parser.get(section, key)

        if ini_value.strip() == "":
            ini_value = None
        else:
            if print_value:
                logging.getLogger(__name__).info(
                    "INI value for %s in section [%s]: %s",
                    key,
                    section,
                    interpret_value(ini_value),
                )
            return interpret_value(ini_value)

        logging.getLogger(__name__).warning(
            "Warning: %s in section [%s] is not set or empty in INI file (falling back).",
            key,
            section,
        )

    # Fallback to environment variable
    logging.getLogger(__name__).debug("Using environment variable for %s", key)
    if section_is_prefix_for_env:
        key = f"{section.upper()}_{key.upper()}"
        logging.getLogger(__name__).debug(
            "Applied section prefix to environment variable key: %s", key
        )
    env_value = os.environ.get(key)

    if env_value is None or env_value.strip() == "":
        logging.getLogger(__name__).warning(
            "Warning: %s is not set or is empty in environment variables (falling back).",
            key,
        )
    else:
        if print_value:
            logging.getLogger(__name__).info(
                "Environment variable for %s: %s", key, interpret_value(env_value)
            )
        return interpret_value(env_value)

    # Final fallback to default
    logging.getLogger(__name__).debug("Using default value for %s", key)
    if print_value:
        logging.getLogger(__name__).info("Default value for %s: %s", key, default)
    return default
