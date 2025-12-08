from sqlalchemy import literal, select
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col


def build_enum_gezinsrelatie(engine, source_schema=None):
    """Build the ENUM_GEZINSRELATIE select for Centric Burgerzaken (BRP).

    Source table: ods_cen_gba_tdomein (or gba_tdomein depending on staging naming).
    Filters on kveld = 'KIGS_GZR' and dwh_actueel = 1.
    """
    base_tables = ["ods_cen_gba_tdomein"]
    metadata = reflect_tables(engine, source_schema, base_tables)

    tdomein = get_table(
        metadata,
        source_schema,
        "ods_cen_gba_tdomein",
        required_cols=["kode", "oms", "kveld", "dwh_actueel"],
    )

    return (
        select(
            col(tdomein, "kode").label("ID"),
            col(tdomein, "oms").label("Waarde"),
        )
        .where(col(tdomein, "kveld") == literal("KIGS_GZR"))
        .where(col(tdomein, "dwh_actueel") == literal(1))
    )


__query_exports__ = {
    "ENUM_GEZINSRELATIE": build_enum_gezinsrelatie,
}
