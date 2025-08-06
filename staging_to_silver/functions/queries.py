# staging_to_silver/functions/queries.py
from sqlalchemy import MetaData, select, and_, or_, func

def BESCHIKTE_VOORZIENING(engine, source_schema=None):
    table_names = ["WVIND_B","SZREGEL","WVBESL","WVDOS","ABC_REFCOD"]

    metadata = MetaData()
    metadata.reflect(bind=engine,
                     schema=source_schema,
                     only=table_names)

    # grab them (SQLAlchemy keys them as f"{schema}.{name}")
    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    wvind_b, szregel, wvbesl, wvdos, abc_refcod = (
        metadata.tables[name] for name in fq_names
    )

    return (
        select(
            wvind_b.c.DD_EIND.label("Datumeinde"),
            wvind_b.c.DD_BEGIN.label("Datumstart"),
            wvind_b.c.EENHEID.label("Eenheid"),
            wvind_b.c.CODE_FREQUENTIE.label("Frequentie"),
            wvind_b.c.VOLUME.label("Omvang"),
            wvind_b.c.STATUS_INDICATIE.label("Status"),
            szregel.c.OMSCHRYVING.label("Wet"),
            func.concat(
                wvind_b.c.BESLUITNR,
                wvind_b.c.VOLGNR_IND
            ).label("BeschikteVoorzieningID"),
            wvbesl.c.BESLUITNR.label("BeschikkingID"),
            abc_refcod.c.OMSCHRYVING.label("Redeneinde"),
        )
        .select_from(wvind_b)
        .outerjoin(szregel, wvind_b.c.KODE_REGELING == szregel.c.KODE_REGELING)
        .outerjoin(wvbesl,  wvind_b.c.BESLUITNR   == wvbesl.c.BESLUITNR)
        .outerjoin(
            wvdos,
            and_(
                wvind_b.c.BESLUITNR  == wvdos.c.BESLUITNR,
                wvind_b.c.VOLGNR_IND == wvdos.c.VOLGNR_IND,
            )
        )
        .outerjoin(
            abc_refcod,
            and_(
                wvdos.c.KODE_REDEN_EINDE_VOORZ == abc_refcod.c.CODE,
                or_(
                    and_(
                        szregel.c.OMSCHRYVING == "JEUGDWET",
                        abc_refcod.c.DOMEIN     == "JZG_REDEN_EINDE_PRODUCT",
                    ),
                    and_(
                        szregel.c.OMSCHRYVING != "JEUGDWET",
                        abc_refcod.c.DOMEIN     == "WVRTEIND",
                    ),
                )
            )
        )
    )

queries = {
    'BESCHIKTE_VOORZIENING': BESCHIKTE_VOORZIENING,
    # ...
}
