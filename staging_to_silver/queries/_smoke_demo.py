from sqlalchemy import Table, MetaData, select


def _demo_query(engine, source_schema: str = "staging"):
    """
    Very small synthetic query used only for Docker smoke tests.
    Reads from staging.demotable and selects columns as expected by silver.demo_silver.
    """
    md = MetaData()
    src = Table("demotable", md, schema=source_schema, autoload_with=engine)
    # Project columns matching silver.demo_silver: id, val
    return select(src.c.id.label("id"), src.c.val.label("val"))


__query_exports__ = {
    # Destination table key; loader will adhere to TABLE_NAME_CASE if configured
    "demo_silver": _demo_query,
}
