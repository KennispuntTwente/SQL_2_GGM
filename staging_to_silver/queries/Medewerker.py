from sqlalchemy import select, cast, literal, Date, String
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col


def build_medewerker(engine, source_schema=None):
    base_tables = ["szwerker"]

    metadata = reflect_tables(engine, source_schema, base_tables)
    szwerker = get_table(
        metadata,
        source_schema,
        "szwerker",
        required_cols=[
            "kode_werker",
            "naam",
            "kode_instan",
            "e_mail",
            "ind_geslacht",
            "toelichting",
            "telefoon",
        ],
    )

    return select(
        col(szwerker, "kode_werker").label("MEDEWERKER_ID"),
        col(szwerker, "naam").label("ACHTERNAAM"),
        col(szwerker, "kode_instan").label("FUNCTIE"),
        col(szwerker, "e_mail").label("EMAILADRES"),
        col(szwerker, "ind_geslacht").label("GESLACHTSAANDUIDING"),
        col(szwerker, "toelichting").label("MEDEWERKERTOELICHTING"),
        col(szwerker, "telefoon").label("TELEFOONNUMMER"),
        cast(literal(None), Date).label("DATUMINDIENST"),
        cast(literal(None), Date).label("DATUMUITDIENST"),
        cast(literal(None), String(80)).label("EXTERN"),
        cast(literal(None), String(80)).label("MEDEWERKERIDENTIFICATIE"),
        cast(literal(None), String(80)).label("ROEPNAAM"),
        cast(literal(None), String(80)).label("VOORLETTERS"),
        cast(literal(None), String(80)).label("VOORVOEGSELACHTERNAAM"),
    ).select_from(szwerker)


__query_exports__ = {
    "MEDEWERKER": build_medewerker,
}
