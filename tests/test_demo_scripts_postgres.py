# Integration tests for demo scripts running against Postgres
# Focuses on verifying sql_to_staging and staging_to_silver demos create expected tables
# This ensures demo scripts work end-to-end with real Postgres containers

import subprocess
import pathlib

import pytest
from sqlalchemy import text

from tests.integration_utils import docker_running, slow_tests_enabled
from dev_sql_server.get_connection import get_connection

# Tables loaded by synthetic demo
SOURCE_TABLES = [
    "szclient",
    "wvbesl",
    "wvind_b",
    "szregel",
    "wvdos",
    "abc_refcod",
    "szukhis",
    "szwerker",
]


@pytest.mark.slow
@pytest.mark.postgres
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_demo_sql_to_staging_then_staging_to_silver_postgres():
    """Runs both demo scripts and verifies staging and silver effects on Postgres.

    - Runs `bash sql_to_staging/demo/demo.sh` to generate and load synthetic data
    - Runs `bash staging_to_silver/demo/demo.sh` to initialize silver and map from staging
    - Asserts all SOURCE_TABLES exist in `staging` and at least two have rows
    - Asserts known silver tables exist in `silver` and that silver has tables
    """
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    # Execute the demo scripts from repository root
    subprocess.run(["bash", "sql_to_staging/demo/demo.sh"], check=True, cwd=repo_root)
    subprocess.run(
        ["bash", "staging_to_silver/demo/demo.sh"], check=True, cwd=repo_root
    )

    # Connect to the Postgres dev DB used by demos (port 55432)
    engine = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="postgres",
        password="postgres",
        port=55432,
        force_refresh=False,
        print_tables=False,
    )

    with engine.connect() as conn:
        # Verify staging tables exist
        staging_tables = conn.execute(
            text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='staging' ORDER BY table_name
            """)
        ).fetchall()
        staging_set = {r[0].lower() for r in staging_tables}
        missing = {t for t in SOURCE_TABLES if t not in staging_set}
        assert not missing, f"Staging missing tables: {missing} (have: {staging_set})"

        # Check at least two of the source tables have rows as a sanity check
        non_empty = 0
        for t in SOURCE_TABLES:
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM staging.{t}")).scalar()
            if cnt and int(cnt) > 0:
                non_empty += 1
        assert non_empty >= 2, (
            f"Expected at least two non-empty staging tables, got {non_empty}"
        )

        # Verify silver schema is initialized with tables and known names exist
        silver_tables = conn.execute(
            text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='silver' ORDER BY table_name
            """)
        ).fetchall()
        assert silver_tables, "No silver tables created by staging_to_silver demo"
        silver_set = {r[0].lower() for r in silver_tables}
        # From ggm_selectie/cssd/ DDL (unquoted identifiers -> lowercased in Postgres)
        assert "client" in silver_set, "Expected table 'client' in silver schema"
        assert "declaratieregel" in silver_set, (
            "Expected table 'declaratieregel' in silver schema"
        )


@pytest.mark.slow
@pytest.mark.postgres
@pytest.mark.skipif(
    not slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_demo_odata_to_staging_postgres(tmp_path):
    """Runs the odata_to_staging demo and verifies OData tables are loaded in Postgres.

    Uses Northwind sample service for a tiny, deterministic subset.
    """
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    # Prepare a minimal .env for the demo to read (main.py loads odata_to_staging/.env)
    # Use a small entity set and a modest row limit to keep runtime bounded.
    env_path = repo_root / "odata_to_staging" / ".env"
    original_env = None
    if env_path.exists():
        original_env = env_path.read_text(encoding="utf-8")
    env_path.write_text(
        "\n".join(
            [
                "# Test .env for OData demo",
                "ODATA_URL = https://services.odata.org/V2/Northwind/Northwind.svc/",
                "ODATA_AUTH_MODE = NONE",
                "ODATA_ENTITY_SETS = Categories",
                "ODATA_PAGE_SIZE = 10",
                "ROW_LIMIT = 50",
                "LOWER_TABLE_NAMES = true",
                # Destination matches demo/config.ini
                "DST_DRIVER = postgresql+psycopg2",
                "DST_USERNAME = postgres",
                "DST_PASSWORD = postgres",
                "DST_HOST = localhost",
                "DST_PORT = 55432",
                "DST_DB = ggm",
                "DST_SCHEMA = odata_staging",
            ]
        ),
        encoding="utf-8",
    )

    try:
        # Run the demo script which ensures the Postgres dev DB is running
        subprocess.run(
            ["bash", "odata_to_staging/demo/demo.sh"], check=True, cwd=repo_root
        )

        # Connect and verify the odata_staging schema has expected tables with rows
        engine = get_connection(
            db_type="postgres",
            db_name="ggm",
            user="postgres",
            password="postgres",
            port=55432,
            force_refresh=False,
            print_tables=False,
        )
        with engine.connect() as conn:
            tables = conn.execute(
                text(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema='odata_staging' ORDER BY table_name
                    """
                )
            ).fetchall()
            tset = {r[0].lower() for r in tables}
            assert "categories" in tset, (
                "Expected 'categories' table in odata_staging schema"
            )
            cnt = conn.execute(
                text("SELECT COUNT(*) FROM odata_staging.categories")
            ).scalar()
            assert cnt and int(cnt) > 0, "Expected rows in odata_staging.categories"
    finally:
        # Restore any original .env content (best effort)
        if original_env is None:
            try:
                env_path.unlink()
            except Exception:
                pass
        else:
            try:
                env_path.write_text(original_env, encoding="utf-8")
            except Exception:
                pass
