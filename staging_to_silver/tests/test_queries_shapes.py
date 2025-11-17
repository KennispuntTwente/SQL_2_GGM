# Tests for query shapes in staging_to_silver module using SQLite in-memory database
# Focuses on verifying selected column names and order for key queries
# This ensures that the query definitions match expected schema shapes

import pytest
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime
from dotenv import load_dotenv

from staging_to_silver.functions.query_loader import load_queries


load_dotenv("tests/.env")


@pytest.fixture
def sqlite_engine():
    # In-memory SQLite engine for lightweight shape checks
    engine = create_engine("sqlite+pysqlite:///:memory:")
    yield engine
    engine.dispose()


def _create_table(engine, name, cols, schema=None):
    md = MetaData()
    Table(name, md, *cols)
    md.create_all(engine)


def test_beschikking_shape(sqlite_engine):
    # Create only the table(s) needed for reflection
    _create_table(
        sqlite_engine,
        "wvbesl",
        [
            Column("besluitnr", String),
            Column("clientnr", String),
        ],
    )

    queries = load_queries(table_name_case="upper", column_name_case="upper")
    stmt = queries["BESCHIKKING"](sqlite_engine, source_schema=None)
    labels = [c.name for c in stmt.selected_columns]
    assert labels == [
        "BESCHIKKING_ID",
        "CLIENT_ID",
        "HEEFT_VOORZIENINGEN_BESCHIKTE_VOORZIENING_ID",
        "CODE",
        "COMMENTAAR",
        "DATUMAFGIFTE",
        "GRONDSLAGEN",
        "WET",
    ]


def test_client_shape(sqlite_engine):
    _create_table(
        sqlite_engine,
        "szclient",
        [
            Column("clientnr", String),
            Column("ind_gezag", String),
        ],
    )

    queries = load_queries(table_name_case="upper", column_name_case="upper")
    stmt = queries["CLIENT"](sqlite_engine, source_schema=None)
    labels = [c.name for c in stmt.selected_columns]
    assert labels[:2] == ["RECHTSPERSOON_ID", "GEZAGSDRAGERGEKEND_ENUM_ID"]
    # Ensure we select at least 5 columns as defined
    assert len(labels) >= 5


def test_medewerker_shape(sqlite_engine):
    _create_table(
        sqlite_engine,
        "szwerker",
        [
            Column("kode_werker", String),
            Column("naam", String),
            Column("kode_instan", String),
            Column("e_mail", String),
            Column("ind_geslacht", String),
            Column("toelichting", String),
            Column("telefoon", String),
        ],
    )

    queries = load_queries(table_name_case="upper", column_name_case="upper")
    stmt = queries["MEDEWERKER"](sqlite_engine, source_schema=None)
    labels = [c.name for c in stmt.selected_columns]
    assert labels[:7] == [
        "MEDEWERKER_ID",
        "ACHTERNAAM",
        "FUNCTIE",
        "EMAILADRES",
        "GESLACHTSAANDUIDING",
        "MEDEWERKERTOELICHTING",
        "TELEFOONNUMMER",
    ]


def test_beschikte_voorziening_shape(sqlite_engine):
    # This query references several tables; create minimal structure
    _create_table(
        sqlite_engine,
        "wvind_b",
        [
            Column("dd_eind", DateTime),
            Column("dd_begin", DateTime),
            Column("volume", Integer),
            Column("status_indicatie", String),
            Column("besluitnr", String),
            Column("volgnr_ind", String),
            Column("kode_regeling", String),
            Column("clientnr", String),
        ],
    )
    _create_table(
        sqlite_engine,
        "szregel",
        [
            Column("kode_regeling", String),
            Column("omschryving", String),
        ],
    )
    _create_table(
        sqlite_engine,
        "wvbesl",
        [
            Column("besluitnr", String),
        ],
    )
    _create_table(
        sqlite_engine,
        "wvdos",
        [
            Column("besluitnr", String),
            Column("volgnr_ind", String),
            Column("kode_reden_einde_voorz", String),
        ],
    )
    _create_table(
        sqlite_engine,
        "abc_refcod",
        [
            Column("code", String),
            Column("omschrijving", String),
            Column("domein", String),
        ],
    )

    queries = load_queries(table_name_case="upper", column_name_case="lower")
    stmt = queries["BESCHIKTE_VOORZIENING"](sqlite_engine, source_schema=None)
    labels = [c.name for c in stmt.selected_columns]

    # Column names are coerced to lower by the wrapper
    expected = {
        "datumeinde",
        "datumstart",
        "omvang",
        "status",
        "beschikte_voorziening_id",
        "redeneinde",
        "code",
        "datumeindeoorspronkelijk",
        "eenheid_enum_id",
        "frequentie_enum_id",
        "heeft_leveringsvorm_293_id",
        "is_voorziening_voorziening_id",
        "leveringsvorm_287_enum_id",
        "toegewezen_product_toewijzing_id",
        "wet_enum_id",
    }
    assert set(labels) == expected
