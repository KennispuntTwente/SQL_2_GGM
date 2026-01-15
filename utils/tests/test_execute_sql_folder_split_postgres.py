# Tests for SQL statement splitting with Postgres dollar-quoted blocks
# Focuses on correctly parsing PL/pgSQL function bodies containing semicolons
# This ensures multi-statement SQL files with stored procedures are split correctly

from utils.database.execute_sql_folder import _split_sql_statements


def test_split_respects_postgres_dollar_quoted_blocks():
    sql = (
        """
        CREATE OR REPLACE FUNCTION public.add(a integer, b integer)
        RETURNS integer
        LANGUAGE plpgsql
        AS $$
        BEGIN
            -- inner semicolon should not split the function body
            RETURN a + b;
        END;
        $$;

        CREATE TABLE public.t1(id integer);
        """
    )

    parts = _split_sql_statements(sql, db_type="postgres")

    # Expect two top-level statements: function definition and create table
    assert len(parts) == 2
    assert parts[0].lstrip().upper().startswith("CREATE OR REPLACE FUNCTION")
    assert parts[1].lstrip().upper().startswith("CREATE TABLE")
