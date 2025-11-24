from sqlalchemy import cast, Date, func
from sqlalchemy.types import TIMESTAMP


def local_date_amsterdam(col, engine):
    """Cross-dialect conversion of a UTC timestamp to Europe/Amsterdam date.

    - PostgreSQL: use timezone('Europe/Amsterdam', timezone('UTC', ts)) then cast Date
    - MSSQL:       use ts AT TIME ZONE 'UTC' AT TIME ZONE 'W. Europe Standard Time' then cast Date
    - Fallback:    just cast to Date (no tz conversion) to keep query buildable on other dialects
    """

    dialect = (engine.dialect.name or "").lower()
    if dialect == "mssql":
        # Windows timezone ID for Europe/Amsterdam in SQL Server
        return cast(
            col.op("AT TIME ZONE")("UTC").op("AT TIME ZONE")("W. Europe Standard Time"),
            Date,
        )
    elif dialect.startswith("postgres"):
        # Ensure the column is a timestamp before applying timezone conversions
        ts = cast(col, TIMESTAMP)
        return cast(func.timezone("Europe/Amsterdam", func.timezone("UTC", ts)), Date)
    else:
        # For SQLite or other engines used in shape tests, avoid dialect-specific
        # functions and rely on a simple CAST to Date. On SQLite this yields a
        # 4-tuple (year, month, day, None) which SQLAlchemy normally converts
        # back to a `date`, but in some shapes we only care that the expression
        # is buildable; callers should treat this as dialect-specific.
        return cast(col, Date)
