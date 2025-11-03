from sqlalchemy import MetaData, select, cast, literal, String


def build_client(engine, source_schema=None):
    """
    Returns a SELECT that matches the CLIENT destination schema.
    Based on previous implementation in staging_to_silver/functions/Client.py
    """
    table_names = ["szclient"]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [
        f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names
    ]
    (szclient,) = (metadata.tables[name] for name in fq_names)

    return select(
        szclient.c.clientnr.label("RECHTSPERSOON_ID"),
        szclient.c.ind_gezag.label("GEZAGSDRAGERGEKEND_ENUM_ID"),
        cast(literal(None), String(80)).label("CODE"),
        cast(literal(None), String(80)).label("JURIDISCHESTATUS"),
        cast(literal(None), String(80)).label("WETTELIJKEVERTEGENWOORDIGING"),
    ).select_from(szclient)


__query_exports__ = {
    "CLIENT": build_client,
}
