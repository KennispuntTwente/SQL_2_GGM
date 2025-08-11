# staging_to_silver/functions/queries.py
from sqlalchemy import MetaData, select, and_, or_, func, text
from sqlalchemy import cast, null, Date, BIGINT

def BESCHIKTE_VOORZIENING(engine, source_schema=None):
    # table_names = ["WVIND_B","SZREGEL","WVBESL","WVDOS","ABC_REFCOD"]
    table_names = ["wvind_b", "szregel", "wvbesl", "wvdos", "abc_refcod"]

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
            # Convert BIGINT epoch to date
            cast(wvind_b.c.dd_eind, null()).label("datumeinde"),
            cast(wvind_b.c.dd_begin, null()).label("datumstart"),
            wvind_b.c.volume.label("omvang"),
            wvind_b.c.status_indicatie.label("status"),
            func.concat(
                wvind_b.c.besluitnr,
                wvind_b.c.volgnr_ind
            ).label("beschikte_voorziening_id"),
            abc_refcod.c.omschrijving.label("redeneinde"),

            # Add missing columns as cast(null)
            cast(null(), wvind_b.c.besluitnr.type).label("code"),
            cast(null(), wvind_b.c.dd_eind.type).label("datumeindeoorspronkelijk"),
            cast(null(), wvind_b.c.eenheid.type).label("eenheid_enum_id"),
            cast(null(), wvind_b.c.code_frequentie.type).label("frequentie_enum_id"),
            cast(null(), wvind_b.c.besluitnr.type).label("heeft_leveringsvorm_293_id"),
            cast(null(), wvind_b.c.besluitnr.type).label("is_voorziening_voorziening_id"),
            cast(null(), wvind_b.c.eenheid.type).label("leveringsvorm_287_enum_id"),
            cast(null(), wvind_b.c.besluitnr.type).label("toegewezen_product_toewijzing_id"),
            cast(null(), wvind_b.c.eenheid.type).label("wet_enum_id"),
        )
        .select_from(wvind_b)
        .outerjoin(szregel, wvind_b.c.kode_regeling == szregel.c.kode_regeling)
        .outerjoin(wvbesl,  wvind_b.c.besluitnr   == wvbesl.c.besluitnr)
        .outerjoin(
            wvdos,
            and_(
                wvind_b.c.besluitnr  == wvdos.c.besluitnr,
                wvind_b.c.volgnr_ind == wvdos.c.volgnr_ind,
            )
        )
        .outerjoin(
            abc_refcod,
            and_(
                wvdos.c.kode_reden_einde_voorz == abc_refcod.c.code,
                or_(
                    and_(
                        szregel.c.omschryving == "JEUGDWET",
                        abc_refcod.c.domein     == "JZG_REDEN_EINDE_PRODUCT",
                    ),
                    and_(
                        szregel.c.omschryving != "JEUGDWET",
                        abc_refcod.c.domein     == "WVRTEIND",
                    ),
                )
            )
        )
    )

queries = {
    'beschikte_voorziening': BESCHIKTE_VOORZIENING,
    # ...
}
