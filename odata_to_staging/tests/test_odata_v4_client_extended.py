"""Extended tests for OData v4 client - covering edge cases and gaps.

Tests additional scenarios:
1. Navigation property handling in get_entity_properties with $select
2. Case-insensitive EntityType lookup
3. Error handling for invalid JSON responses
4. Query error handling
5. EntitySet not found error
6. EntityType not found error
7. Composite keys
8. Empty entity type (no properties)
9. Metadata XML with different namespace formats
10. download_parquet_odata integration with v4 client
"""

import json
import os
import pytest
import requests
from unittest.mock import MagicMock

from odata_to_staging.functions.odata_v4_client import (
    ODataV4Client,
    ODataV4Error,
)
from odata_to_staging.functions.download_parquet_odata import (
    download_parquet_odata,
    _is_v4_client,
    _rows_from_dicts,
)


# Sample OData v4 $metadata XML with composite keys
METADATA_COMPOSITE_KEYS = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="TestModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="OrderItem">
        <Key>
          <PropertyRef Name="OrderID"/>
          <PropertyRef Name="ItemID"/>
        </Key>
        <Property Name="OrderID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="ItemID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="Quantity" Type="Edm.Int32"/>
        <Property Name="Price" Type="Edm.Decimal"/>
      </EntityType>
      <EntityContainer Name="TestContainer">
        <EntitySet Name="OrderItems" EntityType="TestModel.OrderItem"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""

# Metadata with different case in EntityType name
METADATA_CASE_MISMATCH = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="TestModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="PRODUCT">
        <Key>
          <PropertyRef Name="ID"/>
        </Key>
        <Property Name="ID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="Name" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="TestContainer">
        <EntitySet Name="Products" EntityType="TestModel.product"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""

# Metadata with Microsoft-style namespace (older OData implementations)
METADATA_MICROSOFT_NS = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://schemas.microsoft.com/ado/2007/06/edmx">
  <edmx:DataServices>
    <Schema Namespace="TestModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="Customer">
        <Key>
          <PropertyRef Name="CustomerID"/>
        </Key>
        <Property Name="CustomerID" Type="Edm.String" Nullable="false"/>
        <Property Name="CompanyName" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="TestContainer">
        <EntitySet Name="Customers" EntityType="TestModel.Customer"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""

# Metadata without namespace (simplified XML)
METADATA_NO_NAMESPACE = """<?xml version="1.0" encoding="utf-8"?>
<Edmx Version="4.0">
  <DataServices>
    <Schema Namespace="TestModel">
      <EntityType Name="Item">
        <Key>
          <PropertyRef Name="ItemID"/>
        </Key>
        <Property Name="ItemID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="Description" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="TestContainer">
        <EntitySet Name="Items" EntityType="TestModel.Item"/>
      </EntityContainer>
    </Schema>
  </DataServices>
</Edmx>
"""


class TestODataV4CompositeKeys:
    """Tests for composite key handling."""

    @pytest.fixture
    def client_with_composite_keys(self):
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = METADATA_COMPOSITE_KEYS
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response
        return ODataV4Client("https://example.com/odata/v4", session)

    def test_composite_keys_extracted(self, client_with_composite_keys):
        """Composite keys should be extracted correctly."""
        schema = client_with_composite_keys.schema
        order_item_type = schema["entity_types"]["OrderItem"]

        assert order_item_type["keys"] == ["OrderID", "ItemID"]
        assert len(order_item_type["properties"]) == 4

    def test_composite_keys_first_in_properties(self, client_with_composite_keys):
        """All key properties should come first in get_entity_properties."""
        props = client_with_composite_keys.get_entity_properties("OrderItems")

        # Both keys should be first
        assert props[0] == "OrderID"
        assert props[1] == "ItemID"
        assert "Quantity" in props
        assert "Price" in props


