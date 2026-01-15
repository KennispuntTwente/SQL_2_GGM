# End-to-end pipeline test reproducing the synthetic/README workflow on Postgres
# Focuses on generating CSVs, loading to source, and running sql_to_staging + staging_to_silver
# This ensures the full synthetic data pipeline works correctly with real containers

import os
import random
import pathlib
import subprocess

import pytest
from sqlalchemy import text

# Tables from synthetic dataset
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
def test_readme_one_liner_pipeline_postgres(tmp_path):
    """End-to-end test reproducing the synthetic/README pipeline (Postgres).

    Steps:
    1. Generate synthetic CSVs
    2. Load them into the source database (public schema) in a Postgres container
    3. Create destination database 'ggm' and schemas staging & silver
    4. Run sql_to_staging to copy tables source -> ggm.staging
    5. Run staging_to_silver to map ggm.staging -> ggm.silver using queries & DDL

    Assertions:
    - All SOURCE_TABLES exist in schema staging of DB ggm
    - At least one table exists in schema silver after mapping
    - silver schema has >= 1 table; staging has all expected tables
    (Row counts are intentionally not asserted to stay robust against query filtering.)
    """
    if os.getenv("RUN_SLOW_TESTS") != "1":
        pytest.skip("RUN_SLOW_TESTS not enabled")

    # Use repository root as CWD so `python -m synthetic.*` resolves the package
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    synthetic_dir = repo_root / "data" / "synthetic_e2e"
    synthetic_dir.mkdir(parents=True, exist_ok=True)

    password = "SecureP@ss1!24323482349"
    # Pick a high, pseudo-random port to avoid collisions with parallel CI jobs
    port = random.randint(56000, 58000)

    # 1) Generate CSVs
    # Use module invocation so this works both from source checkout and
    # installed package layouts (as used in CI).
    gen_cmd = [
        "python",
        "-m",
        "synthetic.generate_synthetic_data",
        "--out",
        str(synthetic_dir),
        "--rows",
        "12",
        "--seed",
        "987",
    ]
    subprocess.run(gen_cmd, check=True, cwd=repo_root)

    # 2) Load into source DB (schema public -> pass empty schema to loader)
    # Invoke loader as a module to ensure package context (avoids ad-hoc sys.path edits).
    load_cmd = [
        "python",
        "-m",
        "synthetic.load_csvs_to_db",
        "--db",
        "postgres",
        "--db-name",
        "source",
        "--user",
        "sa",
        "--password",
        password,
        "--port",
        str(port),
        "--schema",
        "",  # empty -> public
        "--csv-dir",
        str(synthetic_dir),
        "--force-refresh",
    ]
    subprocess.run(load_cmd, check=True, cwd=repo_root)

    # 3) Ensure ggm DB exists & create schemas staging & silver
    from dev_sql_server.get_connection import get_connection

    engine = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="sa",
        password=password,
        port=port,
        force_refresh=True,
        print_tables=False,
    )
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver"))

    # 4) Run sql_to_staging (source -> ggm.staging) via INI
    ini_src = tmp_path / "src_to_staging.ini"
    ini_src.write_text(
        "\n".join(
            [
                "[database-source]",
                "SRC_DRIVER = postgresql+psycopg2",
                "SRC_HOST = localhost",
                f"SRC_PORT = {port}",
                "SRC_DB = source",
                "SRC_USERNAME = sa",
                f"SRC_PASSWORD = {password}",
                "",
                "[database-destination]",
                "DST_DRIVER = postgresql+psycopg2",
                "DST_HOST = localhost",
                f"DST_PORT = {port}",
                "DST_DB = ggm",
                "DST_SCHEMA = staging",
                "DST_USERNAME = sa",
                f"DST_PASSWORD = {password}",
                "",
                "[settings]",
                "TRANSFER_MODE = SQLALCHEMY_DIRECT",
                f"SRC_TABLES = {','.join(SOURCE_TABLES)}",
                "ASK_PASSWORD_IN_CLI = False",
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(
        ["python", "-m", "sql_to_staging.main", "--config", str(ini_src)],
        check=True,
        cwd=repo_root,
    )

    # 5) Run staging_to_silver (ggm.staging -> ggm.silver) via INI
    ini_silver = tmp_path / "staging_to_silver.ini"
    ini_silver.write_text(
        "\n".join(
            [
                "[database-destination]",
                "DST_DRIVER = postgresql+psycopg2",
                "DST_HOST = localhost",
                f"DST_PORT = {port}",
                "DST_DB = ggm",
                "DST_SCHEMA = staging",
                "DST_USERNAME = sa",
                f"DST_PASSWORD = {password}",
                "",
                "[settings]",
                "SILVER_SCHEMA = silver",
                "INIT_SQL_FOLDER = ggm_selectie/cssd",
                "INIT_SQL_SUFFIX_FILTER = True",
                "DELETE_EXISTING_SCHEMA = True",
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(
        ["python", "-m", "staging_to_silver.main", "--config", str(ini_silver)],
        check=True,
        cwd=repo_root,
    )

    # Assertions
    with engine.connect() as conn:
        staging_tables = conn.execute(
            text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='staging' ORDER BY table_name
        """)
        ).fetchall()
        staging_set = {r[0].lower() for r in staging_tables}
        missing = {t for t in SOURCE_TABLES if t not in staging_set}
        assert not missing, f"Staging missing tables: {missing} (have: {staging_set})"

        silver_tables = conn.execute(
            text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='silver' ORDER BY table_name
        """)
        ).fetchall()
        assert silver_tables, "No silver tables created by staging_to_silver pipeline"

    # Cleanup: remove container (best-effort)
    try:
        import docker

        client = docker.from_env()
        name = f"postgres-docker-db-{port}"
        c = client.containers.get(name)
        c.stop()
        c.remove()
    except Exception:
        # ignore failures (container may be reused by other tests)
        pass
