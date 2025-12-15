import os
import subprocess
import sys
import runpy
import io
import contextlib

import pytest
from sqlalchemy import text
from dotenv import load_dotenv

from dev_sql_server.get_connection import get_connection


load_dotenv("tests/.env")


def _docker_running() -> bool:
    try:
        res = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=5
        )
        return res.returncode == 0
    except Exception:
        return False


def _slow_tests_enabled() -> bool:
    return os.getenv("RUN_SLOW_TESTS", "0").lower() in {"1", "true", "yes", "on"}


@pytest.mark.slow
@pytest.mark.postgres
@pytest.mark.skipif(
    not _slow_tests_enabled(),
    reason="RUN_SLOW_TESTS not enabled; set to 1 to run slow integration tests.",
)
@pytest.mark.skipif(
    not _docker_running(),
    reason="Docker is not available/running; required for this integration test.",
)
def test_main_staging_to_silver_postgres(tmp_path):
    # Start Postgres with silver schema initialized from GGM DDL
    engine = get_connection(
        db_type="postgres",
        db_name="ggm_main_staging_to_silver",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=5434,
        force_refresh=True,
        sql_folder="./ggm_selectie/CSSD",
        sql_suffix_filter=True,
        sql_schema="silver",
        print_tables=False,
    )

    # Create minimal staging data required by a couple of queries
    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "staging"'))
        conn.execute(
            text(
                """
			DROP TABLE IF EXISTS staging.wvind_b CASCADE;
			CREATE TABLE staging.wvind_b (
				besluitnr VARCHAR(50),
				volgnr_ind VARCHAR(50),
				dd_eind TIMESTAMP,
				dd_begin TIMESTAMP,
				volume INTEGER,
				status_indicatie VARCHAR(50),
				kode_regeling VARCHAR(50),
				clientnr VARCHAR(50)
			);
			DROP TABLE IF EXISTS staging.szregel CASCADE;
			CREATE TABLE staging.szregel (
				kode_regeling VARCHAR(50),
				omschryving VARCHAR(50)
			);
			DROP TABLE IF EXISTS staging.wvbesl CASCADE;
			CREATE TABLE staging.wvbesl (
				besluitnr VARCHAR(50)
			);
			DROP TABLE IF EXISTS staging.wvdos CASCADE;
			CREATE TABLE staging.wvdos (
				besluitnr VARCHAR(50),
				volgnr_ind VARCHAR(50),
				kode_reden_einde_voorz VARCHAR(50)
			);
			DROP TABLE IF EXISTS staging.abc_refcod CASCADE;
			CREATE TABLE staging.abc_refcod (
				code VARCHAR(50),
				omschrijving VARCHAR(50),
				domein VARCHAR(100)
			);
			"""
            )
        )
        conn.execute(
            text(
                """
			INSERT INTO staging.wvind_b (besluitnr, volgnr_ind, dd_eind, dd_begin, volume, status_indicatie, kode_regeling, clientnr)
			VALUES ('B001','01','2024-01-01 00:00:00','2023-12-02 00:00:00',10,'active','KR1','C1');
			INSERT INTO staging.szregel (kode_regeling, omschryving) VALUES ('KR1','JEUGDWET');
			INSERT INTO staging.wvbesl (besluitnr) VALUES ('B001');
			INSERT INTO staging.wvdos (besluitnr, volgnr_ind, kode_reden_einde_voorz) VALUES ('B001','01','RC1');
			INSERT INTO staging.abc_refcod (code, omschrijving, domein) VALUES ('RC1','Some reason','JZG_REDEN_EINDE_PRODUCT');
			"""
            )
        )
        # Upper-case variant for BESCHIKKING
        conn.execute(text('DROP TABLE IF EXISTS staging."WVBESL" CASCADE;'))
        conn.execute(
            text(
                'CREATE TABLE staging."WVBESL" ("BESLUITNR" VARCHAR(50), "CLIENTNR" VARCHAR(50));'
            )
        )
        conn.execute(
            text(
                'INSERT INTO staging."WVBESL" ("BESLUITNR", "CLIENTNR") VALUES (\'B001\', \'C1\');'
            )
        )

    # Create config for staging_to_silver.main
    cfg_path = tmp_path / "staging_to_silver.ini"
    cfg_path.write_text(
        """
[database-destination]
DST_DRIVER=postgresql+psycopg2
DST_USERNAME=sa
DST_PASSWORD=S3cureP@ssw0rd!23243
DST_HOST=localhost
DST_PORT=5434
DST_DB=ggm_main_staging_to_silver
DST_SCHEMA=staging

[settings]
SILVER_SCHEMA=silver
SILVER_TABLE_NAME_CASE=upper
SILVER_NAME_MATCHING=auto
ASK_PASSWORD_IN_CLI=False
ROW_LIMIT=
""".strip()
    )

    # Execute staging_to_silver.main in-process via runpy to ensure current env/interpreter is used
    old_argv = sys.argv[:]
    sys.argv = ["staging_to_silver.main", "--config", str(cfg_path)]
    buf_out, buf_err = io.StringIO(), io.StringIO()
    return_code = 0
    try:
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            runpy.run_module("staging_to_silver.main", run_name="__main__")
    except SystemExit as e:
        # argparse/sys.exit might be used; capture exit code
        return_code = e.code if isinstance(e.code, int) else 1
    finally:
        stdout, stderr = buf_out.getvalue(), buf_err.getvalue()
        sys.argv = old_argv

    if return_code != 0:
        raise AssertionError(
            f"staging_to_silver.main failed: {return_code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )

    # Validate a couple of target tables have rows
    with engine.connect() as conn:
        cnt_bv = conn.execute(
            text("SELECT COUNT(*) FROM silver.beschikte_voorziening")
        ).scalar_one()
        cnt_b = conn.execute(
            text("SELECT COUNT(*) FROM silver.beschikking")
        ).scalar_one()
    assert cnt_bv >= 1
    assert cnt_b >= 1
