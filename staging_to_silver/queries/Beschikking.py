from sqlalchemy import MetaData, select, cast, literal, String, Date, Integer
from utils.database.naming import normalize_table_name, get_table_column, normalize_column_name

def build_beschikking(engine, source_schema=None):
    """
    Returns a SELECT that matches the BESCHIKKING destination schema.
    """
    table_names = [normalize_table_name("WVBESL", kind="source")]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    # Only one table expected, unpack it
    (wvbesl,) = (metadata.tables[name] for name in fq_names)
    
    return (
        select(
            get_table_column(wvbesl, "BESLUITNR").label(
                normalize_column_name("BESCHIKKING_ID", kind="destination")
            ),
            get_table_column(wvbesl, "CLIENTNR").label(
                normalize_column_name("CLIENT_ID", kind="destination")
            ),
            get_table_column(wvbesl, "BESLUITNR").label(
                normalize_column_name(
                    "HEEFT_VOORZIENINGEN_BESCHIKTE_VOORZIENING_ID", kind="destination"
                )
            ),
            cast(literal(None), String(20)).label(
                normalize_column_name("CODE", kind="destination")
            ),
            cast(literal(None), String(200)).label(
                normalize_column_name("COMMENTAAR", kind="destination")
            ),
            cast(literal(None), Date).label(
                normalize_column_name("DATUMAFGIFTE", kind="destination")
            ),
            cast(literal(None), Integer).label(
                normalize_column_name("GRONDSLAGEN", kind="destination")
            ),
            cast(literal(None), String(255)).label(
                normalize_column_name("WET", kind="destination")
            ),
        )
        .select_from(wvbesl)
    )

# Map target table names to query builder functions
__query_exports__ = {
    "BESCHIKKING": build_beschikking,
}
