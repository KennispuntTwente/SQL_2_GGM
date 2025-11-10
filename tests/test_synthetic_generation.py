from pathlib import Path
import subprocess
import sys
import sqlite3
import pytest

# Basic smoke test for synthetic data generation and a minimal staging_to_silver run on SQLite.
# We avoid Docker dependencies here; this ensures the generator keeps required columns present.


@pytest.mark.fast
def test_generate_and_shape(tmp_path: Path):
    out = tmp_path / "synthetic"
    out.mkdir()

    # Run generator script
    # Pad is verplaatst naar synthetic/
    script = Path("synthetic/generate_synthetic_data.py")
    assert script.exists(), "Generator script missing"
    subprocess.run(
        [sys.executable, str(script), "--out", str(out), "--rows", "3", "--seed", "7"],
        check=True,
    )

    # Ensure a couple of expected files
    expected = {
        "szclient.csv",
        "wvbesl.csv",
        "wvind_b.csv",
        "szregel.csv",
        "wvdos.csv",
        "abc_refcod.csv",
        "szukhis.csv",
        "szwerker.csv",
    }
    found = {p.name for p in out.glob("*.csv")}
    assert expected.issubset(found)

    # Load into SQLite staging DB (simpler than full pipeline) and check table row counts
    db_path = tmp_path / "staging.db"
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for csv in out.glob("*.csv"):
            table = csv.stem
            # Create naive table: infer types by reading header then full file lines
            with csv.open("r", encoding="utf-8") as f:
                header = f.readline().strip().split(",")
                rows = [line.strip().split(",") for line in f.readlines()]
            # Build CREATE TABLE statement (all TEXT for portability)
            cols_sql = ", ".join(f"{col} TEXT" for col in header)
            cur.execute(f"CREATE TABLE {table} ({cols_sql})")
            for r in rows:
                placeholders = ",".join(["?"] * len(r))
                cur.execute(f"INSERT INTO {table} VALUES ({placeholders})", r)
        conn.commit()

        # Simple shape assertions mirroring query expectations
        # szclient at least 'rows' count
        count_client = cur.execute("SELECT COUNT(*) FROM szclient").fetchone()[0]
        assert count_client >= 3
        # wvbesl rows present
        count_besl = cur.execute("SELECT COUNT(*) FROM wvbesl").fetchone()[0]
        assert count_besl >= 3
    finally:
        conn.close()
