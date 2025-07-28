import os
import sys
import warnings
import argparse
import configparser

def parse_args_and_load_parsers(
    prog_desc: str = "Run source to staging data migration",
    src_arg: tuple = ("--source-config", "-s"),
    dst_arg: tuple = ("--destination-config", "-t")
):
    """
    Parses CLI arguments for source‑ and destination‑config INIs, 
    then returns (args, source_cfg, dest_cfg), where each cfg is a
    configparser.ConfigParser() that’s read from the given path
    or left empty (with a warning) if the file doesn’t exist.
    Logs to console what it’s doing for each.
    """
    # 1) build the parser
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument(
        *src_arg,
        help="Settings for source (credentials, tables to extract) in INI format "
             "(optional - will use .env if not provided)"
    )
    parser.add_argument(
        *dst_arg,
        help="Settings for destination (credentials, database, schema, etc.) in INI "
             "format (optional - will use .env if not provided)"
    )

    # 2) parse args (empty list in notebooks)
    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
        args = parser.parse_args([])
    else:
        args = parser.parse_args()

    # 3) helper to load each config file or warn
    def _load(path, name):
        cfg = configparser.ConfigParser()
        if path:
            print(f"→ Attempting to load {name} config from: {path}")
            if os.path.exists(path):
                cfg.read(path)
                print(f"✔ Loaded {name} config from: {path}")
            else:
                warnings.warn(f"{name.capitalize()} config file not found: {path}. Falling back to environment variables.")
                print(f"⚠ Falling back to environment for {name} config")
        else:
            print(f"→ No {name} config path provided; using environment variables")
        return cfg

    source_cfg = _load(args.source_config, "source")
    dest_cfg   = _load(args.destination_config, "destination")

    return args, source_cfg, dest_cfg
