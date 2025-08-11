from sqlalchemy import Table, Column, Integer, String, BigInteger, MetaData, text
from sqlalchemy.sql import insert
import re

def fill_engine_with_data(engine, schema):
    # ensure the schema exists
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", schema):
        raise ValueError(f"Unsafe schema name: {schema!r}")
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

    metadata = MetaData(schema=schema)

    wvind_b = Table(
        "wvind_b", metadata,
        Column("besluitnr", String),
        Column("volgnr_ind", String),
        Column("dd_eind", BigInteger),
        Column("dd_begin", BigInteger),
        Column("volume", Integer),
        Column("status_indicatie", String),
        Column("kode_regeling", String),
        Column("eenheid", String),
        Column("code_frequentie", String),
    )

    szregel = Table("szregel", metadata,
        Column("kode_regeling", String, primary_key=True),
        Column("omschryving", String),
    )
    wvbesl = Table("wvbesl", metadata, Column("besluitnr", String, primary_key=True))
    wvdos = Table("wvdos", metadata,
        Column("besluitnr", String),
        Column("volgnr_ind", String),
        Column("kode_reden_einde_voorz", String),
    )
    abc_refcod = Table("abc_refcod", metadata,
        Column("code", String, primary_key=True),
        Column("omschrijving", String),
        Column("domein", String),
    )

    metadata.create_all(engine)  # now works: schema exists

    with engine.begin() as conn:
        conn.execute(insert(wvind_b), [{
            "besluitnr": "B001",
            "volgnr_ind": "01",
            "dd_eind": 1704067200,
            "dd_begin": 1701475200,
            "volume": 10,
            "status_indicatie": "active",
            "kode_regeling": "KR1",
            "eenheid": "UUR",
            "code_frequentie": "DAILY",
        }])
        conn.execute(insert(szregel), [{"kode_regeling": "KR1", "omschryving": "JEUGDWET"}])
        conn.execute(insert(wvbesl), [{"besluitnr": "B001"}])
        conn.execute(insert(wvdos), [{"besluitnr": "B001", "volgnr_ind": "01", "kode_reden_einde_voorz": "RC1"}])
        conn.execute(insert(abc_refcod), [{"code": "RC1", "omschrijving": "Some reason", "domein": "JZG_REDEN_EINDE_PRODUCT"}])

    print(f"Dummy staging data inserted into schema '{schema}'.")