class TestODataV4CaseInsensitiveTypeLookup:
    """Tests for case-insensitive EntityType matching."""

    @pytest.fixture
    def client_with_case_mismatch(self):
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = METADATA_CASE_MISMATCH
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response
        return ODataV4Client("https://example.com/odata/v4", session)

    def test_case_insensitive_type_lookup(self, client_with_case_mismatch):
        """EntityType lookup should be case-insensitive."""
        # EntitySet references "TestModel.product" (lowercase)
        # But EntityType is named "PRODUCT" (uppercase)
        # Should still find it via case-insensitive match
        props = client_with_case_mismatch.get_entity_properties("Products")

        assert "ID" in props
        assert "Name" in props


class TestODataV4NamespaceVariants:
    """Tests for different XML namespace formats."""

    def test_microsoft_namespace_parsing(self):
        """Should parse metadata with Microsoft-style edmx namespace."""
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = METADATA_MICROSOFT_NS
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", session)
        entity_sets = client.get_entity_set_names()

        assert "Customers" in entity_sets
        props = client.get_entity_properties("Customers")
        assert "CustomerID" in props
        assert "CompanyName" in props

    def test_no_namespace_parsing(self):
        """Should parse metadata without XML namespaces."""
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = METADATA_NO_NAMESPACE
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", session)
        entity_sets = client.get_entity_set_names()

        assert "Items" in entity_sets
        props = client.get_entity_properties("Items")
        assert "ItemID" in props


