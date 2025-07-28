import os

def get_config_value(key, section="database", cfg_parser=None):
    """
    Get configuration value from INI file if present, otherwise from environment variable.
    """
    # Try INI first
    if cfg_parser and cfg_parser.has_option(section, key):
        print(f"Using INI value for {key} in section [{section}]")
        ini_value = cfg_parser.get(section, key)

        # If ini_value is '', set to None
        if ini_value == '':
            ini_value = None

        # If ini_value is None, warn in console
        if ini_value is None:
            print(f"Warning: {key} in section [{section}] is not set or empty in INI file (returning None)")

        return ini_value

    # Fallback to environment variable
    print(f"Using environment variable for {key}")
    env_value = os.environ.get(key)

    # If env_value is None, warn in console
    if env_value is None:
        print(f"Warning: {key} is not set in environment variables (returning None)")

    return env_value
