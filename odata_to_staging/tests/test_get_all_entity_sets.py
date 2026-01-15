# Tests for get_all_entity_sets helper function
# Ensures entity set discovery from OData schema works correctly

import pytest
from types import SimpleNamespace

from odata_to_staging.functions.get_all_entity_sets import get_all_entity_sets


class _EntitySet:
    """Mock EntitySet with a name attribute."""

    def __init__(self, name: str):
        self.name = name


def test_get_all_entity_sets_multiple():
    """Should return all entity set names from client schema."""
    entity_sets = [
        _EntitySet("Employees"),
        _EntitySet("Orders"),
        _EntitySet("Products"),
    ]
    schema = SimpleNamespace(entity_sets=entity_sets)
    client = SimpleNamespace(schema=schema)

    result = get_all_entity_sets(client)

    assert result == ["Employees", "Orders", "Products"]


def test_get_all_entity_sets_empty_schema():
    """Should return empty list when no entity sets in schema."""
    schema = SimpleNamespace(entity_sets=[])
    client = SimpleNamespace(schema=schema)

    result = get_all_entity_sets(client)

    assert result == []


def test_get_all_entity_sets_single():
    """Should handle single entity set correctly."""
    entity_sets = [_EntitySet("Categories")]
    schema = SimpleNamespace(entity_sets=entity_sets)
    client = SimpleNamespace(schema=schema)

    result = get_all_entity_sets(client)

    assert result == ["Categories"]


def test_get_all_entity_sets_preserves_order():
    """Entity sets should be returned in schema order."""
    entity_sets = [
        _EntitySet("Zebras"),
        _EntitySet("Apples"),
        _EntitySet("Bananas"),
    ]
    schema = SimpleNamespace(entity_sets=entity_sets)
    client = SimpleNamespace(schema=schema)

    result = get_all_entity_sets(client)

    assert result == ["Zebras", "Apples", "Bananas"]


def test_get_all_entity_sets_missing_schema_raises():
    """Should raise RuntimeError when schema is not accessible."""
    client = SimpleNamespace()  # No schema attribute

    with pytest.raises(RuntimeError, match="schema.entity_sets"):
        get_all_entity_sets(client)


def test_get_all_entity_sets_missing_entity_sets_raises():
    """Should raise RuntimeError when entity_sets is not accessible."""
    schema = SimpleNamespace()  # No entity_sets attribute
    client = SimpleNamespace(schema=schema)

    with pytest.raises(RuntimeError, match="schema.entity_sets"):
        get_all_entity_sets(client)
