from typing import Callable, Dict, Optional, Set


def is_postgres(engine) -> bool:
    """Return True if the SQLAlchemy engine targets PostgreSQL."""
    try:
        return engine.dialect.name.lower() == "postgresql"
    except Exception:
        return False


def should_defer_constraints(engine) -> bool:
    """Only PostgreSQL supports `SET CONSTRAINTS ALL DEFERRED` globally."""
    return is_postgres(engine)


def validate_upsert_supported(engine) -> None:
    """Raise a clear error if 'upsert' is requested on a non-PostgreSQL backend."""
    if not is_postgres(engine):
        raise ValueError(
            "Write mode 'upsert' is PostgreSQL-only; choose append/overwrite/truncate or switch to PostgreSQL."
        )


def parse_name_list(value: Optional[str]) -> Set[str]:
    """Parse a comma/semicolon/space-separated list into a normalized set of names."""
    if not value:
        return set()
    # Split on commas/semicolons/whitespace and drop empties
    tokens = value.replace(";", " ").replace(",", " ").split()
    return {t.strip() for t in tokens if t.strip()}


def filter_queries(
    queries: Dict[str, Callable],
    allowlist: Optional[Set[str]] = None,
    denylist: Optional[Set[str]] = None,
) -> Dict[str, Callable]:
    """
    Filter discovered queries by optional allow- and deny-lists.
    - When allowlist is non-empty, only names present in it are kept.
    - Denylist names are always removed.
    Matching is case-insensitive using the keys present in the `queries` dict.
    """
    if not queries:
        return {}

    allow_ci = {n.lower() for n in (allowlist or set())}
    deny_ci = {n.lower() for n in (denylist or set())}

    out: Dict[str, Callable] = {}
    for name, fn in queries.items():
        key = name.lower()
        if allow_ci and key not in allow_ci:
            continue
        if key in deny_ci:
            continue
        out[name] = fn
    return out
