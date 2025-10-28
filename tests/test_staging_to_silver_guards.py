from types import SimpleNamespace

import pytest

from staging_to_silver.functions.guards import (
    should_defer_constraints,
    validate_upsert_supported,
    filter_queries,
)


class DummyEngine:
    def __init__(self, dialect_name: str):
        self.dialect = SimpleNamespace(name=dialect_name)


def test_should_defer_constraints_only_postgres():
    assert should_defer_constraints(DummyEngine("postgresql")) is True
    assert should_defer_constraints(DummyEngine("sqlite")) is False
    assert should_defer_constraints(DummyEngine("mssql")) is False


def test_validate_upsert_supported_raises_on_non_pg():
    # Non-PostgreSQL backends should error clearly
    with pytest.raises(ValueError):
        validate_upsert_supported(DummyEngine("sqlite"))
    with pytest.raises(ValueError):
        validate_upsert_supported(DummyEngine("mssql"))

    # PostgreSQL backend should pass
    validate_upsert_supported(DummyEngine("postgresql"))


def test_filter_queries_allow_and_deny():
    called = []

    def q1(*args, **kwargs):
        called.append("A")

    def q2(*args, **kwargs):
        called.append("B")

    def q3(*args, **kwargs):
        called.append("C")

    queries = {"A": q1, "B": q2, "C": q3}

    # Allowlist keeps only the specified queries
    out = filter_queries(queries, allowlist={"A", "c"}, denylist=None)
    assert set(out.keys()) == {"A", "C"}

    # Denylist removes the specified queries
    out2 = filter_queries(queries, allowlist=None, denylist={"b"})
    assert set(out2.keys()) == {"A", "C"}
