from sqlalchemy import select
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col


def build_wet_enum(engine, source_schema=None):
    base_tables = ["szregel"]

    metadata = reflect_tables(engine, source_schema, base_tables)
    szregel = get_table(
        metadata,
        source_schema,
        "szregel",
        required_cols=["kode_regeling", "omschryving"],
    )

    return select(
        col(szregel, "kode_regeling").label("WET_ENUM_ID"),
        col(szregel, "omschryving").label("VALUE"),
    )


__query_exports__ = {
    "WET_ENUM": build_wet_enum,
}
