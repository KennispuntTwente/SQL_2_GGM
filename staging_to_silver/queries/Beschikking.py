from sqlalchemy import MetaData, select, cast, literal, String, Date, Integer


def build_beschikking(engine, source_schema=None):
    """
    Returns a SELECT that matches the BESCHIKKING destination schema.
    """
    table_names = ["wvbesl"]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [
        f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names
    ]
    # Only one table expected, unpack it
    (wvbesl,) = (metadata.tables[name] for name in fq_names)

    return select(
        wvbesl.c.besluitnr.label("BESCHIKKING_ID"),
        wvbesl.c.clientnr.label("CLIENT_ID"),
        wvbesl.c.besluitnr.label("HEEFT_VOORZIENINGEN_BESCHIKTE_VOORZIENING_ID"),
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
