from __future__ import annotations

from typing import Iterable, List

from sqlalchemy import MetaData, inspect
from sqlalchemy.sql.schema import Table
from utils.config.get_config_value import get_config_value


def _unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        out.append(it)
    return out


def _get_source_name_matching_mode() -> str:
    # Read via config helper: INI > ENV > default
    v = (
        str(
            get_config_value(
                "STAGING_NAME_MATCHING",
                section="settings",
                cfg_parser=None,
                default="auto",
                print_value=False,
            )
            or "auto"
        )
        .strip()
        .lower()
    )
    return v if v in {"auto", "strict"} else "auto"


def _get_source_table_name_case() -> str | None:
    v = (
        str(
            get_config_value(
                "STAGING_TABLE_NAME_CASE",
                section="settings",
                cfg_parser=None,
                default="",
                print_value=False,
            )
            or ""
        )
        .strip()
        .lower()
    )
    if v in {"upper", "lower"}:
        return v
    return None


def _apply_case_preference(name: str) -> List[str]:
    pref = _get_source_table_name_case()
    if pref == "upper":
        ordered = [name.upper(), name]
    elif pref == "lower":
        ordered = [name.lower(), name.upper()]
    else:
        ordered = [name, name.upper()]
    # de-dup while preserving order
    return _unique_preserve_order(ordered)


def _get_source_column_name_case() -> str | None:
    """
    Optional preference for staging column name case when resolving columns.
    Values: "upper" | "lower" | None (no preference)
    """
    v = (
        str(
            get_config_value(
                "STAGING_COLUMN_NAME_CASE",
                section="settings",
                cfg_parser=None,
                default="",
                print_value=False,
            )
            or ""
        )
        .strip()
        .lower()
    )
    if v in {"upper", "lower"}:
        return v
    return None


def _apply_column_case_preference(name: str) -> List[str]:
    """
    Build an ordered list of column-name candidates honoring STAGING_COLUMN_NAME_CASE.
    Preference rules mirror table-name handling:
    - upper: [NAME.upper(), NAME]
    - lower: [NAME.lower(), NAME.upper()]
    - None:  [NAME, NAME.upper()] (keeps historical behavior where UPPER often exists)
    """
    pref = _get_source_column_name_case()
    if pref == "upper":
        ordered = [name.upper(), name]
    elif pref == "lower":
        ordered = [name.lower(), name.upper()]
    else:
        ordered = [name, name.upper()]
    return _unique_preserve_order(ordered)


def reflect_tables(engine, schema: str | None, base_names: Iterable[str]) -> MetaData:
    """
    Reflect tables from a schema using a list of base names, adding UPPER variants
    to tolerate case differences across dialects and staging conventions.

    Returns a populated MetaData instance.
    """
    metadata = MetaData()
    mode = _get_source_name_matching_mode()

    # Build candidate list in preferred order
    candidates: List[str] = []
    for n in base_names:
        candidates.extend(_apply_case_preference(n))
    only_list = _unique_preserve_order(candidates)

    if mode == "strict":
        # In strict mode, reflect only table names that actually exist.
        # However, when both case-variants exist (e.g., 'wvbesl' and 'WVBESL'),
        # reflect ALL present variants in preferred order so that downstream
        # selection (e.g., required_cols matching) can pick the correct one.
        insp = inspect(engine)
        try:
            present = set(insp.get_table_names(schema=schema))
        except Exception:
            # Fallback: try without schema (some dialects treat default schema)
            present = set(insp.get_table_names())

        selected: List[str] = []
        missing: List[str] = []
        for base in base_names:
            found_any = False
            for candidate in _apply_case_preference(base):
                if candidate in present:
                    selected.append(candidate)
                    found_any = True
            if not found_any:
                missing.append(base)

        if missing:
            # Mirror SQLAlchemy's error style but clarify base names not found
            raise KeyError(
                f"Table not found for base name(s) {tuple(missing)} in schema '{schema}'"
            )

        if selected:
            metadata.reflect(bind=engine, schema=schema, only=selected)
    else:
        targets = {n.lower() for n in only_list}

        # Use a predicate for `only` so that missing case variants don't error out
        def _only(name: str, _md: MetaData) -> bool:  # pragma: no cover - trivial
            return name.lower() in targets

        metadata.reflect(bind=engine, schema=schema, only=_only)
    return metadata


def get_table(
    metadata: MetaData,
    schema: str | None,
    base_name: str,
    required_cols: Iterable[str] | None = None,
) -> Table:
    """
    Return a Table from metadata for a base name, trying both exact and UPPER variants,
    then falling back to case-insensitive match within the given schema.
    """
    # Try exact and UPPER variants
    candidates: List[Table] = []
    mode = _get_source_name_matching_mode()

    # Try preferred order decided by STAGING_TABLE_NAME_CASE
    for name in _apply_case_preference(base_name):
        key = f"{schema + '.' if schema else ''}{name}"
        tbl = metadata.tables.get(key)
        if tbl is not None:
            candidates.append(tbl)

    # Fallback: any table whose unqualified name matches case-insensitively
    if mode != "strict":
        target = base_name.lower()
        for key, tbl in metadata.tables.items():
            # For MSSQL cross-database schemas, keys can look like 'db.schema.table'.
            # Split on the LAST dot to get the table name rather than 'schema.table'.
            unqualified = key.rsplit(".", 1)[-1]
            if unqualified.lower() == target:
                if schema is None or key.startswith(f"{schema}."):
                    candidates.append(tbl)

    # If required columns specified, prefer a table that contains them
    if required_cols:
        req = {c.lower() for c in required_cols}
        for tbl in candidates:
            cols = {
                (getattr(c, "key", None) or getattr(c, "name", "")).lower()
                for c in tbl.c
            }
            if req.issubset(cols):
                return tbl
        # No candidate satisfies the required columns; be explicit rather than
        # returning a mismatched table which would fail later at column lookup.
        raise KeyError(
            f"Table '{base_name}' found but missing required columns {sorted(req)} in schema '{schema}'"
        )

    if candidates:
        return candidates[0]

    raise KeyError(f"Table not found for base name '{base_name}' in schema '{schema}'")


def col(table: Table, name: str):
    """
    Fetch a column from a Table with case-insensitive matching on the column key.
    Prefers an exact case-insensitive match; falls back to dict-style access if present.
    """
    mode = _get_source_name_matching_mode()
    # Note: STAGING_COLUMN_NAME_CASE influences candidate ordering via
    # _apply_column_case_preference; we don't need the raw value here.

    # Build an ordered list of candidate names to try, honoring preference but
    # still considering the typical UPPER variant used in many staging sources.
    candidates: List[str] = _apply_column_case_preference(name)

    # Try direct lookups first (exact key matches) honoring preferences
    for candidate in _unique_preserve_order(candidates):
        try:
            return table.c[candidate]
        except Exception:
            pass

    # Fallback: case-insensitive scan unless in strict mode
    if mode != "strict":
        lname = name.lower()
        for c in table.c:
            key = getattr(c, "key", None) or getattr(c, "name", None)
            if key is not None and str(key).lower() == lname:
                return c
    # Fallback: exact lookup (may raise)
    try:
        return table.c[name]
    except Exception:
        raise AttributeError(name)
