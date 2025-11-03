from sqlalchemy import MetaData, select, and_, cast, literal, String


def build_declaratieregel(engine, source_schema=None):
    table_names = ["szukhis", "wvdos", "wvind_b"]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [
        f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names
    ]
    szukhis, wvdos, wvindb = (metadata.tables[name] for name in fq_names)

    # Joins:
    # 1) WVINDB ⋈ WVDOS op BESLUITNR en VOLGNR_IND
    join_wvindb_wvdos = wvindb.join(
        wvdos,
        and_(
            wvindb.c.besluitnr == wvdos.c.besluitnr,
            wvindb.c.volgnr_ind == wvdos.c.volgnr_ind,
        ),
        isouter=False,  # inner join
    )

    # 2) WVDOS ⋈ SZUKHIS op SZUKHIS.UNIEKWVDOS == WVDOS.UNIEK
    full_join = join_wvindb_wvdos.join(
        szukhis,
        szukhis.c.uniekwvdos == wvdos.c.uniek,
        isouter=False,  # inner join
    )

    # Selectie (let op: IS_VOOR_BESCHIKKING_ID komt nu uit WVINDB)
    stmt = select(
        szukhis.c.bedrag.label("BEDRAG"),
        wvindb.c.besluitnr.label("IS_VOOR_BESCHIKKING_ID"),
        wvindb.c.clientnr.label("BETREFT_CLIENT_ID"),
        szukhis.c.verslagnr.label("VALT_BINNEN_DECLARATIE_ID"),
        cast(literal(None), String(80)).label("CODE"),
        cast(literal(None), String(80)).label("DATUMEINDE"),
        cast(literal(None), String(80)).label("DATUMSTART"),
    ).select_from(full_join)

    return stmt


__query_exports__ = {
    "DECLARATIEREGEL": build_declaratieregel,
}
