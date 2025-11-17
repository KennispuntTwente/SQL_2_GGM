import configparser
from pathlib import Path

from staging_to_silver.functions.queries_setup import prepare_queries


def _make_cfg(**settings: str) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    cfg.add_section("settings")
    for k, v in settings.items():
        cfg.set("settings", k, v)
    return cfg


def test_query_paths_overrides_default(tmp_path: Path):
    # Create a minimal custom query file exporting a single mapping 'FOO'
    qfile = tmp_path / "my_query.py"
    qfile.write_text(
        """
from sqlalchemy import select, literal
__query_exports__ = {
    'FOO': lambda engine, source_schema=None: select(literal(1).label('A'))
}
""",
        encoding="utf-8",
    )

    cfg = _make_cfg(QUERY_PATHS=str(tmp_path))

    queries = prepare_queries(cfg)

    # Only our custom mapping should be present; built-in package should NOT load by default
    assert set(queries.keys()) == {"FOO"}


def test_query_paths_can_include_default_and_custom(tmp_path: Path):
    # Create a minimal custom query file exporting mapping 'BAR'
    qfile = tmp_path / "extra_query.py"
    qfile.write_text(
        """
from sqlalchemy import select, literal
__query_exports__ = {
    'BAR': lambda engine, source_schema=None: select(literal(2).label('B'))
}
""",
        encoding="utf-8",
    )

    # Compute path to built-in queries directory
    repo_root = Path(__file__).resolve().parents[1]
    default_dir = repo_root / "queries"
    assert default_dir.exists(), f"Default queries dir not found: {default_dir}"

    # Provide both paths; default package should be loaded via filesystem scan
    cfg = _make_cfg(QUERY_PATHS=f"{tmp_path}; {default_dir}")

    queries = prepare_queries(cfg)

    keys = set(queries.keys())
    # Expect at least one known default mapping plus our custom one
    assert "BAR" in keys
    # Known repo usually contains BESCHIKKING mapping
    assert any(k.upper() == "BESCHIKKING" for k in keys)
