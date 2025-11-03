from sqlalchemy import MetaData, select, cast, literal, Date, String


def build_medewerker(engine, source_schema=None):
    table_names = ["szwerker"]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [
        f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names
    ]
    (szwerker,) = (metadata.tables[name] for name in fq_names)

    return select(
        szwerker.c.kode_werker.label("MEDEWERKER_ID"),
        szwerker.c.naam.label("ACHTERNAAM"),
        szwerker.c.kode_instan.label("FUNCTIE"),
        szwerker.c.e_mail.label("EMAILADRES"),
        szwerker.c.ind_geslacht.label("GESLACHTSAANDUIDING"),
        szwerker.c.toelichting.label("MEDEWERKERTOELICHTING"),
        szwerker.c.telefoon.label("TELEFOONNUMMER"),
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
