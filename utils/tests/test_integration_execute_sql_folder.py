from pathlib import Path

import pytest
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection
from utils.database.execute_sql_folder import execute_sql_folder, drop_schema_objects
from tests.integration_utils import (
    docker_running,
    slow_tests_enabled,
    cleanup_db_container_by_port,
    cleanup_db_containers,
)


def _mssql_driver_available() -> bool:
    try:
        import pyodbc  # noqa

        return any("ODBC Driver 18 for SQL Server" in d for d in pyodbc.drivers())
    except Exception:
        return False


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.postgres
def test_execute_sql_and_delete_schema_postgres(tmp_path: Path):
    # Start a clean Postgres
    engine = get_connection(
        db_type="postgres",
        db_name="ggm_exec_folder",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=5433,
        force_refresh=True,
        print_tables=False,
    )

    try:
        sql_dir = tmp_path / "sql"
        sql_dir.mkdir()

        # Generic file and Postgres-specific file; with suffix_filter=True, only *_postgres.sql runs
        (sql_dir / "01_generic.sql").write_text(
            "CREATE TABLE ignore_me(id INT);", encoding="utf-8"
        )
        (sql_dir / "02_make_table_postgres.sql").write_text(
            """
            CREATE TABLE foo_pg(id INT PRIMARY KEY);
            INSERT INTO foo_pg(id) VALUES (42);
            """,
            encoding="utf-8",
        )

        # Execute into schema 'silver' (created if missing); verify table exists and is populated
        execute_sql_folder(engine, sql_dir, suffix_filter=True, schema="silver")

        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM silver.foo_pg")
            ).scalar_one()
            assert count == 1
            # ensure generic file did not run
            exists = conn.execute(
                text(
                    """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema='silver' AND table_name='ignore_me'
                """
                )
            ).scalar_one()
            assert exists == 0

        # Now delete schema contents and ensure table is gone
        drop_schema_objects(engine, schema="silver")

        with engine.connect() as conn:
            exists = conn.execute(
                text(
                    """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema='silver' AND table_name='foo_pg'
                """
                )
            ).scalar_one()
            assert exists == 0
    finally:
        cleanup_db_container_by_port("postgres", 5433)


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not _mssql_driver_available(),
    reason="ODBC Driver 18 for SQL Server not installed; required for MSSQL test.",
)
@pytest.mark.mssql
def test_execute_sql_and_delete_schema_mssql(tmp_path: Path):
    # Start a clean MSSQL
    engine = get_connection(
        db_type="mssql",
        db_name="ggm_exec_folder",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=1434,
        force_refresh=True,
        print_tables=False,
    )

    try:
        sql_dir = tmp_path / "sql"
        sql_dir.mkdir()

        # Only *_mssql.sql should run with suffix filter; create in dbo to avoid ALTER USER/default schema issues
        (sql_dir / "01_make_table_mssql.sql").write_text(
            """
            IF OBJECT_ID(N'dbo.foo_ms', N'U') IS NOT NULL DROP TABLE dbo.foo_ms;
            CREATE TABLE dbo.foo_ms(id INT PRIMARY KEY);
            INSERT INTO dbo.foo_ms(id) VALUES (7);
            """,
            encoding="utf-8",
        )

        execute_sql_folder(engine, sql_dir, suffix_filter=True, schema=None)

        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM dbo.foo_ms")).scalar_one()
            assert count == 1

        # Drop all objects in dbo (reflection-based)
        drop_schema_objects(engine, schema="dbo")

        with engine.connect() as conn:
            exists = conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='dbo' AND table_name='foo_ms'"
                )
            ).scalar_one()
            assert exists == 0
    finally:
        cleanup_db_containers("mssql")


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.mariadb
def test_execute_sql_and_delete_schema_mariadb(tmp_path: Path):
    db_name = "ggm_exec_folder_mb"
    engine = get_connection(
        db_type="mariadb",
        db_name=db_name,
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=3309,
        force_refresh=True,
        print_tables=False,
    )

    try:
        sql_dir = tmp_path / "sql"
        sql_dir.mkdir()

        # Use MySQL suffix for MariaDB (driver dialect is mysql)
        (sql_dir / "01_make_table_mysql.sql").write_text(
            """
            DROP TABLE IF EXISTS foo_mb;
            CREATE TABLE foo_mb(id INT PRIMARY KEY);
            INSERT INTO foo_mb(id) VALUES (5);
            """,
            encoding="utf-8",
        )

        execute_sql_folder(engine, sql_dir, suffix_filter=True, schema=None)

        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM foo_mb")).scalar_one()
            assert count == 1

        # Drop all objects in the current database by passing the database name as schema
        drop_schema_objects(engine, schema=db_name)

        with engine.connect() as conn:
            exists = conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=:db AND table_name='foo_mb'"
                ).bindparams(db=db_name)
            ).scalar_one()
            assert exists == 0
    finally:
        cleanup_db_containers("mariadb")


@pytest.mark.slow
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.oracle
def test_execute_sql_and_delete_schema_oracle(tmp_path: Path):
    engine = get_connection(
        db_type="oracle",
        db_name="ggmexec",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=1523,
        force_refresh=True,
        print_tables=False,
    )

    try:
        sql_dir = tmp_path / "sql"
        sql_dir.mkdir()

        (sql_dir / "01_make_table_oracle.sql").write_text(
            """
            BEGIN
              EXECUTE IMMEDIATE 'DROP TABLE FOO_OR';
            EXCEPTION WHEN OTHERS THEN NULL; END;
            /
            CREATE TABLE FOO_OR(id NUMBER(10) PRIMARY KEY);
            INSERT INTO FOO_OR(id) VALUES (9);
            """,
            encoding="utf-8",
        )

        execute_sql_folder(engine, sql_dir, suffix_filter=True, schema=None)

        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM FOO_OR")).scalar_one()
            assert count == 1

        # Drop objects in the current user schema (SA)
        drop_schema_objects(engine, schema="SA")

        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT COUNT(*) FROM user_tables WHERE table_name='FOO_OR'")
            ).scalar_one()
            assert exists == 0
    finally:
        cleanup_db_containers("oracle")


@pytest.mark.sqlite
def test_execute_sql_and_delete_schema_sqlite(tmp_path: Path):
    # Use in-memory SQLite for a quick integration-style run
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///:memory:")

    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()

    (sql_dir / "01_generic.sql").write_text(
        "CREATE TABLE will_be_ignored(id INT);", encoding="utf-8"
    )
    (sql_dir / "02_make_table_sqlite.sql").write_text(
        """
        CREATE TABLE foo_sq(id INT PRIMARY KEY);
        INSERT INTO foo_sq(id) VALUES (3);
        """,
        encoding="utf-8",
    )

    execute_sql_folder(engine, sql_dir, suffix_filter=True, schema=None)

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM foo_sq")).scalar_one()
        assert count == 1

    drop_schema_objects(engine, schema=None)

    with engine.connect() as conn:
        exists = conn.execute(
            text(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='foo_sq'"
            )
        ).scalar_one()
        assert exists == 0
