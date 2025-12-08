"""Cross-dialect date conversion helpers for SQLAlchemy queries.

These helpers provide dialect-aware functions for converting YYYYMMDD numeric
values to DATE, handling partial/incomplete dates, date arithmetic, and formatting.
"""

from sqlalchemy import case, cast, Date, func, Integer, literal, String


def _get_dialect(engine) -> str:
    """Extract and normalize the dialect name from an engine."""
    return (engine.dialect.name or "").lower()


def _is_mssql(dialect: str) -> bool:
    """Check if the dialect is Microsoft SQL Server."""
    return dialect in {"mssql", "sql server", "sqlserver"}


def yyyymmdd_to_date(engine, expr):
    """Cast a YYYYMMDD numeric/string value to a DATE across dialects.

    Args:
        engine: SQLAlchemy engine (used to determine dialect).
        expr: Column or expression containing the YYYYMMDD value.

    Returns:
        SQLAlchemy expression that evaluates to a DATE.
    """
    expr_str = cast(expr, String(16))
    dialect = _get_dialect(engine)

    if _is_mssql(dialect):
        return func.convert(Date, func.convert(String(8), expr_str))

    if dialect.startswith("postgres"):
        return func.to_date(expr_str, literal("YYYYMMDD"))

    # Fallback (SQLite, Oracle, etc.)
    return func.to_date(expr_str, literal("YYYYMMDD"))


def incomplete_date_to_date(engine, num_col):
    """Convert a YYYYMMDD numeric to DATE, handling partial dates.

    Adjusts for incomplete dates where month or day is 00:
    - YYYY00DD (month=00) -> add 101 to get YYYY0101
    - YYYYMM00 (day=00)   -> add 1 to get YYYYMM01
    - Values <= 0         -> NULL

    Args:
        engine: SQLAlchemy engine (used to determine dialect).
        num_col: Column containing the numeric YYYYMMDD value.

    Returns:
        SQLAlchemy expression that evaluates to a DATE or NULL.
    """
    num_str = cast(num_col, String(16))
    dialect = _get_dialect(engine)

    adjusted = case(
        (num_col <= literal(0), literal(None)),
        (func.substr(num_str, 5, 2) == literal("00"), num_col + literal(101)),
        (func.substr(num_str, 7, 2) == literal("00"), num_col + literal(1)),
        else_=num_col,
    )
    adjusted_str = cast(adjusted, String(16))

    if _is_mssql(dialect):
        return case(
            (adjusted.is_(None), literal(None)),
            else_=func.convert(Date, adjusted_str),
        )

    if dialect.startswith("postgres"):
        return case(
            (adjusted.is_(None), literal(None)),
            else_=func.to_date(adjusted_str, literal("YYYYMMDD")),
        )

    # Fallback
    return case(
        (adjusted.is_(None), literal(None)),
        else_=func.to_date(adjusted_str, literal("YYYYMMDD")),
    )


def date_minus_one(engine, date_expr):
    """Subtract one day from a DATE across dialects.

    Args:
        engine: SQLAlchemy engine (used to determine dialect).
        date_expr: Column or expression of DATE type.

    Returns:
        SQLAlchemy expression for date - 1 day.
    """
    dialect = _get_dialect(engine)

    if _is_mssql(dialect):
        return func.dateadd("day", -1, date_expr)

    # PostgreSQL, SQLite, Oracle support date - integer
    return date_expr - literal(1)


def current_date_yyyymmdd_minus_one(engine):
    """Return current_date - 1 formatted as integer YYYYMMDD.

    Args:
        engine: SQLAlchemy engine (used to determine dialect).

    Returns:
        SQLAlchemy expression evaluating to integer YYYYMMDD for yesterday.
    """
    dialect = _get_dialect(engine)

    if _is_mssql(dialect):
        return cast(
            func.format(func.dateadd("day", -1, func.getdate()), "yyyyMMdd"),
            Integer,
        )

    if dialect.startswith("postgres"):
        return cast(
            func.to_char(func.current_date() - literal(1), literal("YYYYMMDD")),
            Integer,
        )

    # Fallback
    return cast(
        func.to_char(func.current_date() - literal(1), literal("YYYYMMDD")),
        Integer,
    )


def format_date_yyyymmdd(engine, date_expr):
    """Format a DATE as YYYYMMDD string across dialects.

    Args:
        engine: SQLAlchemy engine (used to determine dialect).
        date_expr: Column or expression of DATE type.

    Returns:
        SQLAlchemy expression evaluating to string 'YYYYMMDD'.
    """
    dialect = _get_dialect(engine)

    if _is_mssql(dialect):
        return func.format(date_expr, literal("yyyyMMdd"))

    if dialect.startswith("postgres"):
        return func.to_char(date_expr, literal("YYYYMMDD"))

    # Fallback
    return func.to_char(date_expr, literal("YYYYMMDD"))


def right_n_chars(engine, expr, n: int):
    """Return the rightmost n characters of an expression.

    Args:
        engine: SQLAlchemy engine (used to determine dialect).
        expr: Column or expression to extract from.
        n: Number of characters to extract.

    Returns:
        SQLAlchemy expression for RIGHT(expr, n) or equivalent.
    """
    dialect = _get_dialect(engine)
    expr_str = cast(expr, String(32))

    if _is_mssql(dialect):
        return func.right(expr_str, n)

    # PostgreSQL, SQLite, Oracle: use RIGHT or SUBSTR
    # func.right works on PostgreSQL; for others use SUBSTR
    if dialect.startswith("postgres"):
        return func.right(expr_str, n)

    # Fallback: use SUBSTR(expr, LENGTH(expr) - n + 1, n)
    start_index = func.length(expr_str) - literal(n) + literal(1)
    return func.substr(expr_str, start_index, n)


def format_bsn(engine, rsofi_column):
    """Return a zero-padded 9-digit string representation for a BSN/RSOFI value.

    Args:
        engine: SQLAlchemy engine (used to determine dialect).
        rsofi_column: Column containing the BSN/RSOFI numeric value.

    Returns:
        SQLAlchemy expression evaluating to 9-char zero-padded string.
    """
    digits = func.coalesce(cast(rsofi_column, String(32)), literal(""))
    padded = literal("000000000").concat(digits)

    return right_n_chars(engine, padded, 9)
