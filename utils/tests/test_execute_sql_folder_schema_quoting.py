# Tests for schema placeholder quoting in execute_sql_folder
# Focuses on verifying {schema} substitution produces correctly quoted identifiers per dialect
# This ensures SQL templates with schema placeholders work across Postgres and MSSQL

from pathlib import Path
from typing import List, cast

from sqlalchemy.dialects.postgresql import dialect as pgDialect
from sqlalchemy.dialects.mssql import dialect as msDialect

from utils.database.execute_sql_folder import execute_sql_folder
from utils.database.identifiers import quote_ident, mssql_bracket_escape
from sqlalchemy.engine import Engine


class DummyCursor:
    def __init__(self, dialect_name: str):
        self.dialect_name = dialect_name
        self.statements: List[str] = []
        self._user_queried = False

    def execute(self, sql: str):  # type: ignore[override]
        # Record SQL; behave specially for CURRENT_USER to simulate return value
        self.statements.append(sql)

    def fetchone(self):
        # Simulate CURRENT_USER response for MSSQL path
        if not self._user_queried:
            self._user_queried = True
            return ("testuser",)
        return None


class DummyRawConnection:
    def __init__(self, cursor: DummyCursor):
        self._cursor = cursor
        self._closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        self._closed = True


class DummyEngine:
    def __init__(self, dialect):
        self.dialect = dialect
        self._raw = DummyRawConnection(DummyCursor(dialect.name))

    def raw_connection(self):
        return self._raw

    # begin() is unused in execute_sql_folder path we test; provide stub if future changes require
    def begin(self):  # pragma: no cover - not used here
        raise NotImplementedError


def _make_sql_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "sql"
    folder.mkdir()
    (folder / "001_init.sql").write_text("SELECT 1;", encoding="utf-8")
    return folder


def test_postgres_schema_quoting(tmp_path):
    schema = 'bad"name'  # contains a quote to ensure escaping
    engine = DummyEngine(pgDialect())
    sql_folder = _make_sql_folder(tmp_path)

    execute_sql_folder(
        cast(Engine, engine),
        sql_folder=str(sql_folder),
        suffix_filter=False,
        schema=schema,
    )  # type: ignore[arg-type]

    # First statement should be CREATE SCHEMA IF NOT EXISTS with properly quoted identifier
    expected = (
        f"CREATE SCHEMA IF NOT EXISTS {quote_ident(cast(Engine, engine), schema)}"  # type: ignore[arg-type]
    )
    cur = engine._raw.cursor()
    assert expected in cur.statements[0]
    # search_path statement should use the same quoted identifier without additional raw schema text
    assert (
        cur.statements[1]
        == f"SET search_path TO {quote_ident(cast(Engine, engine), schema)}, public"
    )  # type: ignore[arg-type]


def test_mssql_schema_quoting(tmp_path):
    schema = "bad]name"  # contains a bracket to ensure escaping
    engine = DummyEngine(msDialect())
    sql_folder = _make_sql_folder(tmp_path)

    execute_sql_folder(
        cast(Engine, engine),
        sql_folder=str(sql_folder),
        suffix_filter=False,
        schema=schema,
    )  # type: ignore[arg-type]

    cur = engine._raw.cursor()
    # Look for properly escaped dynamic creation statement
    escaped_bracket = mssql_bracket_escape(schema)
    escaped_literal = schema.replace("'", "''")
    # Statement 0: IF SCHEMA_ID ... CREATE SCHEMA
    assert (
        f"IF SCHEMA_ID(N'{escaped_literal}') IS NULL EXEC('CREATE SCHEMA [{escaped_bracket}]')"
        in cur.statements[0]
    )
    # Statement 2 (after SELECT CURRENT_USER) should ALTER USER with bracket escaped schema
    assert any(
        f"ALTER USER [testuser] WITH DEFAULT_SCHEMA=[{escaped_bracket}]" in s
        for s in cur.statements
    ), cur.statements
