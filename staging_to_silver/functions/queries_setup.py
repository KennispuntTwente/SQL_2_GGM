import logging
import re
from typing import Dict, Callable, cast, List

from utils.config.get_config_value import get_config_value
from staging_to_silver.functions.query_loader import load_queries
from staging_to_silver.functions.guards import parse_name_list, filter_queries


def prepare_queries(cfg) -> Dict[str, Callable]:
    """
    Build and filter the mapping queries based on configuration.

    Steps:
    - Read SILVER_TABLE_NAME_CASE and SILVER_COLUMN_NAME_CASE
    - Load queries from staging_to_silver.queries.CSSD using the case preferences
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

    # Determine additional query sources (folders or individual files) from config.
    # Historical behavior split on commas/semicolons/whitespace which broke Windows paths containing spaces.
    # New behavior: only split on commas/semicolons; preserve embedded whitespace; allow optional quoting.
    raw_paths = cast(
        str,
        get_config_value("QUERY_PATHS", section="settings", cfg_parser=cfg, default=""),
    )

    def parse_extra_query_paths(value: str) -> List[str]:
        """Parse QUERY_PATHS config value into a list of file or directory paths.

        Delimiters: comma or semicolon. Whitespace surrounding tokens is trimmed.
        Embedded spaces inside a path are preserved (e.g. C:\\Data Warehouse\\ggm\\queries).
        Optional single or double quotes around a path are removed.
        Empty tokens are ignored. Duplicates are preserved in order (load_queries will de-dup if needed).
        """
        paths: List[str] = []
        # Split strictly on , or ; so spaces remain intact.
        for token in re.split(r"[;,]", value):
            token = token.strip()
            if not token:
                continue
            # Drop surrounding quotes if present and balanced.
            if len(token) >= 2 and token[0] == token[-1] and token[0] in ('"', "'"):
                token = token[1:-1]
            paths.append(token)
        return paths

    extra_paths = parse_extra_query_paths(raw_paths) if raw_paths.strip() else []

    queries = load_queries(
        package="staging_to_silver.queries.CSSD",
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


# Expose parsing helper for tests
def parse_extra_query_paths(value: str) -> List[str]:  # type: ignore[redefinition]
    paths: List[str] = []
    for token in re.split(r"[;,]", value):
        token = token.strip()
        if not token:
            continue
        if len(token) >= 2 and token[0] == token[-1] and token[0] in ('"', "'"):
            token = token[1:-1]
        paths.append(token)
    return paths