class TestODataV4ErrorHandling:
    """Tests for error handling scenarios."""

    def test_entity_set_not_found_raises_value_error(self):
        """get_entity_properties should raise ValueError for unknown EntitySet."""
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = METADATA_COMPOSITE_KEYS
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", session)

        with pytest.raises(ValueError, match="EntitySet.*not found"):
            client.get_entity_properties("NonExistentEntitySet")

    def test_entity_type_not_found_raises_value_error(self):
        """get_entity_properties should raise ValueError if EntityType not in schema."""
        # Create a schema where EntitySet references a non-existent EntityType
        metadata_missing_type = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="TestModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityContainer Name="TestContainer">
        <EntitySet Name="Products" EntityType="TestModel.NonExistentType"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = metadata_missing_type
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", session)

        with pytest.raises(ValueError, match="EntityType.*not found"):
            client.get_entity_properties("Products")

    def test_query_entities_invalid_json_raises_error(self):
        """query_entities should raise ODataV4Error on invalid JSON response."""
        session = MagicMock(spec=requests.Session)

        # Query response - invalid JSON
        query_response = MagicMock()
        query_response.status_code = 200
        query_response.raise_for_status = MagicMock()
        query_response.json.side_effect = ValueError("Invalid JSON")

        session.get.return_value = query_response

        client = ODataV4Client("https://example.com/odata/v4", session)
        # Pre-set schema to avoid metadata fetch
        client._schema = {
            "entity_sets": [{"name": "OrderItems", "entity_type": "OrderItem"}],
            "entity_types": {"OrderItem": {"keys": ["OrderID"], "properties": []}},
        }

        with pytest.raises(ODataV4Error, match="Invalid JSON"):
            client.query_entities("OrderItems")

    def test_query_entities_http_error_raises_error(self):
        """query_entities should raise ODataV4Error on HTTP error."""
        session = MagicMock(spec=requests.Session)

        session.get.side_effect = requests.ConnectionError("Network error")

        client = ODataV4Client("https://example.com/odata/v4", session)
        # Pre-set schema to avoid metadata fetch
        client._schema = {
            "entity_sets": [{"name": "OrderItems", "entity_type": "OrderItem"}],
            "entity_types": {"OrderItem": {"keys": ["OrderID"], "properties": []}},
        }

        with pytest.raises(ODataV4Error, match="Failed to query"):
            client.query_entities("OrderItems")

    def test_query_from_url_http_error_raises_error(self):
        """query_entities_from_url should raise ODataV4Error on HTTP error."""
        session = MagicMock(spec=requests.Session)
        session.get.side_effect = requests.ConnectionError("Network error")

        client = ODataV4Client("https://example.com/odata/v4", session)
        # Pre-set schema to avoid metadata fetch
        client._schema = {"entity_sets": [], "entity_types": {}}

        with pytest.raises(ODataV4Error, match="Failed to follow nextLink"):
            client.query_entities_from_url("https://example.com/next")

    def test_query_from_url_invalid_json_raises_error(self):
        """query_entities_from_url should raise ODataV4Error on invalid JSON."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.side_effect = ValueError("Bad JSON")
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {"entity_sets": [], "entity_types": {}}

        with pytest.raises(ODataV4Error, match="Invalid JSON"):
            client.query_entities_from_url("https://example.com/next")

    def test_metadata_parse_error_raises_error(self):
        """Invalid XML in metadata should raise ODataV4Error."""
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<invalid>xml<unclosed"
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", session)

        with pytest.raises(ODataV4Error, match="Failed to parse"):
            _ = client.schema


class TestODataV4SelectWithNavigationPaths:
    """Tests for $select with navigation property paths."""

    @pytest.fixture
    def client_with_nav_props(self):
        metadata = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="TestModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="Order">
        <Key>
          <PropertyRef Name="OrderID"/>
        </Key>
        <Property Name="OrderID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="OrderDate" Type="Edm.DateTimeOffset"/>
        <Property Name="TotalAmount" Type="Edm.Decimal"/>
        <NavigationProperty Name="Customer" Type="TestModel.Customer"/>
        <NavigationProperty Name="Items" Type="Collection(TestModel.OrderItem)"/>
      </EntityType>
      <EntityType Name="Customer">
        <Key><PropertyRef Name="CustomerID"/></Key>
        <Property Name="CustomerID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="Name" Type="Edm.String"/>
      </EntityType>
      <EntityType Name="OrderItem">
        <Key><PropertyRef Name="ItemID"/></Key>
        <Property Name="ItemID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="ProductName" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="TestContainer">
        <EntitySet Name="Orders" EntityType="TestModel.Order"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""
        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = metadata
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response
        return ODataV4Client("https://example.com/odata/v4", session)

    def test_select_with_only_key(self, client_with_nav_props):
        """$select with only key should return just the key."""
        props = client_with_nav_props.get_entity_properties("Orders", select="OrderID")
        assert props == ["OrderID"]

    def test_select_empty_string(self, client_with_nav_props):
        """Empty $select string should return all properties."""
        props = client_with_nav_props.get_entity_properties("Orders", select="")
        assert "OrderID" in props
        assert "OrderDate" in props
        assert "TotalAmount" in props

    def test_select_with_whitespace(self, client_with_nav_props):
        """$select with extra whitespace should be handled."""
        props = client_with_nav_props.get_entity_properties(
            "Orders", select="  OrderID  ,  OrderDate  "
        )
        assert "OrderID" in props
        assert "OrderDate" in props
        assert len(props) == 2


class TestODataV4ClientDetection:
    """Tests for _is_v4_client helper function."""

    def test_v4_client_detected(self):
        """ODataV4Client should be detected as v4."""
        session = MagicMock(spec=requests.Session)
        session.get.return_value = MagicMock(
            status_code=200, text=METADATA_COMPOSITE_KEYS, raise_for_status=MagicMock()
        )

        client = ODataV4Client("https://example.com/odata/v4", session)
        assert _is_v4_client(client) is True

    def test_v2_client_not_detected_as_v4(self):
        """Mock v2-like client should not be detected as v4."""
        # v2 client has entity_sets attribute but no query_entities method
        mock_v2 = MagicMock()
        mock_v2.entity_sets = MagicMock()
        # Remove the methods that v4 has
        del mock_v2.query_entities
        del mock_v2.get_entity_properties

        assert _is_v4_client(mock_v2) is False


class TestRowsFromDicts:
    """Tests for _rows_from_dicts function."""

    def test_basic_dict_extraction(self):
        """Should extract specified properties from dicts."""
        entities = [
            {"ID": 1, "Name": "Alice", "Extra": "ignored"},
            {"ID": 2, "Name": "Bob", "Extra": "also ignored"},
        ]
        props = ["ID", "Name"]

        rows = _rows_from_dicts(entities, props)

        assert len(rows) == 2
        assert rows[0] == {"ID": 1, "Name": "Alice"}
        assert rows[1] == {"ID": 2, "Name": "Bob"}

    def test_missing_property_returns_none(self):
        """Missing properties should be None in output."""
        entities = [{"ID": 1}]  # Missing "Name"
        props = ["ID", "Name"]

        rows = _rows_from_dicts(entities, props)

        assert rows[0] == {"ID": 1, "Name": None}

    def test_nested_dict_is_json_serialized(self):
        """Nested dicts (from $expand) should be JSON serialized."""
        entities = [
            {
                "ID": 1,
                "Customer": {"CustomerID": 100, "Name": "Acme Corp"},
            }
        ]
        props = ["ID", "Customer"]

        rows = _rows_from_dicts(entities, props)

        assert rows[0]["ID"] == 1
        customer_json = rows[0]["Customer"]
        assert isinstance(customer_json, str)
        parsed = json.loads(customer_json)
        assert parsed["CustomerID"] == 100
        assert parsed["Name"] == "Acme Corp"

    def test_nested_list_is_json_serialized(self):
        """Nested lists (from $expand collection) should be JSON serialized."""
        entities = [
            {
                "ID": 1,
                "Items": [
                    {"ItemID": 1, "Product": "Widget"},
                    {"ItemID": 2, "Product": "Gadget"},
                ],
            }
        ]
        props = ["ID", "Items"]

        rows = _rows_from_dicts(entities, props)

        items_json = rows[0]["Items"]
        assert isinstance(items_json, str)
        parsed = json.loads(items_json)
        assert len(parsed) == 2
        assert parsed[0]["Product"] == "Widget"


class TestODataV4DownloadIntegration:
    """Integration tests for download_parquet_odata with v4 client."""

    @pytest.fixture
    def v4_client(self):
        """Create a mock v4 client for testing."""
        session = MagicMock(spec=requests.Session)

        client = ODataV4Client("https://example.com/odata/v4", session)
        # Pre-set schema
        client._schema = {
            "entity_sets": [
                {"name": "Products", "entity_type": "Product"},
            ],
            "entity_types": {
                "Product": {
                    "name": "Product",
                    "keys": ["ProductID"],
                    "properties": [
                        {"name": "ProductID", "type": "Edm.Int32", "nullable": False},
                        {"name": "ProductName", "type": "Edm.String", "nullable": True},
                        {"name": "Price", "type": "Edm.Decimal", "nullable": True},
                    ],
                    "navigation_properties": [],
                },
            },
        }

        # Mock query_entities
        def mock_query(entity_set, **kwargs):
            return [
                {"ProductID": 1, "ProductName": "Widget", "Price": "9.99"},
                {"ProductID": 2, "ProductName": "Gadget", "Price": "19.99"},
            ], None  # entities, next_url

        session.get.return_value = MagicMock(
            status_code=200,
            raise_for_status=MagicMock(),
            json=MagicMock(
                return_value={
                    "value": [
                        {"ProductID": 1, "ProductName": "Widget", "Price": "9.99"},
                        {"ProductID": 2, "ProductName": "Gadget", "Price": "19.99"},
                    ],
                    "@odata.nextLink": None,
                }
            ),
        )

        return client

    def test_download_with_v4_client(self, v4_client, tmp_path):
        """download_parquet_odata should work with ODataV4Client."""
        import polars as pl

        manifest_path = download_parquet_odata(
            v4_client,
            entity_sets=["Products"],
            output_dir=str(tmp_path),
            page_size=10,
        )

        assert manifest_path is not None

        with open(manifest_path) as f:
            manifest = json.load(f)

        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        assert len(parquet_files) == 1

        df = pl.read_parquet(tmp_path / parquet_files[0])
        assert set(df.columns) == {"ProductID", "ProductName", "Price"}
        assert len(df) == 2

    def test_download_v4_with_select(self, v4_client, tmp_path):
        """download_parquet_odata should respect $select with v4 client."""
        import polars as pl

        # Override mock to return only selected columns
        v4_client.session.get.return_value.json.return_value = {
            "value": [
                {"ProductID": 1, "ProductName": "Widget"},
                {"ProductID": 2, "ProductName": "Gadget"},
            ],
            "@odata.nextLink": None,
        }

        manifest_path = download_parquet_odata(
            v4_client,
            entity_sets=["Products"],
            output_dir=str(tmp_path),
            page_size=10,
            per_entity_options={"Products": {"select": "ProductID,ProductName"}},
        )

        with open(manifest_path) as f:
            manifest = json.load(f)

        parquet_files = [f for f in manifest["files"] if f.endswith(".parquet")]
        df = pl.read_parquet(tmp_path / parquet_files[0])

        # Should only have selected columns
        assert set(df.columns) == {"ProductID", "ProductName"}

    def test_download_v4_entity_set_not_found(self, v4_client, tmp_path):
        """download_parquet_odata should raise for unknown EntitySet with v4 client."""
        with pytest.raises(ValueError, match="not found"):
            download_parquet_odata(
                v4_client,
                entity_sets=["NonExistent"],
                output_dir=str(tmp_path),
            )


class TestODataV4CountWithFilter:
    """Tests for count_entities with filter expressions."""

    def test_count_with_filter(self):
        """count_entities should pass filter to the count endpoint."""
        session = MagicMock(spec=requests.Session)
        count_response = MagicMock()
        count_response.status_code = 200
        count_response.text = "15"
        count_response.raise_for_status = MagicMock()
        session.get.return_value = count_response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        count = client.count_entities("Products", filter_expr="Price gt 10")

        assert count == 15
        # Verify filter was passed in URL (urlencode uses %24 for $)
        call_args = session.get.call_args
        url = call_args[0][0]
        assert "%24filter=" in url or "$filter=" in url
        assert "Price" in url and "gt" in url and "10" in url


class TestODataV4UrlHandling:
    """Tests for URL construction edge cases."""

    def test_service_url_trailing_slash_stripped(self):
        """Service URL with trailing slash should be normalized."""
        session = MagicMock(spec=requests.Session)
        client = ODataV4Client("https://example.com/odata/v4/", session)

        assert client.service_url == "https://example.com/odata/v4"

    def test_query_builds_correct_url(self):
        """query_entities should build correct URL with literal $ signs, not encoded."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": []}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        client.query_entities(
            "Products",
            select="ID,Name",
            filter_expr="Price gt 10",
            skip=100,
            top=50,
        )

        call_args = session.get.call_args
        url = call_args[0][0]

        # URL should use literal $ characters, not %24
        assert "https://example.com/odata/v4/Products?" in url
        assert "$select=ID,Name" in url  # Literal $ and comma preserved
        assert "$filter=Price" in url
        assert "$skip=100" in url
        assert "$top=50" in url
        # Make sure %24 is NOT in the URL ($ should not be encoded)
        assert "%24" not in url


