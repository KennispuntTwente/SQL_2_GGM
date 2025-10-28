from sqlalchemy import MetaData, Table, select

# Minimal test query builder for staging_to_silver integration on SQLite
# Expects a source table named 'src_people' in the same SQLite database
# and a destination table named 'PEOPLE' with columns ID, NAME.


def build_people(engine, source_schema=None):
    meta = MetaData()
    src = Table("src_people", meta, autoload_with=engine)
    # Labels must match destination column names and order
    return select(
        src.c.id.label("ID"),
        src.c.name.label("NAME"),
    )


__query_exports__ = {
    "PEOPLE": build_people,
}
