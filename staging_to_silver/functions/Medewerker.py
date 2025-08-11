# staging_to_silver/functions/queries.py
from sqlalchemy import MetaData, select, and_, or_, func, literal, case

def MEDEWERKER(engine, source_schema=None):
    table_names = ["SZWERKER"]

    metadata = MetaData()
    metadata.reflect(bind=engine,
                     schema=source_schema,
                     only=table_names)

    # grab them (SQLAlchemy keys them as f"{schema}.{name}")
    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    szwerker = (
        metadata.tables[name] for name in fq_names
    )

    return (
        select(
            szwerker.c.KODE_WERKER.label("MEDEWERKER_ID"),
            szwerker.c.NAAM.label("ACHTERNAAM"),
            szwerker.c.KODE_INSTAN.label("FUNCTIE"),
            szwerker.c.E_MAIL.label("EMAILADRES"),
            szwerker.c.IND_GESLACHT.label("GESLACHTSAANDUIDING"),
            szwerker.c.TOELICHTING.label("MEDEWERKERTOELICHTING"),
            szwerker.c.TELEFOON.label("TELEFOONNUMMER"),

            cast(literal(None), Date).label("DATUMINDIENST"),
            cast(literal(None), Date).label("DATUMUITDIENST"),
            cast(literal(None), Date).label("EXTERN"),
            cast(literal(None), Date).label("MEDEWERKERIDENTIFICATIE"),
            cast(literal(None), Date).label("ROEPNAAM"),
            cast(literal(None), Date).label("VOORLETTERS"),
            cast(literal(None), Date).label("VOORVOEGSELACHTERNAAM"),
        )
           
        .select_from(szwerker)
    )
            

queries = {
    'MEDEWERKER': MEDEWERKER
}
