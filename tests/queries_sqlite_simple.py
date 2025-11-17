from sqlalchemy import MetaData, Table, select


def _people_query(engine, source_schema):
    """Simple mapping from src_people to PEOPLE for SQLite e2e test."""
    meta = MetaData()
    src_people = Table("src_people", meta, autoload_with=engine)
    return select(
        src_people.c.id.label("ID"),
        src_people.c.name.label("NAME"),
    )


__query_exports__ = {
    "PEOPLE": _people_query,
}
