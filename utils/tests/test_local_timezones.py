from sqlalchemy import Column, DateTime, Integer, MetaData, Table, create_engine, select

from utils.database.local_timezones import local_date_amsterdam


def test_local_date_amsterdam_sqlite_compiles_to_cast():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    t = Table(
        "events",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("ts", DateTime(timezone=False)),
    )

    expr = select(local_date_amsterdam(t.c.ts, engine))
    compiled = expr.compile(engine)

    assert "CAST" in str(compiled)
