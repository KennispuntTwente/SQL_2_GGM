# Tests for OData issues fixes:
# 1. $expand/nested values serialization (not dropped)
# 2. $select column filtering (only selected columns in output)
# 3. Pagination edge cases (skiptoken-style services)
# 4. Concurrent file naming (run_id in filenames)

import json
import os
import re
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import polars as pl
import pytest

from odata_to_staging.functions.download_parquet_odata import (
    _to_scalar,
    _entity_properties,
    _rows_from_entities,
    download_parquet_odata,
)


# ============================================================================
# Test fixtures and mock classes
# ============================================================================


class MockProp:
    """Mock property for schema."""

    def __init__(self, name: str):
        self.name = name


class MockEntityType:
    """Mock entity type for schema."""

    def __init__(self, keys: List[str], props: List[str]):
        self.key_proprties = [MockProp(k) for k in keys]
        self._all_props = [MockProp(p) for p in props]

    def proprties(self):
        return list(self._all_props)


class MockSchema:
    """Mock schema for client."""

    def __init__(self, entity_types: Dict[str, MockEntityType]):
        self._entity_types = entity_types

    def entity_set(self, name: str):
        return SimpleNamespace(entity_type=self._entity_types[name])


class MockRequest:
    """Mock request builder that tracks method calls."""

    def __init__(
        self,
        all_data: List[Any],
        total_count: Optional[int] = None,
        supports_count: bool = True,
        supports_next_url: bool = False,
    ):
        self._all_data = all_data  # Flat list of all entities
        self._total_count = total_count
        self._supports_count = supports_count
        self._supports_next_url = supports_next_url
        self._skip = 0
        self._top = None
        self._select = None
        self._expand = None
        self._filter = None

    def select(self, val):
        self._select = val
        return self

    def expand(self, val):
        self._expand = val
        return self

    def filter(self, val):
        self._filter = val
        return self

    def skip(self, n: int):
        self._skip = n
        return self

    def top(self, n: int):
        self._top = n
        return self

    def next_url(self, url: str):
        # Simulate next_url API
        if not self._supports_next_url:
            raise AttributeError("next_url not supported")
        return self

    def count(self):
        class _Count:
            def __init__(inner_self, supports: bool, value: Optional[int]):
                inner_self._supports = supports
                inner_self._value = value

            def execute(inner_self):
                if not inner_self._supports:
                    raise RuntimeError("$count not supported by service")
                return inner_self._value

        return _Count(self._supports_count, self._total_count)

    def execute(self):
        # Use skip/top to return the appropriate slice of data
        start = self._skip
        if self._top is not None:
            end = start + self._top
        else:
            end = len(self._all_data)

        result = self._all_data[start:end]
        return list(result)


class MockEntitySetProxy:
    """Mock entity set proxy."""

    def __init__(
        self,
        all_data: List[Any],
        total_count: Optional[int] = None,
        supports_count: bool = True,
        supports_next_url: bool = False,
    ):
        self._all_data = all_data  # Flat list of all entities
        self._total_count = total_count
        self._supports_count = supports_count
        self._supports_next_url = supports_next_url

    def get_entities(self):
        # Return a fresh request each time (simulating real pyodata behavior)
        return MockRequest(
            self._all_data,
            self._total_count,
            self._supports_count,
            self._supports_next_url,
        )


class MockClient:
    """Mock OData client."""

    def __init__(
        self, schema: MockSchema, entity_set_proxies: Dict[str, MockEntitySetProxy]
    ):
        self.schema = schema
        self.entity_sets = SimpleNamespace(**entity_set_proxies)


# ============================================================================
# Tests for Issue 1: $expand/nested values serialization
# ============================================================================


