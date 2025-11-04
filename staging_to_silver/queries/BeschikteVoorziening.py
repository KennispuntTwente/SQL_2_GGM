from sqlalchemy import select, and_, or_, func, cast, Date, literal
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col


def _local_date_amsterdam(col, engine):
    """Cross-dialect conversion of a UTC timestamp to Europe/Amsterdam date.

    - PostgreSQL: use timezone('Europe/Amsterdam', timezone('UTC', ts)) then cast Date
    - MSSQL:       use ts AT TIME ZONE 'UTC' AT TIME ZONE 'W. Europe Standard Time' then cast Date
    - Fallback:    just cast to Date (no tz conversion) to keep query buildable on other dialects
    """
    dialect = (engine.dialect.name or "").lower()
    if dialect == "mssql":
        # Windows timezone ID for Europe/Amsterdam in SQL Server
        return cast(
            col.op("AT TIME ZONE")("UTC").op("AT TIME ZONE")("W. Europe Standard Time"),
            Date,
        )
    elif dialect.startswith("postgres"):
        return cast(func.timezone("Europe/Amsterdam", func.timezone("UTC", col)), Date)
    else:
        # For SQLite or other engines used in shape tests, avoid dialect-specific functions
        return cast(col, Date)


def build_beschikte_voorziening(engine, source_schema=None):
    base_tables = ["wvind_b", "szregel", "wvbesl", "wvdos", "abc_refcod"]

    metadata = reflect_tables(engine, source_schema, base_tables)
    wvind_b = get_table(metadata, source_schema, "wvind_b")
    szregel = get_table(metadata, source_schema, "szregel")
    wvbesl = get_table(metadata, source_schema, "wvbesl")
    wvdos = get_table(metadata, source_schema, "wvdos")
    abc_refcod = get_table(metadata, source_schema, "abc_refcod")

    return (
        select(
            # Timestamp zonder timezone (aanname is UTC-timezone; TODO: check of dit klopt) ->
            # UTC-timezone op zetten; dan omzetten naar Amsterdam-tijdzone ->
            # dan casten naar Date
            _local_date_amsterdam(col(wvind_b, "dd_eind"), engine).label("datumeinde"),
            _local_date_amsterdam(col(wvind_b, "dd_begin"), engine).label("datumstart"),
            # Alternatief:
            # cast(wvind_b.c.dd_eind.op("AT TIME ZONE")("UTC").op("AT TIME ZONE")("Europe/Amsterdam"), Date).label("datumeinde"),
            # cast(wvind_b.c.dd_begin.op("AT TIME ZONE")("UTC").op("AT TIME ZONE")("Europe/Amsterdam"), Date).label("datumstart"),
            # Of misschien:
            # cast(func.to_timestamp(wvind_b.c.dd_eind ).op("AT TIME ZONE")("Europe/Amsterdam"), Date).label("datumeinde"),
            # cast(func.to_timestamp(wvind_b.c.dd_begin).op("AT TIME ZONE")("Europe/Amsterdam"), Date).label("datumstart"),
            col(wvind_b, "volume").label("omvang"),
            col(wvind_b, "status_indicatie").label("status"),
            func.concat(col(wvind_b, "besluitnr"), col(wvind_b, "volgnr_ind")).label(
                "beschikte_voorziening_id"
            ),
            # 'redeneinde' lijkt date te zijn in target? (Is tekst in bron, wat logisch lijkt)
            # abc_refcod.c.omschrijving.label("redeneinde"),
            literal(None).label("redeneinde"),
            # Add missing columns as cast(null)
            literal(None).label("code"),
            literal(None).label("datumeindeoorspronkelijk"),
            literal(None).label("eenheid_enum_id"),
            literal(None).label("frequentie_enum_id"),
            literal(None).label("heeft_leveringsvorm_293_id"),
            literal(None).label("is_voorziening_voorziening_id"),
            literal(None).label("leveringsvorm_287_enum_id"),
            literal(None).label("toegewezen_product_toewijzing_id"),
            literal(None).label("wet_enum_id"),
        )
        .select_from(wvind_b)
        .outerjoin(
            szregel, col(wvind_b, "kode_regeling") == col(szregel, "kode_regeling")
        )
        .outerjoin(wvbesl, col(wvind_b, "besluitnr") == col(wvbesl, "besluitnr"))
        .outerjoin(
            wvdos,
            and_(
                col(wvind_b, "besluitnr") == col(wvdos, "besluitnr"),
                col(wvind_b, "volgnr_ind") == col(wvdos, "volgnr_ind"),
            ),
        )
        .outerjoin(
            abc_refcod,
            and_(
                col(wvdos, "kode_reden_einde_voorz") == col(abc_refcod, "code"),
                or_(
                    and_(
                        col(szregel, "omschryving") == "JEUGDWET",
                        col(abc_refcod, "domein") == "JZG_REDEN_EINDE_PRODUCT",
                    ),
                    and_(
                        col(szregel, "omschryving") != "JEUGDWET",
                        col(abc_refcod, "domein") == "WVRTEIND",
                    ),
                ),
            ),
        )
    )


# Map target table names to query builder functions
__query_exports__ = {
    "BESCHIKTE_VOORZIENING": build_beschikte_voorziening,
}
