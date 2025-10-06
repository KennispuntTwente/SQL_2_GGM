from sqlalchemy import MetaData, select


def build_szregel(engine, source_schema=None):
    table_names = ["SZREGEL"]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    (szregel,) = (metadata.tables[name] for name in fq_names)

    return (
        select(
            szregel.c.KODE_REGELING.label("WET_ENUM_ID"),
            szregel.c.OMSCHRYVING.label("VALUE"),
        )
    )


__query_exports__ = {
    "SZREGEL": build_szregel,
}
