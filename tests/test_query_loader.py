import sys
import types
import pytest

from staging_to_silver.functions.query_loader import load_queries
from utils.database.naming import normalize_table_name


@pytest.fixture(autouse=True)
def clear_query_cache():
    # Ensure load_queries cache doesn't bleed between tests
    load_queries.cache_clear()
    yield
    load_queries.cache_clear()


def test_discovery_and_table_name_normalization():
    queries = load_queries(table_name_case="upper")
    # A few known exports from the package should be present and uppercased
    assert "BESCHIKTE_VOORZIENING" in queries
    assert "BESCHIKKING" in queries
    assert "CLIENT" in queries


def _install_fake_module(mod_name: str, exports: dict):
    mod = types.ModuleType(mod_name)
    mod.__query_exports__ = exports
    sys.modules[mod_name] = mod
    return mod


def test_column_name_case_wrapping_lower():
    # Create a fake builder that returns a SELECT with mixed-case labels
    from sqlalchemy import select, literal

    def fake_builder(engine, source_schema=None):
        return select(
            literal(1).label("ColOne"),
            literal(2).label("AnotherCol"),
        )

    mod_name = "_tmp_fake_queries_lower_case"
    _install_fake_module(mod_name, {"FAKE_TABLE": fake_builder})

    queries = load_queries(
        table_name_case="upper", column_name_case="lower", extra_modules=(mod_name,)
    )

    stmt = queries["FAKE_TABLE"](engine=None)
    labels = [c.name for c in stmt.selected_columns]
    assert labels == ["colone", "anothercol"]


def test_column_name_case_wrapping_upper():
    from sqlalchemy import select, literal

    def fake_builder(engine, source_schema=None):
        return select(
            literal(1).label("a"),
            literal(2).label("bB"),
        )

    mod_name = "_tmp_fake_queries_upper_case"
    _install_fake_module(mod_name, {"FAKE2": fake_builder})

    queries = load_queries(
        table_name_case="upper", column_name_case="upper", extra_modules=(mod_name,)
    )

    stmt = queries["FAKE2"](engine=None)
    labels = [c.name for c in stmt.selected_columns]
    assert labels == ["A", "BB"]


def test_duplicate_destination_detection():
    # Re-export an existing destination name to trigger duplicate error
    def fake_builder(engine, source_schema=None):
        from sqlalchemy import select, literal
        return select(literal(1).label("x"))

    mod_name = "_tmp_fake_queries_duplicate"
    _install_fake_module(mod_name, {"BESCHIKTE_VOORZIENING": fake_builder})

    with pytest.raises(ValueError):
        load_queries(extra_modules=(mod_name,))


def test_normalize_table_name_source_and_destination(monkeypatch):
    # Destination: use DESTINATION_TABLE_CASE preference
    monkeypatch.setenv("DESTINATION_TABLE_CASE", "lower")
    assert normalize_table_name("FOO", kind="destination") == "foo"
    # Legacy TABLE_NAME_CASE fallback when DESTINATION_TABLE_CASE not set
    monkeypatch.delenv("DESTINATION_TABLE_CASE", raising=False)
    monkeypatch.setenv("TABLE_NAME_CASE", "upper")
    assert normalize_table_name("bar", kind="destination") == "BAR"
    # Source uses SOURCE_TABLE_NAME_CASE
    monkeypatch.setenv("SOURCE_TABLE_NAME_CASE", "upper")
    assert normalize_table_name("wvbESl", kind="source") == "WVBESL"
