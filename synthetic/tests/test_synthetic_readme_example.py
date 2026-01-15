# Tests for synthetic data README example script
# Focuses on running the exact one-liner example from synthetic/README.md
# This ensures documented examples remain functional and produce expected results

import os
import pathlib
import random
import subprocess

import pytest
from sqlalchemy import text


@pytest.mark.slow
@pytest.mark.postgres
def test_synthetic_readme_one_liner_script_runs(tmp_path):
    """Run the exact example script referenced by synthetic/README.md.

    We override PORT and OUT_DIR to avoid collisions across parallel runs, but otherwise
    the commands are identical to the README example via the maintained script.
    """
    if os.getenv("RUN_SLOW_TESTS") != "1":
        pytest.skip("RUN_SLOW_TESTS not enabled")

    # Repo root needed so paths like synthetic/examples/... resolve correctly
    repo = pathlib.Path(__file__).resolve().parents[2]
    script = repo / "synthetic" / "examples" / "one_liner_postgres.sh"
    assert script.exists(), "Example script missing; README reference out of sync"

    # Use a random high port and a separate output dir to minimize conflicts
    port = random.randint(56000, 59000)
    out_dir = repo / "data" / f"synthetic_{port}"
    out_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("PASSWORD", "SecureP@ss1!24323482349")
    env["PORT"] = str(port)
    env["OUT_DIR"] = str(out_dir)
    env.setdefault("ROWS", "10")

    # Ensure executable bit (Windows CI uses bash too via Git Bash or WSL)
    try:
        script.chmod(0o755)
    except Exception:
        pass

    # Run the example script from repo root
    subprocess.run(["bash", str(script)], check=True, cwd=str(repo), env=env)

    # Verify results by connecting via helper
    from dev_sql_server.get_connection import get_connection

    engine = get_connection(
        db_type="postgres",
        db_name="ggm",
        user="sa",
        password=env["PASSWORD"],
        port=port,
        force_refresh=False,
        print_tables=False,
    )

    with engine.connect() as conn:
        staging_tables = {
            r[0]
            for r in conn.execute(
                text("""
            SELECT table_name FROM information_schema.tables WHERE table_schema='staging'
        """)
            )
        }
        assert staging_tables, "No tables found in staging schema after sql_to_staging"

        silver_tables = {
            r[0]
            for r in conn.execute(
                text("""
            SELECT table_name FROM information_schema.tables WHERE table_schema='silver'
        """)
            )
        }
        assert silver_tables, "No tables found in silver schema after staging_to_silver"

    # Best-effort cleanup: stop/remove the container for this port
    try:
        import docker

        client = docker.from_env()
        name = f"postgres-docker-db-{port}"
        c = client.containers.get(name)
        c.stop()
        c.remove()
    except Exception:
        pass
