from sqlalchemy import MetaData, select


def build_szregel(engine, source_schema=None):
    table_names = ["szregel"]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [
        f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names
    ]
    (szregel,) = (metadata.tables[name] for name in fq_names)

    return select(
        szregel.c.kode_regeling.label("WET_ENUM_ID"),
        szregel.c.omschryving.label("VALUE"),
    )


__query_exports__ = {
    "SZREGEL": build_szregel,
}
