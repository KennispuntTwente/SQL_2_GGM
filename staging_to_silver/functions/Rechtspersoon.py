# staging_to_silver/functions/queries.py
from sqlalchemy import MetaData, select, and_, or_, func, literal

def RECHTSPERSOON(engine, source_schema=None):
    table_names = ["WVAANB", "SZCRED"]

    metadata = MetaData()
    metadata.reflect(bind=engine,
                     schema=source_schema,
                     only=table_names)

    # grab them (SQLAlchemy keys them as f"{schema}.{name}")
    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    wvaanb, szcred = (
        metadata.tables[name] for name in fq_names
    )

    return (
        select(
            wvaanb.c.VOORZNR.label("RECHTSPERSOON_ID"),
            wvaanb.c.EMAIL.label("EMAILADRES"),
            wvaanb.c.FAX.label("FAXNUMMER"),
            wvaanb.c.AGB_NR.label("IDENTIFICATIE"),
            szcred.c.KVK_NR.label("KVKNUMMER"),
            wvaanb.c.NAAM.label("NAAM"),
            # wvaanb.c.??.label("RECHTSVORM"),
            szcred.c.IBAN.label("REKENINGNUMMER"),
            wvaanb.c.TELEFOON.label("TELEFOONNUMMER"),

            func.concat(
                func.coalesce(wvaanb.c.STRAAT, literal('')),
                literal(' '),
                func.coalesce(wvaanb.c.HUISNUMMER, literal('')),
                func.coalesce(wvaanb.c.HUISLETTER, literal('')),
                func.coalesce(wvaanb.c.HUISNR_TOEV, literal('')),
                func.coalesce(wvaanb.c.AAND_HUISNR, literal('')),
                literal(', '),
                func.coalesce(wvaanb.c.POSTCODE, literal('')),
                literal(' '),
                func.coalesce(wvaanb.c.WOONPLAATS, literal(''))
            ).label("ADRESBINNENLAND")

            func.concat(
                func.coalesce(wvaanb.c.STRAAT, literal('')),
                literal(' '),
                func.coalesce(wvaanb.c.HUISNUMMER, literal('')),
                func.coalesce(wvaanb.c.HUISLETTER, literal('')),
                func.coalesce(wvaanb.c.HUISNR_TOEV, literal('')),
                func.coalesce(wvaanb.c.AAND_HUISNR, literal('')),
                literal(', '),
                func.coalesce(wvaanb.c.POSTCODE, literal('')),
                literal(' '),
                func.coalesce(wvaanb.c.WOONPLAATS, literal(''))
            ).label("ADRESCORRESPONDENTIE")
        )
        .select_from(wvaanb)
        .outerjoin(szcred, wvaanb.c.KODE_CREDITEUR == szcred.c.KODE_CREDITEUR)
   

queries = {
    'RECHTSPERSOON': RECHTSPERSOON,
}
