# Tests for schema_qualifier cross-database schema qualification
# Focuses on MSSQL three-part naming (db.schema) vs Postgres/SQLite behavior
# This ensures correct schema prefixes are generated for different database backends

from staging_to_silver.functions.schema_qualifier import qualify_schema


def test_qualify_schema_mssql_three_part():
    assert qualify_schema("mssql", "DbX", "sch", default_schema="dbo") == "DbX.sch"
    # default schema when empty
    assert qualify_schema("mssql", "DbX", "", default_schema="dbo") == "DbX.dbo"


def test_qualify_schema_non_mssql():
    # Non-MSSQL ignores db and returns schema or None
    assert qualify_schema("postgresql", "db", "public") == "public"
    assert qualify_schema("postgresql", "db", "") is None
    assert qualify_schema("sqlite", None, None) is None