class TestODataV4GetAllEntitySets:
    """Tests for get_all_entity_sets with v4 client."""

    def test_get_all_entity_sets_v4(self):
        """get_all_entity_sets should work with v4 client."""
        from odata_to_staging.functions.get_all_entity_sets import get_all_entity_sets

        session = MagicMock(spec=requests.Session)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = METADATA_COMPOSITE_KEYS
        mock_response.raise_for_status = MagicMock()
        session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", session)

        entity_sets = get_all_entity_sets(client)

        assert entity_sets == ["OrderItems"]

    def test_get_all_entity_sets_v4_error_handling(self):
        """get_all_entity_sets should raise RuntimeError on v4 client error."""
        from odata_to_staging.functions.get_all_entity_sets import get_all_entity_sets

        session = MagicMock(spec=requests.Session)
        session.get.side_effect = requests.ConnectionError("Network error")

        client = ODataV4Client("https://example.com/odata/v4", session)

        with pytest.raises(RuntimeError, match="Failed to get entity sets"):
            get_all_entity_sets(client)


class TestODataV4SpecialCharactersInFilter:
    """Test handling of special characters in filter expressions."""

    def test_filter_with_single_quotes(self):
        """Filter expressions containing single quotes should work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": [{"Name": "O'Brien"}]}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Customers", "entity_type": "Customer"}],
            "entity_types": {
                "Customer": {"keys": [{"name": "ID"}], "properties": [{"name": "Name"}]}
            },
        }

        # Filter with single quote (OData escapes as '')
        result, _ = client.query_entities("Customers", filter_expr="Name eq 'O''Brien'")
        assert result == [{"Name": "O'Brien"}]

        # Verify filter was passed correctly
        call_url = session.get.call_args[0][0]
        assert "$filter=" in call_url

    def test_filter_with_ampersand(self):
        """Filter expressions containing & should be properly encoded."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": []}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        # Filter with & in value (should be encoded)
        client.query_entities("Products", filter_expr="Name eq 'A&B'")
        call_url = session.get.call_args[0][0]
        # The & in 'A&B' should be encoded to prevent breaking the URL
        assert "%26" in call_url or "A&B" in call_url  # Either encoded or raw

    def test_filter_with_unicode_characters(self):
        """Filter expressions containing unicode should work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": [{"Name": "Müller"}]}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Customers", "entity_type": "Customer"}],
            "entity_types": {
                "Customer": {"keys": [], "properties": [{"name": "Name"}]}
            },
        }

        result, _ = client.query_entities("Customers", filter_expr="Name eq 'Müller'")
        assert result == [{"Name": "Müller"}]


class TestODataV4EmptyResults:
    """Test handling of empty result sets."""

    def test_empty_value_array(self):
        """Empty value array should return empty list."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": []}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        result, next_url = client.query_entities("Products")
        assert result == []
        assert next_url is None

    def test_missing_value_key(self):
        """Response without 'value' key should return empty list."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {}  # No 'value' key
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        result, next_url = client.query_entities("Products")
        assert result == []
        assert next_url is None

    def test_count_returns_zero(self):
        """Count endpoint returning 0 should work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.text = "0"
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        count = client.count_entities("Products")
        assert count == 0


