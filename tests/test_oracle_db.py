# Tijdelijk script om Oracle database te initialiseren om te testen
# Maakt oracle sql server, met db ggm, met enkele tabellen

from sqlalchemy import (
    MetaData, Table, Column,
    Integer, String, Numeric, Date, ForeignKey
)
from sqlalchemy.sql import text
from ggm_dev_server.get_connection import get_connection

def setup_oracle():
    # 1) get a single connection (one container!)
    engine = get_connection(
        db_type="oracle",
        db_name="ggm",
        user="SA",                       # your schema
        password="SecureP@ss1!24323482349",
        force_refresh=True               # only call this ONCE
    )

    # 2) define metadata + all tables under schema=SA
    metadata = MetaData(schema="SA")
    Table(
        "SZCLIENT", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False)
    )
    Table(
        "SZORDER", metadata,
        Column("order_id", Integer, primary_key=True),
        Column("client_id", Integer, ForeignKey("SA.SZCLIENT.id"), nullable=False),
        Column("order_date", Date)
    )
    Table(
        "WVBEDRAG", metadata,
        Column("id", Integer, primary_key=True),
        Column("bedrag", Numeric(10,2))
    )
    Table(
        "WVAANB", metadata,
        Column("id", Integer, primary_key=True),
        Column("description", String(200))
    )

    # 3) create tables
    metadata.create_all(engine)

    # 4) insert sample data
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO SA.SZCLIENT (id, name) VALUES (1, 'Client A')"))
        conn.execute(text("INSERT INTO SA.SZCLIENT (id, name) VALUES (2, 'Client B')"))
        conn.execute(text("INSERT INTO SA.WVBEDRAG  (id, bedrag) VALUES (1, 100.00)"))
        conn.execute(text("INSERT INTO SA.WVBEDRAG  (id, bedrag) VALUES (2, 200.00)"))
        conn.execute(text("INSERT INTO SA.WVAANB   (id, description) VALUES (1, 'Description A')"))
        conn.execute(text("INSERT INTO SA.WVAANB   (id, description) VALUES (2, 'Description B')"))

    print("✓ Oracle ready with SZCLIENT, SZORDER, WVBEDRAG, WVAANB")
    return engine

con = setup_oracle()
