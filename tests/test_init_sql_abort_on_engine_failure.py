import configparser
import pathlib
import pytest

from staging_to_silver.functions.init_sql import run_init_sql


@pytest.fixture()
def cfg_tmp_dir(tmp_path: pathlib.Path):
    # Create a temporary INIT_SQL_FOLDER with a harmless SQL file
    sql_dir = tmp_path / "init_sql"
    sql_dir.mkdir()
    (sql_dir / "001_dummy.sql").write_text(
        "-- dummy file; should not be executed due to abort"
    )

    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    cfg.set("settings", "INIT_SQL_FOLDER", str(sql_dir))
    cfg.set("settings", "INIT_SQL_SUFFIX_FILTER", "true")
    cfg.set("settings", "DELETE_EXISTING_SCHEMA", "false")

    cfg.add_section("database-destination")
    cfg.set("database-destination", "DST_DRIVER", "mssql+pyodbc")
    cfg.set("database-destination", "DST_USERNAME", "user")
    cfg.set("database-destination", "DST_PASSWORD", "pass")
    cfg.set("database-destination", "DST_HOST", "localhost")
    cfg.set("database-destination", "DST_PORT", "1433")
    cfg.set("database-destination", "DST_DB", "StageDB")

    return cfg, sql_dir


def test_run_init_sql_aborts_on_silver_engine_failure(monkeypatch, cfg_tmp_dir):
    cfg, _ = cfg_tmp_dir

    # Force create_sqlalchemy_engine to raise to simulate misconfigured SILVER_DB
    from staging_to_silver.functions import init_sql as init_sql_module

    def _raise(*args, **kwargs):  # noqa: D401
        raise ValueError("simulated engine creation failure")

    monkeypatch.setattr(init_sql_module, "create_sqlalchemy_engine", _raise)

    with pytest.raises(ValueError):
        run_init_sql(
            engine=None,  # main engine unused in failure path
            cfg=cfg,
            dialect_name="mssql",
            database="StageDB",
            silver_db="SilverDB",  # different triggers cross-DB logic
            silver_schema="dbo",
        )
