from pathlib import Path
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    insert,
    select,
)
from staging_to_silver.functions.query_loader import load_queries
from source_to_staging.functions.direct_transfer import direct_transfer


def _mk_engine(tmp_path: Path, name: str):
    db = tmp_path / f"{name}.sqlite"
    return create_engine(f"sqlite+pysqlite:///{db}")


def test_direct_transfer_sqlite_to_sqlite(tmp_path: Path):
    src = _mk_engine(tmp_path, "src")
    dst = _mk_engine(tmp_path, "dst")

    # Create source table with mixed types
    meta = MetaData()
    src_tbl = Table(
        "src_mixed",
        meta,
        Column("id", Integer),
        Column("name", String(40)),
        Column("amount", Float),
        Column("flag", Boolean),
        Column("note", Text),
    )
    meta.create_all(src)

    with src.begin() as conn:
        conn.execute(
            insert(src_tbl),
            [
                {"id": 1, "name": "Alice", "amount": 10.5, "flag": True, "note": "x"},
                {"id": 2, "name": "Bob", "amount": 20.0, "flag": False, "note": None},
            ],
        )

    # Run direct transfer (no schemas on SQLite)
    direct_transfer(
        source_engine=src,
        dest_engine=dst,
        tables=["src_mixed"],
        source_schema=None,
        dest_schema=None,
        chunk_size=1,
        lowercase_columns=True,
        write_mode="replace",
    )

    # Validate values
    with dst.connect() as conn:
        rows = conn.execute(
            select(Table("src_mixed", MetaData(), autoload_with=dst))
        ).fetchall()
        assert len(rows) == 2
        # SQLite may coerce booleans to 0/1; compare loosely
        by_id = {r[0]: r for r in rows}
        assert by_id[1][1] == "Alice"
        assert abs(by_id[1][2] - 10.5) < 1e-9
        assert by_id[2][1] == "Bob"
        assert by_id[2][4] is None


def test_staging_to_silver_sqlite_simple(tmp_path: Path):
    # Single SQLite DB for both staging and silver
    eng = _mk_engine(tmp_path, "one")

    meta = MetaData()
    # Source (staging) table
    src_people = Table(
        "src_people",
        meta,
        Column("id", Integer),
        Column("name", String(40)),
    )
    # Destination (silver) table — uppercase name and columns
    people = Table(
        "PEOPLE",
        meta,
        Column("ID", Integer),
        Column("NAME", String(40)),
    )
    meta.create_all(eng)

    with eng.begin() as conn:
        conn.execute(
            insert(src_people), [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Ben"}]
        )

    # Load the single test query and execute using same transaction logic as app
    queries = load_queries(
        table_name_case="upper",
        column_name_case=None,
        extra_modules=("tests.queries_sqlite_simple",),
        scan_package=False,
    )

    with eng.begin() as conn:
        for name, query_fn in queries.items():
            select_stmt = query_fn(eng, source_schema=None)
            # Reflect destination table and order columns according to the SELECT
            dest_tbl = Table(name, MetaData(), autoload_with=eng)
            order = [c.name for c in select_stmt.selected_columns]
            dest_cols_map = {c.name.lower(): c for c in dest_tbl.columns}
            dest_cols = []
            for col in order:
                dest_cols.append(dest_tbl.columns.get(col, dest_cols_map[col.lower()]))

            ins = dest_tbl.insert().from_select(dest_cols, select_stmt)
            conn.execute(ins)

    # Validate destination got rows
    with eng.connect() as conn:
        rows = conn.execute(select(people)).fetchall()
        assert rows == [(1, "Ada"), (2, "Ben")]