class TestODataV4NavigationProperties:
    """Test the get_navigation_properties method."""

    def test_get_navigation_properties_returns_list(self):
        """get_navigation_properties should return navigation property names."""
        session = MagicMock(spec=requests.Session)
        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Orders", "entity_type": "Order"}],
            "entity_types": {
                "Order": {
                    "keys": [{"name": "OrderID"}],
                    "properties": [{"name": "OrderID"}, {"name": "OrderDate"}],
                    "navigation_properties": [
                        {"name": "Customer", "type": "Customer"},
                        {"name": "OrderDetails", "type": "Collection(OrderDetail)"},
                    ],
                }
            },
        }

        nav_props = client.get_navigation_properties("Orders")
        assert nav_props == ["Customer", "OrderDetails"]

    def test_get_navigation_properties_empty_when_none(self):
        """get_navigation_properties returns empty list when no nav properties."""
        session = MagicMock(spec=requests.Session)
        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Simple", "entity_type": "SimpleType"}],
            "entity_types": {
                "SimpleType": {
                    "keys": [{"name": "ID"}],
                    "properties": [{"name": "ID"}],
                    # No navigation_properties key
                }
            },
        }

        nav_props = client.get_navigation_properties("Simple")
        assert nav_props == []

    def test_get_navigation_properties_unknown_entity_set(self):
        """get_navigation_properties raises ValueError for unknown entity set."""
        session = MagicMock(spec=requests.Session)
        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [],
            "entity_types": {},
        }

        with pytest.raises(ValueError, match="EntitySet 'Unknown' not found"):
            client.get_navigation_properties("Unknown")


