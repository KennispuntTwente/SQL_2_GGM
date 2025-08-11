# staging_to_silver/functions/queries.py
from sqlalchemy import MetaData, select, and_, or_, func, literal, case

def BESCHIKKING(engine, source_schema=None):
    table_names = ["WVBESL"]

    metadata = MetaData()
    metadata.reflect(bind=engine,
                     schema=source_schema,
                     only=table_names)

    # grab them (SQLAlchemy keys them as f"{schema}.{name}")
    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    wvbesl = (
        metadata.tables[name] for name in fq_names
    )

    return (
        select(
            wvbesl.c.BESLUITNR.label("BESCHIKKING_ID"),
            wvbesl.c.CLIENTNR.label("CLIENT_ID"),
            wvbesl.c.BESLUITNR.label("HEEFT_VOORZIENINGEN_BESCHIKTE_VOORZIENING_ID"),
            cast(literal(None), String(20)).label("CODE"),
            cast(literal(None), String(200)).label("COMMENTAAR"),
            cast(literal(None), Date).label("DATUMAFGIFTE"),
            cast(literal(None), Integer).label("GRONDSLAGEN"),
            cast(literal(None), String(255)).label("WET"),

          
        )
           
        .select_from(szwerker)
    )
            

queries = {
    'MEDEWERKER': MEDEWERKER
}
