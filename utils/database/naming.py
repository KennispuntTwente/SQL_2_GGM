from typing import Literal, Optional
from sqlalchemy import Table

from utils.config.get_config_value import get_config_value


def _apply_case(name: str, mode: Optional[str]) -> str:
    if not mode:
        return name
    mode_l = str(mode).lower()
    if mode_l == "upper":
        return name.upper()
    if mode_l == "lower":
        return name.lower()
    # unknown or 'keep'
    return name


def normalize_table_name(
    name: str,
    kind: Literal["source", "destination"] = "destination",
    case: Optional[str] = None,
) -> str:
    """
    Normalize a table name according to configuration or an explicit case override.

    - kind: 'source' | 'destination' controls which config key is consulted.
    - case: when provided, overrides config. Allowed values: 'upper', 'lower', None.

    Config keys (section [settings]):
      - SOURCE_TABLE_NAME_CASE
      - DESTINATION_TABLE_CASE (preferred)
      - TABLE_NAME_CASE (deprecated fallback for destination)
    """
    # Explicit override wins
    if case:
        return _apply_case(name, case)

    if kind == "source":
        mode = get_config_value(
            "SOURCE_TABLE_NAME_CASE", section="settings", cfg_parser=None, default=None
        )
        return _apply_case(name, mode)

    # destination (default): prefer DESTINATION_TABLE_CASE, fall back to legacy TABLE_NAME_CASE
    dest_mode = get_config_value(
        "DESTINATION_TABLE_CASE", section="settings", cfg_parser=None, default=None
    )
    if not dest_mode:
        dest_mode = get_config_value(
            "TABLE_NAME_CASE", section="settings", cfg_parser=None, default=None
        )
    return _apply_case(name, dest_mode)


def normalize_column_name(
    name: str,
    kind: Literal["source", "destination"] = "destination",
    case: Optional[str] = None,
) -> str:
    """
    Normalize a column name according to configuration or explicit override.

    Config keys (section [settings]):
      - SOURCE_COLUMN_NAME_CASE
      - DESTINATION_COLUMN_NAME_CASE (preferred)
      - COLUMN_NAME_CASE (deprecated fallback for destination)
    """
    if case:
        return _apply_case(name, case)

    if kind == "source":
        mode = get_config_value(
            "SOURCE_COLUMN_NAME_CASE", section="settings", cfg_parser=None, default=None
        )
        return _apply_case(name, mode)

    dest_mode = get_config_value(
        "DESTINATION_COLUMN_NAME_CASE", section="settings", cfg_parser=None, default=None
    )
    if not dest_mode:
        dest_mode = get_config_value(
            "COLUMN_NAME_CASE", section="settings", cfg_parser=None, default=None
        )
    return _apply_case(name, dest_mode)


def get_table_column(
    table: Table,
    name: str,
    *,
    kind: Literal["source", "destination"] = "source",
    case: Optional[str] = None,
):
    """
    Resolve a column from a reflected Table using a normalized name and case-insensitive fallback.
    - kind: which config to use for normalization (default 'source')
    - case: explicit override for normalization mode
    """
    desired = normalize_column_name(name, kind=kind, case=case)
    # Direct hit
    try:
        return table.columns[desired]
    except KeyError:
        pass

    # Case-insensitive map
    ci_map = {c.name.lower(): c for c in table.columns}
    found = ci_map.get(desired.lower())
    if found is not None:
        return found

    # Try upper/lower variants explicitly
    for candidate in (desired.upper(), desired.lower()):
        try:
            return table.columns[candidate]
        except KeyError:
            continue

    available = [c.name for c in table.columns]
    raise KeyError(
        f"Column '{name}' (normalized='{desired}') not found in table {getattr(table, 'fullname', table.name)}. "
        f"Available: {available}"
    )
