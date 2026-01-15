# Tests for OData pagination when $count is not supported by the service
# Focuses on client-driven skip/top pagination with mocked OData responses
# This ensures download_parquet_odata handles services without server-side count

import json
import os
from typing import List

import polars as pl

from odata_to_staging.functions.download_parquet_odata import download_parquet_odata


class MockProp:
    def __init__(self, name: str):
        self.name = name


class MockEntityType:
    def __init__(self, props: List[MockProp], key_names: List[str]):
        self._props = props
        self.key_proprties = [p for p in props if p.name in key_names]

    def proprties(self):  # schema spelling preserved
        return self._props


class MockSchema:
    def __init__(self):
        props = [MockProp("id"), MockProp("value")]
        self._entity_type = MockEntityType(props, ["id"])

    def entity_set(self, name: str):
        return type("ES", (), {"entity_type": self._entity_type})()


class MockEntity:
    def __init__(self, id: int, value: str):
        self.id = id
        self.value = value


class MockRequestBuilder:
    def __init__(self, data: List[MockEntity]):
        self._data = data
        self._skip = 0
        self._top = None

    # Chainable modifiers (ignored for test purposes)
    def select(self, *_):
        return self

    def expand(self, *_):
        return self

    def filter(self, *_):
        return self

    def skip(self, n: int):
        self._skip = n
        return self

    def top(self, n: int):
        self._top = n
        return self

    def count(self):
        # Simulate service that does NOT support $count
        class _Count:
            def execute(self_inner):  # noqa: D401
                raise RuntimeError("$count not supported")

        return _Count()

    def execute(self):
        # Return slice; no next_url attribute (client-driven paging)
        end = len(self._data) if self._top is None else self._skip + self._top
        return self._data[self._skip : end]


class MockEntitySetsAccessor:
    def __init__(self, data_by_name):
        self._data_by_name = data_by_name

    def __getattr__(self, item):
        if item not in self._data_by_name:
            raise AttributeError(item)
        data = self._data_by_name[item]
        # Fresh builder each call so skip/top can be set
        return type(
            "EntitySetProxy",
            (),
            {"get_entities": lambda self_es: MockRequestBuilder(data)},
        )()


class MockClient:
    def __init__(self, entities_by_set):
        self.schema = MockSchema()
        self.entity_sets = MockEntitySetsAccessor(entities_by_set)


def test_download_parquet_odata_pagination_no_count(tmp_path):
    # 5 entities -> with page_size=2 should produce 3 part files (2,2,1)
    entities = [MockEntity(i, f"v{i}") for i in range(5)]
    client = MockClient({"Items": entities})

    manifest_path = download_parquet_odata(
        client,
        entity_sets=["Items"],
        output_dir=str(tmp_path),
        page_size=2,
        row_limit=None,  # no explicit limit
        log_row_count=True,  # will attempt count() and fail
    )

    assert manifest_path is not None
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Expect 3 part files, not truncated at 1
    # Filename pattern is now Items_{run_id}_part####.parquet
    part_files = [
        f for f in manifest["files"] if f.startswith("Items_") and "_part" in f
    ]
    assert len(part_files) == 3, f"Expected 3 part files, got {part_files}"

    # Read back total rows to confirm all 5 exported
    total_rows = 0
    for pf in part_files:
        df = pl.read_parquet(os.path.join(manifest["output_dir"], pf))
        total_rows += len(df)
    assert total_rows == 5
