from sqlalchemy import Table, Column, Integer, String, BigInteger, MetaData, text, Date, DateTime
from sqlalchemy.sql import insert
import re
from datetime import date, datetime, timezone

def fill_engine_with_data(engine, schema, date_mode="epoch"):
    """
    date_mode:
      - "epoch"        -> dd_begin/dd_eind are BigInteger epoch seconds
      - "epoch_ms"     -> dd_begin/dd_eind are BigInteger epoch milliseconds
      - "regular"      -> dd_begin/dd_eind are DATEs
      - "epoch_us"     -> dd_begin/dd_eind are BigInteger epoch microseconds
      - "epoch_days"   -> dd_begin/dd_eind are Integer days since 1970-01-01
      - "yyyymmdd_int" -> dd_begin/dd_eind are Integer like 20240101
      - "timestamp"    -> dd_begin/dd_eind are TIMESTAMP (no timezone)
      - "timestamp_tz" -> dd_begin/dd_eind are TIMESTAMP WITH TIME ZONE
      - "date_str"     -> dd_begin/dd_eind are 'YYYY-MM-DD' strings
      - "iso_str"      -> dd_begin/dd_eind are ISO-8601 strings '...T...Z'
    """
    allowed = {
        "epoch", "epoch_ms", "regular",
        "epoch_us", "epoch_days", "yyyymmdd_int",
        "timestamp", "timestamp_tz", "date_str", "iso_str",
    }
    if date_mode not in allowed:
        raise ValueError(f"date_mode must be one of: {sorted(allowed)}")

    # ensure the schema exists (simple validation)
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", schema):
        raise ValueError(f"Unsafe schema name: {schema!r}")
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

    metadata = MetaData(schema=schema)

    # pick column type based on mode
    if date_mode in {"epoch", "epoch_ms", "epoch_us"}:
        dd_type = BigInteger
    elif date_mode in {"epoch_days", "yyyymmdd_int"}:
        dd_type = Integer
    elif date_mode == "regular":
        dd_type = Date
    elif date_mode == "timestamp":
        dd_type = DateTime(timezone=False)
    elif date_mode == "timestamp_tz":
        dd_type = DateTime(timezone=True)
    elif date_mode in {"date_str", "iso_str"}:
        dd_type = String
    else:
        raise AssertionError("unreachable")

    wvind_b = Table(
        "wvind_b",
        metadata,
        Column("besluitnr", String),
        Column("volgnr_ind", String),
        Column("dd_eind", dd_type),
        Column("dd_begin", dd_type),
        Column("volume", Integer),
        Column("status_indicatie", String),
        Column("kode_regeling", String),
        Column("eenheid", String),
        Column("code_frequentie", String),
    )

    szregel = Table(
        "szregel",
        metadata,
        Column("kode_regeling", String, primary_key=True),
        Column("omschryving", String),
    )
    wvbesl = Table("wvbesl", metadata, Column("besluitnr", String, primary_key=True))
    wvdos = Table(
        "wvdos",
        metadata,
        Column("besluitnr", String),
        Column("volgnr_ind", String),
        Column("kode_reden_einde_voorz", String),
    )
    abc_refcod = Table(
        "abc_refcod",
        metadata,
        Column("code", String, primary_key=True),
        Column("omschrijving", String),
        Column("domein", String),
    )

    metadata.create_all(engine)

    # canonical points in time for the examples
    d_begin = date(2023, 12, 2)
    d_end   = date(2024, 1, 1)
    dt_begin_utc = datetime(2023, 12, 2, 0, 0, 0, tzinfo=timezone.utc)
    dt_end_utc   = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # pick row values based on mode
    if date_mode == "epoch":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind": 1704067200,   # 2024-01-01 UTC (seconds)
            "dd_begin": 1701475200,  # 2023-12-02 UTC (seconds)
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "epoch_ms":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind": 1704067200 * 1000,   # ms
            "dd_begin": 1701475200 * 1000,  # ms
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "regular":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind": d_end,
            "dd_begin": d_begin,
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "epoch_us":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind": 1704067200 * 1_000_000,   # μs
            "dd_begin": 1701475200 * 1_000_000,  # μs
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "epoch_days":
        # days since 1970-01-01
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind":  (d_end - date(1970, 1, 1)).days,   # 19723
            "dd_begin": (d_begin - date(1970, 1, 1)).days, # 19693
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "yyyymmdd_int":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind":  20240101,
            "dd_begin": 20231202,
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "timestamp":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind":   datetime(2024, 1, 1, 0, 0, 0),
            "dd_begin":  datetime(2023, 12, 2, 0, 0, 0),
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "timestamp_tz":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind":  dt_end_utc,    # 2024-01-01T00:00:00+00:00
            "dd_begin": dt_begin_utc,  # 2023-12-02T00:00:00+00:00
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "date_str":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind":  "2024-01-01",
            "dd_begin": "2023-12-02",
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    elif date_mode == "iso_str":
        row_wvind_b = {
            "besluitnr": "B001", "volgnr_ind": "01",
            "dd_eind":  "2024-01-01T00:00:00Z",
            "dd_begin": "2023-12-02T00:00:00Z",
            "volume": 10, "status_indicatie": "active",
            "kode_regeling": "KR1", "eenheid": "UUR", "code_frequentie": "DAILY",
        }
    else:
        raise AssertionError("unreachable")

    with engine.begin() as conn:
        conn.execute(insert(wvind_b), [row_wvind_b])
        conn.execute(insert(szregel), [{"kode_regeling": "KR1", "omschryving": "JEUGDWET"}])
        conn.execute(insert(wvbesl), [{"besluitnr": "B001"}])
        conn.execute(
            insert(wvdos),
            [{"besluitnr": "B001", "volgnr_ind": "01", "kode_reden_einde_voorz": "RC1"}],
        )
        conn.execute(
            insert(abc_refcod),
            [{"code": "RC1", "omschrijving": "Some reason", "domein": "JZG_REDEN_EINDE_PRODUCT"}],
        )

    print(f"Dummy staging data inserted into schema '{schema}' with date_mode='{date_mode}'.")
