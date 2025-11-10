import logging
from typing import Dict, Callable, cast

from utils.config.get_config_value import get_config_value
from staging_to_silver.functions.query_loader import load_queries
from staging_to_silver.functions.guards import parse_name_list, filter_queries


def prepare_queries(cfg) -> Dict[str, Callable]:
    """
    Build and filter the mapping queries based on configuration.

    Steps:
    - Read SILVER_TABLE_NAME_CASE and SILVER_COLUMN_NAME_CASE
    - Load queries from staging_to_silver.queries using the case preferences
    - Parse QUERY_ALLOWLIST / QUERY_DENYLIST and filter accordingly
    - Log skipped queries
    Returns the selected queries dict keyed by destination table name.
    """
    log = logging.getLogger("staging_to_silver")

    table_name_case = get_config_value(
        "SILVER_TABLE_NAME_CASE", section="settings", cfg_parser=cfg, default=None
    )
    column_name_case = get_config_value(
        "SILVER_COLUMN_NAME_CASE", section="settings", cfg_parser=cfg, default=None
    )

    # Determine additional query sources (folders or individual files) from config
    raw_paths = cast(
        str,
        get_config_value("QUERY_PATHS", section="settings", cfg_parser=cfg, default=""),
    )
    extra_paths = []
    if raw_paths.strip():
        # Split on commas/semicolons/whitespace similar to allow/deny list parsing
        tokens = raw_paths.replace(";", " ").replace(",", " ").split()
        extra_paths = [t.strip() for t in tokens if t.strip()]

    queries = load_queries(
        package="staging_to_silver.queries",
        table_name_case=cast(str, table_name_case)
        or "upper",  # default historical behavior
        column_name_case=cast(str | None, column_name_case),
        extra_files_or_dirs=tuple(extra_paths),
        # Default behavior: scan built-in package only when no custom paths were provided
        scan_package=(len(extra_paths) == 0),
    )

    allow_cfg = cast(
        str,
        get_config_value(
            "QUERY_ALLOWLIST", section="settings", cfg_parser=cfg, default=""
        ),
    )
    deny_cfg = cast(
        str,
        get_config_value(
            "QUERY_DENYLIST", section="settings", cfg_parser=cfg, default=""
        ),
    )

    allow = parse_name_list(allow_cfg)
    deny = parse_name_list(deny_cfg)

    selected = filter_queries(queries, allowlist=allow or None, denylist=deny or None)
    skipped = set(queries.keys()) - set(selected.keys())
    if skipped:
        log.info("Skipping queries (filtered): %s", ", ".join(sorted(skipped)))

    return selected
