from typing import Optional


def qualify_schema(
    dialect_name: str,
    db: Optional[str],
    schema: Optional[str],
    *,
    default_schema: str = "dbo",
) -> Optional[str]:
    """
    Return a dialect-appropriate schema qualifier for reflection and table naming.

    - For MSSQL, when `db` is provided, returns "db.schema_or_default".
    - Otherwise returns just `schema` (or None if empty).

    This intentionally does not validate the existence of db/schema; it only formats.
    """
    d = (dialect_name or "").lower()
    s = (schema or "").strip()
    b = (db or "").strip()
    if d == "mssql" and b:
        return f"{b}.{s or default_schema}"
    return s or None
