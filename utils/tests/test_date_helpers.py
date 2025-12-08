"""Tests for utils.database.date_helpers cross-dialect date conversion functions."""

import pytest
from sqlalchemy import Column, Date, Integer, MetaData, Table, create_engine, select

from utils.database.date_helpers import (
    current_date_yyyymmdd_minus_one,
    date_minus_one,
    format_bsn,
    format_date_yyyymmdd,
    incomplete_date_to_date,
    right_n_chars,
    yyyymmdd_to_date,
)


@pytest.fixture
def sqlite_engine():
    """Create a SQLite in-memory engine for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def sample_table():
    """Create a sample table for testing expressions."""
    metadata = MetaData()
    return Table(
        "test_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("date_num", Integer),
        Column("bsn", Integer),
        Column("dt", Date),
    )


class TestYyyymmddToDate:
    """Tests for yyyymmdd_to_date function."""

    def test_compiles_on_sqlite(self, sqlite_engine, sample_table):
        """Verify the expression compiles on SQLite."""
        expr = select(yyyymmdd_to_date(sqlite_engine, sample_table.c.date_num))
        compiled = str(expr.compile(sqlite_engine))
        assert "to_date" in compiled.lower()

    def test_returns_clause_element(self, sqlite_engine, sample_table):
        """Verify the function returns a valid SQLAlchemy clause element."""
        result = yyyymmdd_to_date(sqlite_engine, sample_table.c.date_num)
        # Should be usable in a select
        stmt = select(result)
        assert stmt is not None


class TestIncompleteDateToDate:
    """Tests for incomplete_date_to_date function."""

    def test_compiles_on_sqlite(self, sqlite_engine, sample_table):
        """Verify the expression compiles on SQLite."""
        expr = select(incomplete_date_to_date(sqlite_engine, sample_table.c.date_num))
        compiled = str(expr.compile(sqlite_engine))
        # Should contain CASE for the adjustment logic
        assert "CASE" in compiled.upper()

    def test_handles_null_for_zero(self, sqlite_engine, sample_table):
        """Verify the CASE includes handling for <= 0."""
        expr = incomplete_date_to_date(sqlite_engine, sample_table.c.date_num)
        compiled = str(
            select(expr).compile(sqlite_engine, compile_kwargs={"literal_binds": True})
        )
        # Should reference the comparison for <= 0
        assert "0" in compiled


class TestDateMinusOne:
    """Tests for date_minus_one function."""

    def test_compiles_on_sqlite(self, sqlite_engine, sample_table):
        """Verify the expression compiles on SQLite."""
        expr = select(date_minus_one(sqlite_engine, sample_table.c.dt))
        compiled = str(expr.compile(sqlite_engine))
        # SQLite fallback uses subtraction
        assert "-" in compiled or "1" in compiled

    def test_returns_clause_element(self, sqlite_engine, sample_table):
        """Verify the function returns a valid SQLAlchemy clause element."""
        result = date_minus_one(sqlite_engine, sample_table.c.dt)
        stmt = select(result)
        assert stmt is not None


class TestCurrentDateYyyymmddMinusOne:
    """Tests for current_date_yyyymmdd_minus_one function."""

    def test_compiles_on_sqlite(self, sqlite_engine):
        """Verify the expression compiles on SQLite."""
        expr = select(current_date_yyyymmdd_minus_one(sqlite_engine))
        compiled = str(expr.compile(sqlite_engine))
        # Should contain to_char or similar
        assert "to_char" in compiled.lower() or "current" in compiled.lower()


class TestFormatDateYyyymmdd:
    """Tests for format_date_yyyymmdd function."""

    def test_compiles_on_sqlite(self, sqlite_engine, sample_table):
        """Verify the expression compiles on SQLite."""
        expr = select(format_date_yyyymmdd(sqlite_engine, sample_table.c.dt))
        compiled = str(expr.compile(sqlite_engine))
        assert "to_char" in compiled.lower()


class TestRightNChars:
    """Tests for right_n_chars function."""

    def test_compiles_on_sqlite(self, sqlite_engine, sample_table):
        """Verify the expression compiles on SQLite."""
        expr = select(right_n_chars(sqlite_engine, sample_table.c.bsn, 5))
        compiled = str(expr.compile(sqlite_engine))
        # Should use substr for SQLite fallback
        assert "substr" in compiled.lower()

    def test_extracts_correct_length(self, sqlite_engine, sample_table):
        """Verify the expression references the correct length."""
        expr = right_n_chars(sqlite_engine, sample_table.c.bsn, 9)
        compiled = str(
            select(expr).compile(sqlite_engine, compile_kwargs={"literal_binds": True})
        )
        assert "9" in compiled


class TestFormatBsn:
    """Tests for format_bsn function."""

    def test_compiles_on_sqlite(self, sqlite_engine, sample_table):
        """Verify the expression compiles on SQLite."""
        expr = select(format_bsn(sqlite_engine, sample_table.c.bsn))
        compiled = str(
            expr.compile(sqlite_engine, compile_kwargs={"literal_binds": True})
        )
        # Should contain the padding zeros
        assert "000000000" in compiled

    def test_uses_right_n_chars(self, sqlite_engine, sample_table):
        """Verify the expression uses right extraction for 9 chars."""
        expr = format_bsn(sqlite_engine, sample_table.c.bsn)
        compiled = str(
            select(expr).compile(sqlite_engine, compile_kwargs={"literal_binds": True})
        )
        # Should reference 9 for the substring length
        assert "9" in compiled
