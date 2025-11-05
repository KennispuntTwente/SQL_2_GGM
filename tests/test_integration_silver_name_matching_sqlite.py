from pathlib import Path
import os

import pytest
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert, select

from staging_to_silver.functions.query_loader import load_queries


def _mk_engine(tmp_path: Path, name: str):
    db = tmp_path / f"{name}.sqlite"
    return create_engine(f"sqlite+pysqlite:///{db}")


def _install_simple_mapping(tmp_module_name: str):
    """
    Dynamically install a minimal query module exporting a mapping to 'PEOPLE'.
    The builder labels columns in lower-case to exercise SILVER_NAME_MATCHING.
    """
    import sys
    import types
    from sqlalchemy import select

    def builder(engine, source_schema=None):
        md = MetaData()
        src = Table("src_people", md, autoload_with=engine)
        return select(src.c.id.label("id"), src.c.name.label("name"))

    mod = types.ModuleType(tmp_module_name)
    mod.__query_exports__ = {"PEOPLE": builder}
    sys.modules[tmp_module_name] = mod


def test_silver_name_matching_strict_and_column_case(tmp_path: Path):
    eng = _mk_engine(tmp_path, "silver_name_match")

    # Create staging and silver tables (silver has UPPER column names)
    meta = MetaData()
    src_people = Table("src_people", meta, Column("id", Integer), Column("name", String(40)))
    people = Table("PEOPLE", meta, Column("ID", Integer), Column("NAME", String(40)))
    meta.create_all(eng)

    with eng.begin() as conn:
        conn.execute(insert(src_people), [{"id": 1, "name": "Ada"}])

    # Install a simple mapping module with lower-case labels
    _install_simple_mapping("tests._tmp_queries_people_lower_labels")

    # Load queries including our temp module
    queries = load_queries(
        table_name_case="upper",
        column_name_case=None,
        extra_modules=("tests._tmp_queries_people_lower_labels",),
        scan_package=True,
    )
    assert "PEOPLE" in queries

    # Helper insert honoring SILVER_NAME_MATCHING=auto (default)
    def _insert(select_name, stmt):
        dest_tbl = Table(select_name, MetaData(), autoload_with=eng)
        order = [c.name for c in stmt.selected_columns]
        dest_map = {c.name.lower(): c for c in dest_tbl.columns}
        cols = []
        for name in order:
            try:
                cols.append(dest_tbl.columns[name])
            except KeyError:
                if os.getenv("SILVER_NAME_MATCHING", "auto").lower() != "strict":
                    ci = dest_map.get(name.lower())
                    if ci is not None:
                        cols.append(ci)
                        continue
                # Re-raise to match strict behavior
                raise
        ins = dest_tbl.insert().from_select(cols, stmt)
        with eng.begin() as conn:
            conn.execute(ins)

    # Baseline: auto matching should succeed even though labels are lower-case
    os.environ["SILVER_NAME_MATCHING"] = "auto"
    stmt = queries["PEOPLE"](eng, source_schema=None)
    _insert("PEOPLE", stmt)
    with eng.connect() as conn:
        rows = conn.execute(select(people)).fetchall()
    assert rows == [(1, "Ada")]

    # Strict: without relabeling, matching lower-case labels against UPPER columns should fail
    os.environ["SILVER_NAME_MATCHING"] = "strict"
    with pytest.raises(KeyError):
        # Rebuild select and attempt insert to trigger strict mismatch
        stmt2 = queries["PEOPLE"](eng, source_schema=None)
        _insert("PEOPLE", stmt2)

    # Now enable SILVER_COLUMN_NAME_CASE=upper so labels are coerced; strict should pass
    queries2 = load_queries(
        table_name_case="upper",
        column_name_case="upper",
        extra_modules=("tests._tmp_queries_people_lower_labels",),
        scan_package=True,
    )
    os.environ["SILVER_NAME_MATCHING"] = "strict"
    stmt3 = queries2["PEOPLE"](eng, source_schema=None)
    _insert("PEOPLE", stmt3)
    with eng.connect() as conn:
        rows2 = conn.execute(select(people).order_by(people.c.ID)).fetchall()
    # One previous row + one new row (duplicate allowed since no PK); both equal content
    assert rows2 == [(1, "Ada"), (1, "Ada")]
