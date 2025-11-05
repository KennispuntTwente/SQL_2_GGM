"""
Utilities for safe, dialect-aware quoting of SQL identifiers.

We prefer SQLAlchemy's identifier preparer where possible. Use these helpers
only in the few places where we must build raw SQL strings (e.g., TRUNCATE or
SQL text executed outside of SQLAlchemy DDL helpers).
"""
from __future__ import annotations

from typing import Iterable, Optional, Sequence, Union

from sqlalchemy.engine import Dialect, Engine


def _get_dialect(obj: Union[str, Dialect, Engine]) -> Dialect:
    if hasattr(obj, "dialect") and hasattr(obj.dialect, "name"):
        return obj.dialect  # type: ignore[return-value]
    if isinstance(obj, Dialect):
        return obj
    # Fallback: construct a lightweight default quoting behavior based on name
    from sqlalchemy.dialects import registry  # type: ignore
    from sqlalchemy.engine import url

    name = str(obj).lower()
    # Try to resolve via make_url for strings like postgresql+psycopg2
    try:
        u = url.make_url(name if "://" in name else f"{name}://")
        name = (u.get_backend_name() or name).lower()
    except Exception:
        pass

    # Use SQLAlchemy registry to get a Dialect class; fall back to default
    try:
        dialect_cls = registry.load(f"{name}.dialect")
        return dialect_cls()
    except Exception:
        # Use default (PostgreSQL-like) quoting if we can't resolve
        from sqlalchemy.dialects import postgresql

        return postgresql.dialect()  # type: ignore[return-value]


def quote_ident(dialect_or_engine: Union[str, Dialect, Engine], name: str) -> str:
    """Quote a single identifier (schema/table/column) per dialect rules."""
    d = _get_dialect(dialect_or_engine)
    return d.identifier_preparer.quote(name)


def quote_fqn(
    dialect_or_engine: Union[str, Dialect, Engine],
    parts: Sequence[Optional[str]] | Iterable[Optional[str]],
) -> str:
    """
    Quote and join a fully-qualified name from parts.

    - Skips falsy/None parts.
    - Uses MSSQL [db].[schema].[table] vs standard "schema"."table" as per dialect.
    """
    d = _get_dialect(dialect_or_engine)
    quoted: list[str] = []
    for p in parts:
        if not p:
            continue
        quoted.append(d.identifier_preparer.quote(str(p)))
    return ".".join(quoted)


def quote_truncate_target(
    dialect_or_engine: Union[str, Dialect, Engine],
    db: Optional[str],
    schema: Optional[str],
    table: str,
) -> str:
    """
    Build a dialect-appropriate, fully quoted target for TRUNCATE/DELETE statements.

    Some dialects (notably MSSQL) support cross-database references; include db when
    provided. For others, db is ignored.
    """
    d = _get_dialect(dialect_or_engine)
    dname = (getattr(d, "name", "") or "").lower()
    if dname == "mssql" and db:
        return quote_fqn(d, [db, schema, table])
    return quote_fqn(d, [schema, table])


def mssql_bracket_escape(name: str) -> str:
    """Escape a string for use inside [bracket] quoting in a dynamic SQL string."""
    return name.replace("]", "]]" )
