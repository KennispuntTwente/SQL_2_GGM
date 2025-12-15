from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import MetaData, Table, text

from dev_sql_server.get_connection import get_connection
from staging_to_silver.functions.schema_qualifier import qualify_schema
from tests.integration_utils import (
    docker_running,
    mssql_driver_available,
    slow_tests_enabled,
)
from tests.integration_utils import port_for_worker


@pytest.mark.slow
@pytest.mark.mssql
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
@pytest.mark.skipif(
    not mssql_driver_available(),
    reason="ODBC Driver 18 for SQL Server not installed; required for MSSQL test.",
)
def test_mssql_crossdb_init_and_load(tmp_path: Path):
    # Use one SQL Server container (single instance) and create two databases in it
    port = port_for_worker(1437)
    user = "sa"
    password = "S3cureP@ssw0rd!23243"

    # 1) Start/reuse container and create source DB (connect engine to source)
    src_db = "srcdb_cross"
    engine = get_connection(
        db_type="mssql",
        db_name=src_db,
        user=user,
        password=password,
        port=port,
        force_refresh=True,
        sql_folder=None,
        sql_suffix_filter=True,
        sql_schema=None,
        print_tables=False,
    )

    # 2) Ensure target DB exists in the same instance (create via master connection)
    silver_db = "ggmdb_cross"
    from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine

    url = engine.url
    driver = f"{url.get_backend_name()}+{url.get_driver_name()}"
    master_engine = create_sqlalchemy_engine(
        driver=driver,
        username=url.username or user,
        password=url.password or password,
        host=url.host or "localhost",
        port=url.port or port,
        database="master",
        mssql_odbc_driver="ODBC Driver 18 for SQL Server",
    )
    # CREATE DATABASE must run outside an explicit transaction on MSSQL
    with master_engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as conn:
        conn.exec_driver_sql(
            f"IF DB_ID(N'{silver_db}') IS NULL CREATE DATABASE [{silver_db}]"
        )

    # 3) Prepare staging table in source DB and schema
    with engine.begin() as conn:
        conn.execute(
            text("IF SCHEMA_ID(N'staging') IS NULL EXEC('CREATE SCHEMA [staging]')")
        )
        conn.execute(
            text(
                "IF OBJECT_ID(N'staging.demotable', N'U') IS NOT NULL DROP TABLE staging.demotable"
            )
        )
        conn.execute(text("CREATE TABLE staging.demotable (id INT, val INT)"))
        conn.execute(
            text("INSERT INTO staging.demotable(id, val) VALUES (1, 10), (2, 20)")
        )

    # 4) Create silver table in silver_db via INIT_SQL (schema-qualified file)
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()
    sql_file = sql_dir / "001_demo_mssql.sql"
    sql_file.write_text(
        "CREATE TABLE [silver].[demo_silver] (id INT, val INT);\n", encoding="utf-8"
    )

    # Execute SQL scripts against the target DB using a separate engine
    from utils.database.execute_sql_folder import execute_sql_folder
    from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine

    # Build an engine to the silver DB in the same instance
    with engine.begin() as conn:
        # Extract host/port from engine.url
        url = engine.url
        driver = f"{url.get_backend_name()}+{url.get_driver_name()}"
        host = url.host or "localhost"
        port_effective = url.port or port
        username = url.username or user
        pwd = url.password or password

    silver_engine = create_sqlalchemy_engine(
        driver=driver,
        username=username,
        password=pwd,
        host=host,
        port=port_effective,
        database=silver_db,
        mssql_odbc_driver="ODBC Driver 18 for SQL Server",
    )

    execute_sql_folder(
        silver_engine,
        sql_dir,
        suffix_filter=False,  # run our single file regardless of suffix
        schema="silver",
    )

    # 5) Run a minimal staging_to_silver step using three-part naming for MSSQL target
    # Build the same projection as the smoke query: id, val from staging.demotable
    from sqlalchemy import select

    md_src = MetaData()
    src_tbl = Table("demotable", md_src, schema="staging", autoload_with=engine)
    select_stmt = select(src_tbl.c.id.label("id"), src_tbl.c.val.label("val"))

    md = MetaData()
    target_schema_for_sa = qualify_schema(
        "mssql", silver_db, "silver", default_schema="dbo"
    )
    dest = Table(
        "demo_silver",
        md,
        schema=target_schema_for_sa,
        autoload_with=engine,
        extend_existing=True,
    )

    cols = [c.name for c in select_stmt.selected_columns]
    dest_map = {c.name.lower(): c for c in dest.columns}
    ordered_cols = []
    for c in cols:
        try:
            ordered_cols.append(dest.columns[c])
        except KeyError:
            ci = dest_map.get(c.lower())
            assert ci is not None, f"Missing col {c} in {dest.fullname}"
            ordered_cols.append(ci)

    with engine.begin() as conn:
        conn.execute(dest.insert().from_select(ordered_cols, select_stmt))
        cnt = conn.execute(
            text(f"SELECT COUNT(*) FROM {silver_db}.silver.demo_silver")
        ).scalar_one()

    assert cnt == 2