class TestToScalarNestedValues:
    """Tests that _to_scalar properly serializes nested values instead of dropping them."""

    def test_list_is_json_serialized(self):
        """Lists (from $expand returning collections) should be JSON serialized."""
        nested_list = [{"id": 1, "name": "Order1"}, {"id": 2, "name": "Order2"}]
        result = _to_scalar(nested_list)
        assert result is not None
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["id"] == 1

    def test_dict_is_json_serialized(self):
        """Dicts (complex types or single expanded entities) should be JSON serialized."""
        nested_dict = {"street": "123 Main St", "city": "Springfield"}
        result = _to_scalar(nested_dict)
        assert result is not None
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["street"] == "123 Main St"
        assert parsed["city"] == "Springfield"

    def test_nested_list_of_dicts(self):
        """Deeply nested structures should be fully serialized."""
        nested = [
            {"order_id": 1, "items": [{"sku": "ABC", "qty": 5}]},
            {"order_id": 2, "items": [{"sku": "DEF", "qty": 3}]},
        ]
        result = _to_scalar(nested)
        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["items"][0]["sku"] == "ABC"

    def test_object_with_dict_is_serialized(self):
        """Objects with __dict__ should be converted to JSON."""

        class NestedEntity:
            def __init__(self):
                self.name = "Test"
                self.value = 42
                self._private = "ignored"

        obj = NestedEntity()
        result = _to_scalar(obj)
        assert result is not None
        parsed = json.loads(result)
        assert parsed["name"] == "Test"
        assert parsed["value"] == 42
        assert "_private" not in parsed  # Private attrs filtered

    def test_empty_list_serialized(self):
        """Empty lists should still be serialized, not become None."""
        result = _to_scalar([])
        assert result == "[]"

    def test_empty_dict_serialized(self):
        """Empty dicts should still be serialized, not become None."""
        result = _to_scalar({})
        assert result == "{}"

    def test_primitives_unchanged(self):
        """Primitives should pass through unchanged."""
        assert _to_scalar(None) is None
        assert _to_scalar(True) is True
        assert _to_scalar(42) == 42
        assert _to_scalar(3.14) == 3.14
        assert _to_scalar("hello") == "hello"


# ============================================================================
# Tests for Issue 2: $select column filtering
# ============================================================================


class TestEntityPropertiesWithSelect:
    """Tests that _entity_properties respects $select."""

    def _make_client(self, keys: List[str], props: List[str]) -> MockClient:
        et = MockEntityType(keys=keys, props=props)
        schema = MockSchema({"TestEntity": et})
        return MockClient(schema, {})

    def test_no_select_returns_all_properties(self):
        """Without $select, all properties should be returned."""
        client = self._make_client(keys=["ID"], props=["ID", "Name", "Email", "Age"])
        props = _entity_properties(client, "TestEntity", select=None)
        assert props == ["ID", "Name", "Email", "Age"]

    def test_select_filters_columns(self):
        """With $select, only selected columns should be returned."""
        client = self._make_client(keys=["ID"], props=["ID", "Name", "Email", "Age"])
        props = _entity_properties(client, "TestEntity", select="ID,Name")
        assert set(props) == {"ID", "Name"}

    def test_select_preserves_key_first(self):
        """Keys should come first even when $select is used."""
        client = self._make_client(keys=["ID"], props=["ID", "Name", "Email", "Age"])
        props = _entity_properties(client, "TestEntity", select="Name,ID")
        assert props[0] == "ID"  # Key first
        assert "Name" in props

    def test_select_with_navigation_path(self):
        """$select with navigation paths like 'Orders/OrderID' should use top-level prop."""
        client = self._make_client(keys=["ID"], props=["ID", "Name", "Orders"])
        props = _entity_properties(client, "TestEntity", select="Name,Orders/OrderID")
        assert "Name" in props
        assert "Orders" in props
        assert "Orders/OrderID" not in props

    def test_select_with_nonexistent_prop(self):
        """Properties not in schema should be ignored."""
        client = self._make_client(keys=["ID"], props=["ID", "Name"])
        props = _entity_properties(client, "TestEntity", select="ID,NonExistent,Name")
        assert set(props) == {"ID", "Name"}


class TestSelectIntegration:
    """Integration tests for $select with download_parquet_odata."""

    def test_download_with_select_only_includes_selected_columns(self, tmp_path):
        """When $select is used, output should only contain selected columns."""

        class Entity:
            def __init__(self, ID, Name, Email, Age):
                self.ID = ID
                self.Name = Name
                self.Email = Email
                self.Age = Age

        entities = [Entity(1, "Alice", "alice@test.com", 30)]
        et = MockEntityType(keys=["ID"], props=["ID", "Name", "Email", "Age"])
        schema = MockSchema({"Employees": et})
        es_proxy = MockEntitySetProxy(entities, total_count=1)
        client = MockClient(schema, {"Employees": es_proxy})

        manifest_path = download_parquet_odata(
            client,
            entity_sets=["Employees"],
            output_dir=str(tmp_path),
            page_size=10,
            per_entity_options={"Employees": {"select": "ID,Name"}},
        )

        assert manifest_path is not None
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Read the parquet file
        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        assert len(parquet_files) == 1
        df = pl.read_parquet(os.path.join(tmp_path, parquet_files[0]))

        # Should only have ID and Name columns
        assert set(df.columns) == {"ID", "Name"}
        assert "Email" not in df.columns
        assert "Age" not in df.columns


