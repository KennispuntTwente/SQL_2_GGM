from sqlalchemy import MetaData, select, and_, cast, literal, String
from utils.database.naming import normalize_table_name, get_table_column, normalize_column_name


def build_declaratieregel(engine, source_schema=None):
    table_names = [
        normalize_table_name("SZUKHIS", kind="source"),
        normalize_table_name("WVDOS", kind="source"),
        normalize_table_name("WVIND_B", kind="source"),
    ]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    szukhis, wvdos, wvindb = (metadata.tables[name] for name in fq_names)

    # Joins:
    # 1) WVINDB ⋈ WVDOS op BESLUITNR en VOLGNR_IND
    join_wvindb_wvdos = wvindb.join(
        wvdos,
        and_(
            wvindb.c.BESLUITNR == wvdos.c.BESLUITNR,
            wvindb.c.VOLGNR_IND == wvdos.c.VOLGNR_IND,
        ),
        isouter=False  # inner join
    )

    # 2) WVDOS ⋈ SZUKHIS op SZUKHIS.UNIEKWVDOS == WVDOS.UNIEK
    full_join = join_wvindb_wvdos.join(
        szukhis,
        szukhis.c.UNIEKWVDOS == wvdos.c.UNIEK,
        isouter=False  # inner join
    )

    # Selectie (let op: IS_VOOR_BESCHIKKING_ID komt nu uit WVINDB)
    stmt = (
        select(
            get_table_column(szukhis, "BEDRAG").label(
                normalize_column_name("BEDRAG", kind="destination")
            ),
            get_table_column(wvindb, "BESLUITNR").label(
                normalize_column_name("IS_VOOR_BESCHIKKING_ID", kind="destination")
            ),
            get_table_column(wvindb, "CLIENTNR").label(
                normalize_column_name("BETREFT_CLIENT_ID", kind="destination")
            ),
            get_table_column(szukhis, "VERSLAGNR").label(
                normalize_column_name("VALT_BINNEN_DECLARATIE_ID", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("CODE", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("DATUMEINDE", kind="destination")
            ),
            cast(literal(None), String(80)).label(
                normalize_column_name("DATUMSTART", kind="destination")
            ),
        )
        .select_from(full_join)
    )

    return stmt

__query_exports__ = {
    "DECLARATIEREGEL": build_declaratieregel,
}
