from pathlib import Path

from sqlalchemy import Column, Integer, String, Table, MetaData, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.dml import Insert

from sql_to_staging.functions.direct_transfer import direct_transfer


def _make_sqlite_engine(db_path: Path):
    return create_engine(f"sqlite:///{db_path.as_posix()}")


def test_direct_transfer_retries_on_transient_insert(tmp_path, monkeypatch):
    """
    Simulate a transient insert error (e.g., deadlock) on the first batch and
    verify direct_transfer retries and completes successfully.
    """
    src_db = tmp_path / "src.db"
    dst_db = tmp_path / "dst.db"

    src_engine = _make_sqlite_engine(src_db)
    dst_engine = _make_sqlite_engine(dst_db)

    meta = MetaData()
    t = Table(
        "foo",
        meta,
        Column("id", Integer, primary_key=True),
        Column("val", String(50)),
    )
    meta.create_all(src_engine)

    # Insert some source rows
    with src_engine.begin() as conn:
        conn.execute(t.insert(), [{"id": i, "val": f"v{i}"} for i in range(10)])

    # Monkeypatch Connection.execute to fail once for INSERTs into 'foo'
    call_state = {"fail_count": 0}
    orig_execute = Connection.execute

    def flaky_execute(self, statement, *args, **kwargs):  # type: ignore[override]
        try:
            is_insert = isinstance(statement, Insert)
            target_table = getattr(statement, "table", None)
            target_name = getattr(target_table, "name", None)
        except Exception:
            is_insert = False
            target_name = None

        if is_insert and target_name == "foo" and call_state["fail_count"] < 1:
            call_state["fail_count"] += 1
            # Raise an OperationalError with a recognizable transient message
            raise OperationalError("insert", {}, Exception("deadlock detected"))
        return orig_execute(self, statement, *args, **kwargs)

    monkeypatch.setattr(Connection, "execute", flaky_execute)

    # Run transfer with small chunk to ensure batching
    direct_transfer(
        source_engine=src_engine,
        dest_engine=dst_engine,
        tables=["foo"],
        source_schema=None,
        dest_schema=None,
        chunk_size=3,
        lowercase_columns=True,
        write_mode="replace",
        row_limit=None,
        max_retries=3,
        backoff_base_seconds=0.01,  # speed up test
        backoff_max_seconds=0.05,
    )

    # Verify all rows copied and that we triggered exactly one transient failure
    with dst_engine.connect() as conn:
        rows = list(conn.execute(t.select()))
    assert len(rows) == 10
    assert call_state["fail_count"] == 1
