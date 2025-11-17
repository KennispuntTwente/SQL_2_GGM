from sqlalchemy import select, and_, cast, literal, String, Date
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col


def build_declaratieregel(engine, source_schema=None):
    base_tables = ["szukhis", "wvdos", "wvind_b"]

    metadata = reflect_tables(engine, source_schema, base_tables)
    szukhis = get_table(
        metadata,
        source_schema,
        "szukhis",
        required_cols=["uniekwvdos", "bedrag", "verslagnr"],
    )
    wvdos = get_table(
        metadata,
        source_schema,
        "wvdos",
        required_cols=["besluitnr", "volgnr_ind", "uniek"],
    )
    wvindb = get_table(
        metadata,
        source_schema,
        "wvind_b",
        required_cols=["besluitnr", "volgnr_ind", "clientnr"],
    )

    # Joins:
    # 1) WVINDB ⋈ WVDOS op BESLUITNR en VOLGNR_IND
    join_wvindb_wvdos = wvindb.join(
        wvdos,
        and_(
            col(wvindb, "besluitnr") == col(wvdos, "besluitnr"),
            col(wvindb, "volgnr_ind") == col(wvdos, "volgnr_ind"),
        ),
        isouter=False,  # inner join
    )

    # 2) WVDOS ⋈ SZUKHIS op SZUKHIS.UNIEKWVDOS == WVDOS.UNIEK
    full_join = join_wvindb_wvdos.join(
        szukhis,
        col(szukhis, "uniekwvdos") == col(wvdos, "uniek"),
        isouter=False,  # inner join
    )

    # Selectie conform DDL volgorde:
    # DECLARATIEREGEL_ID, BEDRAG, BETREFT_CLIENT_ID, CODE, DATUMEINDE, DATUMSTART, IS_VOOR_BESCHIKKING_ID, VALT_BINNEN_DECLARATIE_ID
    # Deterministic primary key: reuse WVDOS.UNIEK (unique per besluitnr+volgnr_ind)
    stmt = select(
        col(wvdos, "uniek").label("DECLARATIEREGEL_ID"),
        col(szukhis, "bedrag").label("BEDRAG"),
        col(wvindb, "clientnr").label("BETREFT_CLIENT_ID"),
        cast(literal(None), String(80)).label("CODE"),
        cast(literal(None), Date).label("DATUMEINDE"),
        cast(literal(None), Date).label("DATUMSTART"),
        col(wvindb, "besluitnr").label("IS_VOOR_BESCHIKKING_ID"),
        col(szukhis, "verslagnr").label("VALT_BINNEN_DECLARATIE_ID"),
    ).select_from(full_join)

    return stmt


__query_exports__ = {
    "DECLARATIEREGEL": build_declaratieregel,
}
