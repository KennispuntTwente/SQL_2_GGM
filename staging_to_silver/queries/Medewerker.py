from sqlalchemy import MetaData, select, cast, literal, Date, String
from utils.database.naming import normalize_table_name, get_table_column, normalize_column_name


def build_medewerker(engine, source_schema=None):
    table_names = [normalize_table_name("SZWERKER", kind="source")]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    (szwerker,) = (metadata.tables[name] for name in fq_names)

    return (
        select(
            get_table_column(szwerker, "KODE_WERKER").label(
                normalize_column_name("MEDEWERKER_ID", kind="destination")
            ),
            get_table_column(szwerker, "NAAM").label(
                normalize_column_name("ACHTERNAAM", kind="destination")
            ),
            get_table_column(szwerker, "KODE_INSTAN").label(
                normalize_column_name("FUNCTIE", kind="destination")
            ),
            get_table_column(szwerker, "E_MAIL").label(
                normalize_column_name("EMAILADRES", kind="destination")
            ),
            get_table_column(szwerker, "IND_GESLACHT").label(
                normalize_column_name("GESLACHTSAANDUIDING", kind="destination")
            ),
            get_table_column(szwerker, "TOELICHTING").label(
                normalize_column_name("MEDEWERKERTOELICHTING", kind="destination")
            ),
            get_table_column(szwerker, "TELEFOON").label(
                normalize_column_name("TELEFOONNUMMER", kind="destination")
            ),
            cast(literal(None), Date).label(
                normalize_column_name("DATUMINDIENST", kind="destination")
            ),
            cast(literal(None), Date).label(
                normalize_column_name("DATUMUITDIENST", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("EXTERN", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("MEDEWERKERIDENTIFICATIE", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("ROEPNAAM", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("VOORLETTERS", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("VOORVOEGSELACHTERNAAM", kind="destination")
            ),
        )
        .select_from(szwerker)
    )


__query_exports__ = {
    "MEDEWERKER": build_medewerker,
}
