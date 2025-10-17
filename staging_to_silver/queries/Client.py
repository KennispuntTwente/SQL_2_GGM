from sqlalchemy import MetaData, select, cast, literal, String
from utils.database.naming import normalize_table_name, get_table_column, normalize_column_name


def build_client(engine, source_schema=None):
    """
    Returns a SELECT that matches the CLIENT destination schema.
    Based on previous implementation in staging_to_silver/functions/Client.py
    """
    table_names = [normalize_table_name("SZCLIENT", kind="source")]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    (szclient,) = (metadata.tables[name] for name in fq_names)

    return (
        select(
            get_table_column(szclient, "CLIENTNR").label(
                normalize_column_name("RECHTSPERSOON_ID", kind="destination")
            ),
            get_table_column(szclient, "IND_GEZAG").label(
                normalize_column_name("GEZAGSDRAGERGEKEND_ENUM_ID", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("CODE", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("JURIDISCHESTATUS", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("WETTELIJKEVERTEGENWOORDIGING", kind="destination")
            ),
        )
        .select_from(szclient)
    )


__query_exports__ = {
    "CLIENT": build_client,
}