# ============================================================================
# Tests for Issue 3: Pagination edge cases
# ============================================================================


class TestPaginationModes:
    """Tests for different pagination scenarios."""

    def test_skip_top_pagination_works(self, tmp_path):
        """Standard $skip/$top pagination should work correctly."""

        class Entity:
            def __init__(self, id: int):
                self.id = id

        # 5 entities, page_size=2 -> should produce 3 pages (2+2+1)
        all_entities = [Entity(i) for i in range(5)]

        et = MockEntityType(keys=["id"], props=["id"])
        schema = MockSchema({"Items": et})
        es_proxy = MockEntitySetProxy(
            all_entities,
            total_count=None,
            supports_count=False,
            supports_next_url=False,
        )
        client = MockClient(schema, {"Items": es_proxy})

        manifest_path = download_parquet_odata(
            client,
            entity_sets=["Items"],
            output_dir=str(tmp_path),
            page_size=2,
            log_row_count=True,
        )

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Should have 3 part files (2+2+1 rows)
        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        assert len(parquet_files) == 3

        # Total rows should be 5
        total_rows = 0
        for pf in parquet_files:
            df = pl.read_parquet(os.path.join(tmp_path, pf))
            total_rows += len(df)
        assert total_rows == 5

    def test_pagination_with_row_limit(self, tmp_path):
        """row_limit should stop pagination early."""

        class Entity:
            def __init__(self, id: int):
                self.id = id

        all_entities = [Entity(i) for i in range(100)]

        et = MockEntityType(keys=["id"], props=["id"])
        schema = MockSchema({"Items": et})
        es_proxy = MockEntitySetProxy(all_entities, total_count=100)
        client = MockClient(schema, {"Items": es_proxy})

        manifest_path = download_parquet_odata(
            client,
            entity_sets=["Items"],
            output_dir=str(tmp_path),
            page_size=10,
            row_limit=25,
        )

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Should have stopped after ~25 rows
        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        total_rows = sum(
            len(pl.read_parquet(os.path.join(tmp_path, pf))) for pf in parquet_files
        )
        assert total_rows <= 30  # Allow some flexibility due to chunking


# ============================================================================
# Tests for Issue 4: Concurrent file naming with run_id
# ============================================================================


