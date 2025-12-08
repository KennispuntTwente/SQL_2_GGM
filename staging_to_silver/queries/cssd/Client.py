from sqlalchemy import select, cast, literal, String
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col


def build_client(engine, source_schema=None):
    """
    Returns a SELECT that matches the CLIENT destination schema.
    Based on previous implementation in staging_to_silver/functions/Client.py
    """
    base_tables = ["szclient"]

    metadata = reflect_tables(engine, source_schema, base_tables)
    szclient = get_table(
        metadata, source_schema, "szclient", required_cols=["clientnr", "ind_gezag"]
    )

    return select(
        col(szclient, "clientnr").label("RECHTSPERSOON_ID"),
        col(szclient, "ind_gezag").label("GEZAGSDRAGERGEKEND_ENUM_ID"),
        cast(literal(None), String(80)).label("CODE"),
        cast(literal(None), String(80)).label("JURIDISCHESTATUS"),
        cast(literal(None), String(80)).label("WETTELIJKEVERTEGENWOORDIGING"),
    ).select_from(szclient)


__query_exports__ = {
    "CLIENT": build_client,
}
