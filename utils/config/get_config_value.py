import os


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
):
    """
    Get configuration value from INI file if present and non-empty, otherwise from environment variable
    if present and non-empty, otherwise return `default`.

    Priority: INI > ENV > default. Empty strings are treated as missing.
    Interprets boolean-like values as actual booleans.
    """
    # Try INI first
    if cfg_parser and cfg_parser.has_option(section, key):
        print(f"Using INI value for {key} in section [{section}]")
        ini_value = cfg_parser.get(section, key)

        if ini_value.strip() == "":
            ini_value = None
        else:
            if print_value:
                print(
                    f"INI value for {key} in section [{section}]: {interpret_value(ini_value)}"
                )
            return interpret_value(ini_value)

        print(
            f"Warning: {key} in section [{section}] is not set or empty in INI file (falling back)."
        )

    # Fallback to environment variable
    print(f"Using environment variable for {key}")
    if section_is_prefix_for_env:
        key = f"{section.upper()}_{key.upper()}"
        print(f"Applied section prefix to environment variable key: {key}")
    env_value = os.environ.get(key)

    if env_value is None or env_value.strip() == "":
        print(
            f"Warning: {key} is not set or is empty in environment variables (falling back)."
        )
    else:
        if print_value:
            print(f"Environment variable for {key}: {interpret_value(env_value)}")
        return interpret_value(env_value)

    # Final fallback to default
    print(f"Using default value for {key}")
    if print_value:
        print(f"Default value for {key}: {default}")
    return default
