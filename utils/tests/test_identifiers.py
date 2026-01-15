# Tests for SQL identifier quoting helpers across different database dialects
# Focuses on quote_ident, quote_fqn, and quote_truncate_target for Postgres and MSSQL
# This ensures correct identifier escaping for reserved words, special characters, and cross-database references

from sqlalchemy.dialects import postgresql, mssql

from utils.database.identifiers import (
    quote_ident,
    quote_fqn,
    quote_truncate_target,
    mssql_bracket_escape,
)


def test_quote_ident_postgresql_basic():
    d = postgresql.dialect()
    assert quote_ident(d, "MixedCase") == '"MixedCase"'
    assert quote_ident(d, "weird name") == '"weird name"'
    # reserved word
    assert quote_ident(d, "select") == '"select"'


def test_quote_ident_mssql_basic():
    d = mssql.dialect()
    assert quote_ident(d, "MyTable") == "[MyTable]"
    assert quote_ident(d, "has space") == "[has space]"
    assert quote_ident(d, "select") == "[select]"


def test_quote_fqn_skips_none_parts():
    d = postgresql.dialect()
    # schema is simple and not reserved -> may be unquoted; table is a reserved word -> quoted
    assert quote_fqn(d, [None, "schema", "table"]) == 'schema."table"'
    # no part requires quoting -> remains unquoted
    assert quote_fqn(d, ["db", None, "t"]) == 'db.t'


def test_quote_truncate_target_mssql_crossdb():
    d = mssql.dialect()
    got = quote_truncate_target(d, db="Db1", schema="dbo", table="T")
    # SQLAlchemy may omit brackets for simple identifiers like dbo
    assert got in ("[Db1].[dbo].[T]", "[Db1].dbo.[T]")


def test_quote_truncate_target_postgresql_ignores_db():
    d = postgresql.dialect()
    got = quote_truncate_target(d, db="Db1", schema="public", table="T")
    assert got in ('"public"."T"', 'public."T"')


def test_mssql_bracket_escape():
    assert mssql_bracket_escape("a]b") == "a]]b"
    assert mssql_bracket_escape("plain") == "plain"
