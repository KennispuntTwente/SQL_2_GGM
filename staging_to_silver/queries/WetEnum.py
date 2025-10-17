from sqlalchemy import MetaData, select
from utils.database.naming import normalize_table_name, get_table_column, normalize_column_name


def build_szregel(engine, source_schema=None):
    table_names = [normalize_table_name("SZREGEL", kind="source")]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    (szregel,) = (metadata.tables[name] for name in fq_names)

    return (
        select(
            get_table_column(szregel, "KODE_REGELING").label(
                normalize_column_name("WET_ENUM_ID", kind="destination")
            ),
            get_table_column(szregel, "OMSCHRYVING").label(
                normalize_column_name("VALUE", kind="destination")
            ),
        )
    )


__query_exports__ = {
    "SZREGEL": build_szregel,
}
