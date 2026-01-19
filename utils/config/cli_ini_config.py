import os
import logging
import sys
import warnings
import argparse
import configparser
from typing import Tuple, Optional


def _ensure_console_logging():
    """Ensure a basic console logger is set so messages are visible like print()."""
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        )


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
        _ensure_console_logging()
        cfg = configparser.ConfigParser()
        if path:
            logging.getLogger(__name__).info("Loading %s config from: %s", name, path)
            if os.path.exists(path):
                cfg.read(path)
                logging.getLogger(__name__).info(
                    "Loaded %s config from: %s", name, path
                )
            else:
                warnings.warn(
                    f"{name.capitalize()} config file not found: {path}. "
                    "Falling back to environment variables."
                )
                logging.getLogger(__name__).warning(
                    "Falling back to environment for %s config", name
                )
        else:
            logging.getLogger(__name__).info(
                "No %s config path provided; using environment variables", name
            )
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
        logging.getLogger(__name__).info("Loading config from: %s", args.config)
        if os.path.exists(args.config):
            cfg.read(args.config)
            logging.getLogger(__name__).info("Loaded config from: %s", args.config)
        else:
            warnings.warn(
                f"Config file not found: {args.config}. Falling back to environment variables."
            )
            logging.getLogger(__name__).warning("Falling back to environment")
    else:
        logging.getLogger(__name__).info(
            "No config path provided; using environment variables"
        )

    return args, cfg
