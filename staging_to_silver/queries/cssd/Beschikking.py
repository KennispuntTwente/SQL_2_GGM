from sqlalchemy import select, cast, literal, String, Date, Integer
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col


def build_beschikking(engine, source_schema=None):
    """
    Returns a SELECT that matches the BESCHIKKING destination schema.
    """
    base_tables = ["wvbesl"]

    metadata = reflect_tables(engine, source_schema, base_tables)
    wvbesl = get_table(
        metadata, source_schema, "wvbesl", required_cols=["besluitnr", "clientnr"]
    )

    return select(
        col(wvbesl, "besluitnr").label("BESCHIKKING_ID"),
        col(wvbesl, "clientnr").label("CLIENT_ID"),
        col(wvbesl, "besluitnr").label("HEEFT_VOORZIENINGEN_BESCHIKTE_VOORZIENING_ID"),
        cast(literal(None), String(20)).label("CODE"),
        cast(literal(None), String(200)).label("COMMENTAAR"),
        cast(literal(None), Date).label("DATUMAFGIFTE"),
        cast(literal(None), Integer).label("GRONDSLAGEN"),
        cast(literal(None), String(255)).label("WET"),
    ).select_from(wvbesl)


# Map target table names to query builder functions
__query_exports__ = {
    "BESCHIKKING": build_beschikking,
}
