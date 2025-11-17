import os
import sys
import runpy
import io
import contextlib
import subprocess

import pytest
import requests
from sqlalchemy import text

from dev_sql_server.get_connection import get_connection


NORTHWIND_V2 = "https://services.odata.org/V2/Northwind/Northwind.svc/"


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


def _northwind_available() -> bool:
    """Best-effort sanity check that the Northwind service is reachable and returns JSON for an entity set.

    Some environments or mirrors require explicit $format=json for v2. We try both base and a simple query.
    """
    try:
        base = requests.get(NORTHWIND_V2, timeout=5)
        if base.status_code != 200:
            return False
        probe = requests.get(f"{NORTHWIND_V2}Employees?$top=1&$format=json", timeout=8)
        if probe.status_code != 200:
            return False
        # Basic JSON check
        ct = probe.headers.get("Content-Type", "").lower()
        if "json" not in ct:
            # Some endpoints return JSON without correct header; try parsing
            try:
                _ = probe.json()
            except Exception:
                return False
        return True
    except Exception:
        return False


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
@pytest.mark.skipif(
    not _northwind_available(),
    reason="Northwind OData service not reachable; skipping to avoid flakey failures.",
)
def test_main_odata_to_staging_postgres(tmp_path):
    # Start a fresh Postgres destination
    engine = get_connection(
        db_type="postgres",
        db_name="ggm_odata_to_staging",
        user="sa",
        password="S3cureP@ssw0rd!23243",
        port=5434,
        force_refresh=True,
        print_tables=False,
    )

    # Prepare config for odata_to_staging.main
    cfg_path = tmp_path / "odata_to_staging.ini"
    cfg_path.write_text(
        f"""
[odata-source]
ODATA_URL={NORTHWIND_V2}
ODATA_AUTH_MODE=NONE
ODATA_ENTITY_SETS=Employees
ODATA_VERIFY_SSL=true

[database-destination]
DST_DRIVER=postgresql+psycopg2
DST_USERNAME=sa
DST_PASSWORD=S3cureP@ssw0rd!23243
DST_HOST=localhost
DST_PORT=5434
DST_DB=ggm_odata_to_staging
DST_SCHEMA=staging

[settings]
ODATA_PAGE_SIZE=200
WRITE_MODE=replace
CLEANUP_PARQUET_FILES=false
LOG_ROW_COUNT=true
""".strip()
    )

    # Run the main module in-process with argv (in tmp_path as CWD so parquet files are isolated)
    old_argv = sys.argv[:]
    old_cwd = os.getcwd()
    sys.argv = ["odata_to_staging.main", "--config", str(cfg_path)]
    buf_out, buf_err = io.StringIO(), io.StringIO()
    return_code = 0
    try:
        os.chdir(tmp_path)
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            runpy.run_module("odata_to_staging.main", run_name="__main__")
    except SystemExit as e:
        return_code = e.code if isinstance(e.code, int) else 1
    finally:
        stdout, stderr = buf_out.getvalue(), buf_err.getvalue()
        sys.argv = old_argv
        os.chdir(old_cwd)

    if return_code != 0:
        raise AssertionError(
            f"odata_to_staging.main failed: {return_code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )

    # If no parquet files were produced, the public endpoint likely blocked or changed – skip gracefully
    data_dir = tmp_path / "data"
    produced = [f for f in (data_dir.glob("Employees_part*.parquet"))]
    if not produced:
        pytest.skip(
            f"Northwind endpoint returned no rows (no parquet files created in {data_dir}); skipping test"
        )

    # Validate that staging.employees exists and has at least one row
    with engine.connect() as conn:
        cnt = conn.execute(text("SELECT COUNT(*) FROM staging.employees")).scalar_one()
    assert cnt >= 1