class TestConcurrentFileNaming:
    """Tests that file naming includes run_id to avoid conflicts."""

    def test_filenames_include_run_id(self, tmp_path):
        """Parquet filenames should include unique run_id."""

        class Entity:
            def __init__(self, id: int):
                self.id = id

        entities = [Entity(1), Entity(2)]
        et = MockEntityType(keys=["id"], props=["id"])
        schema = MockSchema({"Items": et})
        es_proxy = MockEntitySetProxy(entities, total_count=2)
        client = MockClient(schema, {"Items": es_proxy})

        manifest_path = download_parquet_odata(
            client,
            entity_sets=["Items"],
            output_dir=str(tmp_path),
            page_size=10,
        )

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Filename should match pattern: Items_{run_id}_part0000.parquet
        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        assert len(parquet_files) == 1
        filename = parquet_files[0]

        # Pattern: EntitySet_<32-char-hex>_part####.parquet
        pattern = r"^Items_[a-f0-9]{32}_part\d{4}\.parquet$"
        assert re.match(pattern, filename), (
            f"Filename {filename} doesn't match expected pattern"
        )

    def test_concurrent_runs_have_different_run_ids(self, tmp_path):
        """Multiple runs should produce files with different run_ids."""

        class Entity:
            def __init__(self, id: int):
                self.id = id

        entities = [Entity(1)]
        et = MockEntityType(keys=["id"], props=["id"])
        schema = MockSchema({"Items": et})

        run_ids = set()
        for i in range(3):
            # Each run uses fresh mocks
            es_proxy = MockEntitySetProxy(entities, total_count=1)
            client = MockClient(schema, {"Items": es_proxy})

            manifest_path = download_parquet_odata(
                client,
                entity_sets=["Items"],
                output_dir=str(tmp_path),
                page_size=10,
            )

            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            # Extract run_id from manifest
            run_ids.add(manifest["run_id"])

        # All three runs should have different run_ids
        assert len(run_ids) == 3

    def test_concurrent_runs_dont_overwrite_files(self, tmp_path):
        """Multiple runs should create separate files, not overwrite."""

        class Entity:
            def __init__(self, id: int, run: int):
                self.id = id
                self.run = run

        et = MockEntityType(keys=["id"], props=["id", "run"])
        schema = MockSchema({"Items": et})

        manifests = []
        for run_num in range(3):
            entities = [Entity(1, run_num)]
            es_proxy = MockEntitySetProxy(entities, total_count=1)
            client = MockClient(schema, {"Items": es_proxy})

            manifest_path = download_parquet_odata(
                client,
                entity_sets=["Items"],
                output_dir=str(tmp_path),
                page_size=10,
            )
            with open(manifest_path, "r") as f:
                manifests.append(json.load(f))

        # All parquet files should still exist
        all_parquet_files = []
        for m in manifests:
            all_parquet_files.extend(m["files"])

        # Should have 3 separate parquet files
        assert len(all_parquet_files) == 3

        # All files should exist on disk
        for f in all_parquet_files:
            assert os.path.exists(os.path.join(tmp_path, f))


# ============================================================================
# Tests for $expand integration
# ============================================================================


class TestExpandIntegration:
    """Tests for $expand handling."""

    def test_expand_adds_navigation_property_to_columns(self, tmp_path):
        """When $expand is used, navigation property should be in output columns."""

        class Order:
            def __init__(self, order_id: int, amount: float):
                self.order_id = order_id
                self.amount = amount

        class Customer:
            def __init__(self, id: int, name: str, orders: List[Order]):
                self.ID = id
                self.Name = name
                self.Orders = orders  # Expanded navigation property

        customers = [
            Customer(1, "Alice", [Order(101, 50.0), Order(102, 75.0)]),
            Customer(2, "Bob", [Order(201, 100.0)]),
        ]

        et = MockEntityType(keys=["ID"], props=["ID", "Name"])  # Orders is nav prop
        schema = MockSchema({"Customers": et})
        es_proxy = MockEntitySetProxy(customers, total_count=2)
        client = MockClient(schema, {"Customers": es_proxy})

        manifest_path = download_parquet_odata(
            client,
            entity_sets=["Customers"],
            output_dir=str(tmp_path),
            page_size=10,
            per_entity_options={"Customers": {"expand": "Orders"}},
        )

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        df = pl.read_parquet(os.path.join(tmp_path, parquet_files[0]))

        # Orders column should exist
        assert "Orders" in df.columns

        # Orders should be JSON-serialized, not null
        orders_col = df["Orders"].to_list()
        for val in orders_col:
            assert val is not None
            parsed = json.loads(val)
            assert isinstance(parsed, list)

    def test_expand_serializes_nested_entities(self, tmp_path):
        """Expanded entities should be JSON serialized."""

        class Address:
            def __init__(self, street: str, city: str):
                self.street = street
                self.city = city

        class Person:
            def __init__(self, id: int, name: str, address: Address):
                self.ID = id
                self.Name = name
                self.Address = address

        people = [Person(1, "Alice", Address("123 Main", "NYC"))]

        et = MockEntityType(keys=["ID"], props=["ID", "Name"])
        schema = MockSchema({"People": et})
        es_proxy = MockEntitySetProxy(people, total_count=1)
        client = MockClient(schema, {"People": es_proxy})

        manifest_path = download_parquet_odata(
            client,
            entity_sets=["People"],
            output_dir=str(tmp_path),
            page_size=10,
            per_entity_options={"People": {"expand": "Address"}},
        )

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        df = pl.read_parquet(os.path.join(tmp_path, parquet_files[0]))

        # Address should be JSON serialized
        address_val = df["Address"][0]
        assert address_val is not None
        parsed = json.loads(address_val)
        assert parsed["street"] == "123 Main"
        assert parsed["city"] == "NYC"
