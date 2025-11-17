import os
from types import SimpleNamespace

import polars as pl

from odata_to_staging.functions.download_parquet_odata import download_parquet_odata


class _Prop:
    def __init__(self, name: str):
        self.name = name


class _EntityType:
    def __init__(self, keys, props):
        self.key_proprties = [_Prop(k) for k in keys]
        self._props = [_Prop(p) for p in props]

    def proprties(self):
        return list(self._props)


class _Schema:
    def __init__(self, mapping):
        self._mapping = mapping

    def entity_set(self, name):
        et = self._mapping[name]
        return SimpleNamespace(entity_type=et)


class _Request:
    def __init__(self, pages_ref, count):
        # pages_ref is a list of pages; execute() will pop from it lazily
        self._pages_ref = pages_ref
        self._count = count
        self._next_url = None

    # Chainable no-ops for select/expand/filter
    def select(self, *_, **__):
        return self

    def expand(self, *_, **__):
        return self

    def filter(self, *_, **__):
        return self

    def skip(self, *_):
        return self

    def top(self, *_):
        return self

    def next_url(self, url):  # emulate API; we won't use in these tests
        self._next_url = url
        return self

    def count(self, inline=False):  # inline ignored here
        class _Count:
            def __init__(self, value):
                self._value = value

            def execute(self):
                return self._value

        return _Count(self._count)

    def execute(self):
        # Lazily consume the next available page when executing
        data = self._pages_ref.pop(0) if self._pages_ref else []
        return list(data)


class _EntitySetProxy:
    def __init__(self, name, pages, total):
        self._name = name
        self._pages = list(pages)
        self._total = total

    def get_entities(self):
        # Return a request bound to the shared pages list; it will consume on execute()
        return _Request(pages_ref=self._pages, count=self._total)


class _Client:
    def __init__(self, schema, entity_sets):
        self.schema = schema
        self.entity_sets = entity_sets


def test_download_empty_entity_set(tmp_path):
    # Schema: Employees(ID key, Name prop)
    et = _EntityType(keys=["ID"], props=["Name"])
    schema = _Schema({"Employees": et})
    # No data pages
    es_proxy = SimpleNamespace(
        Employees=_EntitySetProxy("Employees", pages=[[]], total=0)
    )
    client = _Client(schema=schema, entity_sets=es_proxy)

    out_dir = tmp_path / "data"
    manifest = download_parquet_odata(
        client, entity_sets=["Employees"], output_dir=str(out_dir)
    )
    assert manifest is not None
    # Directory exists but contains only manifest
    files = os.listdir(out_dir)
    assert any(f.startswith(".ggmpilot_parquet_manifest_") for f in files)
    assert not any(f.endswith(".parquet") for f in files)


def test_download_simple_two_rows(tmp_path):
    et = _EntityType(keys=["ID"], props=["Name"])
    schema = _Schema({"Employees": et})

    class E:
        def __init__(self, ID, Name):
            self.ID = ID
            self.Name = Name

    page1 = [E(1, "Alice"), E(2, "Bob")]
    es_proxy = SimpleNamespace(
        Employees=_EntitySetProxy("Employees", pages=[page1], total=2)
    )
    client = _Client(schema=schema, entity_sets=es_proxy)

    out_dir = tmp_path / "data"
    manifest = download_parquet_odata(
        client,
        entity_sets=["Employees"],
        output_dir=str(out_dir),
        page_size=10,
        log_row_count=True,
    )

    assert manifest is not None
    files = sorted([f for f in os.listdir(out_dir) if f.endswith(".parquet")])
    assert files == ["Employees_part0000.parquet"]
    # Basic sanity: file is a valid parquet we can read
    df = pl.read_parquet(out_dir / files[0])
    assert set(df.columns) == {"ID", "Name"}
    assert len(df) == 2
