import os

def get_config_value(key, section="database", cfg_parser=None, default=None):
    """
    Get configuration value from INI file if present and non-empty, otherwise from environment variable
    if present and non-empty, otherwise return `default`.

    Priority: INI > ENV > default. Empty strings are treated as missing.
    """
    # Try INI first
    if cfg_parser and cfg_parser.has_option(section, key):
        print(f"Using INI value for {key} in section [{section}]")
        ini_value = cfg_parser.get(section, key)

        # Treat empty string as missing
        if ini_value == '':
            ini_value = None

        if ini_value is None:
            print(f"Warning: {key} in section [{section}] is not set or empty in INI file (falling back).")
        else:
            return ini_value

    # Fallback to environment variable
    print(f"Using environment variable for {key}")
    env_value = os.environ.get(key)

    # Treat empty string as missing
    if env_value == '':
        env_value = None

    if env_value is None:
        print(f"Warning: {key} is not set or is empty in environment variables (falling back).")
    else:
        return env_value

    # Final fallback to default
    print(f"Using default value for {key}")
    return default