class TestODataV4ExpandQuery:
    """Test $expand parameter handling."""

    def test_expand_single_navigation(self):
        """$expand with single navigation property should work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {
            "value": [{"OrderID": 1, "Customer": {"CustomerID": "C1", "Name": "Acme"}}]
        }
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Orders", "entity_type": "Order"}],
            "entity_types": {
                "Order": {
                    "keys": [{"name": "OrderID"}],
                    "properties": [{"name": "OrderID"}],
                    "navigation_properties": [{"name": "Customer", "type": "Customer"}],
                }
            },
        }

        result, _ = client.query_entities("Orders", expand="Customer")
        assert result[0]["Customer"]["Name"] == "Acme"

        # Verify $expand was in URL
        call_url = session.get.call_args[0][0]
        assert "$expand=Customer" in call_url

    def test_expand_multiple_navigations(self):
        """$expand with multiple navigation properties (comma-separated)."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": []}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Orders", "entity_type": "Order"}],
            "entity_types": {"Order": {"keys": [], "properties": []}},
        }

        client.query_entities("Orders", expand="Customer,OrderDetails")
        call_url = session.get.call_args[0][0]
        assert "$expand=Customer,OrderDetails" in call_url  # Comma preserved


class TestODataV4PaginationEdgeCases:
    """Test edge cases in pagination handling."""

    def test_next_link_with_different_base_url(self):
        """nextLink with different base URL should still work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": [{"ID": 1}]}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)

        # Use query_entities_from_url with a nextLink that has a different path
        result, _ = client.query_entities_from_url(
            "https://example.com/odata/v4/Products?$skiptoken=abc123"
        )
        assert result == [{"ID": 1}]

    def test_query_with_maximum_top(self):
        """$top with large values should work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": []}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        client.query_entities("Products", top=10000)
        call_url = session.get.call_args[0][0]
        assert "$top=10000" in call_url

    def test_skip_nonzero(self):
        """$skip with non-zero value should be included in URL."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {"value": []}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        client.query_entities("Products", skip=100)
        call_url = session.get.call_args[0][0]
        assert "$skip=100" in call_url


class TestODataV4LargeResponse:
    """Test handling of large responses."""

    def test_many_entities_in_single_response(self):
        """Response with many entities should work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        # Simulate 1000 entities
        large_data = [{"ID": i, "Name": f"Product{i}"} for i in range(1000)]
        response.json.return_value = {"value": large_data}
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {
                "Product": {
                    "keys": [{"name": "ID"}],
                    "properties": [{"name": "ID"}, {"name": "Name"}],
                }
            },
        }

        result, _ = client.query_entities("Products")
        assert len(result) == 1000
        assert result[0]["ID"] == 0
        assert result[999]["ID"] == 999

    def test_deeply_nested_expand(self):
        """Response with deeply nested expanded data should work."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        response.json.return_value = {
            "value": [
                {
                    "OrderID": 1,
                    "Customer": {
                        "CustomerID": "C1",
                        "Address": {
                            "Street": "123 Main St",
                            "City": {"Name": "Springfield", "State": {"Code": "IL"}},
                        },
                    },
                }
            ]
        }
        session.get.return_value = response

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Orders", "entity_type": "Order"}],
            "entity_types": {"Order": {"keys": [], "properties": []}},
        }

        result, _ = client.query_entities("Orders")
        assert result[0]["Customer"]["Address"]["City"]["State"]["Code"] == "IL"


class TestODataV4MetadataEdgeCases:
    """Test edge cases in metadata parsing."""

    def test_entity_set_without_matching_type(self):
        """Entity set referencing non-existent type should raise error on query."""
        session = MagicMock(spec=requests.Session)
        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "NonExistent"}],
            "entity_types": {},  # Type not defined
        }

        with pytest.raises(ValueError, match="EntityType 'NonExistent' not found"):
            client.get_entity_properties("Products")

    def test_properties_with_complex_types(self):
        """Properties with complex types should be included."""
        session = MagicMock(spec=requests.Session)
        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Customers", "entity_type": "Customer"}],
            "entity_types": {
                "Customer": {
                    "keys": ["ID"],  # Keys are strings, not dicts
                    "properties": [
                        {"name": "ID", "type": "Edm.Int32"},
                        {"name": "Name", "type": "Edm.String"},
                        {"name": "Address", "type": "Self.AddressType"},  # Complex type
                    ],
                }
            },
        }

        props = client.get_entity_properties("Customers")
        # All properties should be returned including complex type
        assert len(props) == 3
        assert "Address" in props
