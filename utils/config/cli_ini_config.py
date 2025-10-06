# cli_config.py
import os
import sys
import warnings
import argparse
import configparser
from typing import Tuple, Optional


def parse_and_load_ini_configs(
    prog_desc: str = "Run source to staging data migration",
    src_arg: Tuple[str, str] = ("--source-config", "-s"),
    dst_arg: Tuple[str, str] = ("--destination-config", "-t"),
    allow_notebook_args: bool = True,
) -> Tuple[argparse.Namespace, configparser.ConfigParser, configparser.ConfigParser]:
    """
    Parse CLI args for source/destination INI files and load them.

    Returns (args, source_cfg, dest_cfg), where each cfg is a ConfigParser().
    If a path isn't provided or doesn't exist, returns an empty parser and
    logs a warning (so callers can fall back to env vars).

    Parameters
    ----------
    prog_desc : str
        Description shown in --help.
    src_arg : (str, str)
        Long and short option names for the source config path.
    dst_arg : (str, str)
        Long and short option names for the destination config path.
    allow_notebook_args : bool
        If True and running in a notebook/REPL, parse with empty argv.
    """
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument(
        *src_arg,
        dest="source_config",
        help="Path to source settings (.ini). Optional; fall back to env if omitted.",
    )
    parser.add_argument(
        *dst_arg,
        dest="destination_config",
        help="Path to destination settings (.ini). Optional; fall back to env if omitted.",
    )

    # Parse args (avoid argv noise when in notebooks)
    if allow_notebook_args and ("ipykernel" in sys.modules or "IPython" in sys.modules):
        args = parser.parse_args([])
    else:
        args = parser.parse_args()

    def _load(path: Optional[str], name: str) -> configparser.ConfigParser:
        cfg = configparser.ConfigParser()
        if path:
            print(f"→ Attempting to load {name} config from: {path}")
            if os.path.exists(path):
                cfg.read(path)
                print(f"✔ Loaded {name} config from: {path}")
            else:
                warnings.warn(
                    f"{name.capitalize()} config file not found: {path}. "
                    "Falling back to environment variables."
                )
                print(f"⚠ Falling back to environment for {name} config")
        else:
            print(f"→ No {name} config path provided; using environment variables")
        return cfg

    source_cfg = _load(getattr(args, "source_config", None), "source")
    dest_cfg = _load(getattr(args, "destination_config", None), "destination")
    return args, source_cfg, dest_cfg


def load_single_ini_config(
    prog_desc: str = "Run ETL",
    cfg_arg: Tuple[str, str] = ("--config", "-c"),
    allow_notebook_args: bool = True,
) -> Tuple[argparse.Namespace, configparser.ConfigParser]:
    """
    Convenience wrapper for scripts that only need one .ini.

    Returns (args, cfg). If no path or missing file, returns empty ConfigParser().
    """
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument(
        *cfg_arg,
        dest="config",
        help="Path to settings (.ini). Optional; fall back to env if omitted.",
    )

    if allow_notebook_args and ("ipykernel" in sys.modules or "IPython" in sys.modules):
        args = parser.parse_args([])
    else:
        args = parser.parse_args()

    cfg = configparser.ConfigParser()
    if args.config:
        print(f"→ Attempting to load config from: {args.config}")
        if os.path.exists(args.config):
            cfg.read(args.config)
            print(f"✔ Loaded config from: {args.config}")
        else:
            warnings.warn(
                f"Config file not found: {args.config}. Falling back to environment variables."
            )
            print("⚠ Falling back to environment")
    else:
        print("→ No config path provided; using environment variables")

    return args, cfg
