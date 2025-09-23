# staging_to_silver/functions/queries.py
from sqlalchemy import MetaData, select, and_, or_, func, literal, case

def DECLARATIEREGEL(engine, source_schema=None):
    table_names = ["SZUKHIS"]

    metadata = MetaData()
    metadata.reflect(bind=engine,
                     schema=source_schema,
                     only=table_names)

    # grab them (SQLAlchemy keys them as f"{schema}.{name}")
    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    szukhis = (
        metadata.tables[name] for name in fq_names
    )

    return (
        select(
            szclient.c.CLIENTNR.label("RECHTSPERSOON_ID"),
            szclient.c.IND_GEZAG.label("GEZAGSDRAGERGEKEND_ENUM_ID"),
            cast(literal(None), String(80)).label("CODE"),
            cast(literal(None), String(80)).label("JURIDISCHESTATUS"),
            cast(literal(None), String(80)).label("WETTELIJKEVERTEGENWOORDIGING"),
       
        )
           
        .select_from(szclient)
    )
            

queries = {
    'CLIENT': CLIENT
}
