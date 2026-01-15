"""Tests for OData v4 client using direct HTTP requests.

Uses mocked HTTP responses to verify metadata parsing, entity queries,
pagination handling, and count operations.
"""

import pytest
import requests
from unittest.mock import MagicMock, patch

from odata_to_staging.functions.odata_v4_client import (
    ODataV4Client,
    ODataV4Error,
)


# Sample OData v4 $metadata XML
SAMPLE_METADATA_V4 = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="NorthwindModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="Product">
        <Key>
          <PropertyRef Name="ProductID"/>
        </Key>
        <Property Name="ProductID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="ProductName" Type="Edm.String"/>
        <Property Name="UnitPrice" Type="Edm.Decimal"/>
        <Property Name="UnitsInStock" Type="Edm.Int16"/>
        <NavigationProperty Name="Category" Type="NorthwindModel.Category"/>
      </EntityType>
      <EntityType Name="Category">
        <Key>
          <PropertyRef Name="CategoryID"/>
        </Key>
        <Property Name="CategoryID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="CategoryName" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="NorthwindEntities">
        <EntitySet Name="Products" EntityType="NorthwindModel.Product"/>
        <EntitySet Name="Categories" EntityType="NorthwindModel.Category"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""


class TestODataV4MetadataParsing:
    """Tests for $metadata parsing."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock requests.Session."""
        session = MagicMock(spec=requests.Session)
        return session

    def test_parse_metadata_extracts_entity_sets(self, mock_session):
        """$metadata parsing extracts EntitySet names correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_METADATA_V4
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", mock_session)

        entity_set_names = client.get_entity_set_names()

        assert "Products" in entity_set_names
        assert "Categories" in entity_set_names
        assert len(entity_set_names) == 2

    def test_parse_metadata_extracts_entity_types(self, mock_session):
        """$metadata parsing extracts EntityType definitions correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_METADATA_V4
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", mock_session)

        # Access schema to trigger metadata fetch
        schema = client.schema

        assert "Product" in schema["entity_types"]
        assert "Category" in schema["entity_types"]

        product_type = schema["entity_types"]["Product"]
        assert product_type["keys"] == ["ProductID"]
        assert len(product_type["properties"]) == 4

    def test_get_entity_properties_returns_keys_first(self, mock_session):
        """get_entity_properties returns key properties first."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_METADATA_V4
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", mock_session)

        props = client.get_entity_properties("Products")

        assert props[0] == "ProductID"  # Key should be first
        assert "ProductName" in props
        assert "UnitPrice" in props

    def test_get_entity_properties_with_select(self, mock_session):
        """get_entity_properties filters based on $select."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_METADATA_V4
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response

        client = ODataV4Client("https://example.com/odata/v4", mock_session)

        props = client.get_entity_properties("Products", select="ProductID,ProductName")

        assert props == ["ProductID", "ProductName"]

    def test_metadata_fetch_failure_raises_error(self, mock_session):
        """Failed metadata fetch raises ODataV4Error."""
        mock_session.get.side_effect = requests.ConnectionError("Network error")

        client = ODataV4Client("https://example.com/odata/v4", mock_session)

        with pytest.raises(ODataV4Error) as exc_info:
            _ = client.schema

        assert "Failed to fetch $metadata" in str(exc_info.value)


class TestODataV4EntityQueries:
    """Tests for entity querying."""

    @pytest.fixture
    def client_with_schema(self):
        """Create a client with pre-loaded schema."""
        session = MagicMock(spec=requests.Session)

        # Mock entity query response
        query_response = MagicMock()
        query_response.status_code = 200
        query_response.raise_for_status = MagicMock()
        query_response.json.return_value = {
            "value": [
                {"ProductID": 1, "ProductName": "Chai", "UnitPrice": 18.0},
                {"ProductID": 2, "ProductName": "Chang", "UnitPrice": 19.0},
            ],
            "@odata.nextLink": None,
        }

        session.get.return_value = query_response

        client = ODataV4Client("https://example.com/odata/v4", session)
        # Pre-set schema to avoid metadata fetch
        client._schema = {
            "entity_sets": [
                {"name": "Products", "entity_type": "Product"},
                {"name": "Categories", "entity_type": "Category"},
            ],
            "entity_types": {
                "Product": {
                    "name": "Product",
                    "keys": ["ProductID"],
                    "properties": [
                        {"name": "ProductID", "type": "Edm.Int32", "nullable": False},
                        {"name": "ProductName", "type": "Edm.String", "nullable": True},
                        {"name": "UnitPrice", "type": "Edm.Decimal", "nullable": True},
                    ],
                    "navigation_properties": [],
                },
            },
        }
        return client, session

    def test_query_entities_returns_data_and_next_url(self, client_with_schema):
        """query_entities returns entity list and next URL."""
        client, session = client_with_schema

        entities, next_url = client.query_entities("Products", top=100)

        assert len(entities) == 2
        assert entities[0]["ProductID"] == 1
        assert entities[1]["ProductName"] == "Chang"
        assert next_url is None

    def test_query_entities_with_pagination(self):
        """query_entities handles @odata.nextLink for pagination."""
        session = MagicMock(spec=requests.Session)

        # First page
        page1_response = MagicMock()
        page1_response.status_code = 200
        page1_response.raise_for_status = MagicMock()
        page1_response.json.return_value = {
            "value": [{"ProductID": 1, "ProductName": "Chai"}],
            "@odata.nextLink": "https://example.com/odata/v4/Products?$skiptoken=abc",
        }

        # Second page
        page2_response = MagicMock()
        page2_response.status_code = 200
        page2_response.raise_for_status = MagicMock()
        page2_response.json.return_value = {
            "value": [{"ProductID": 2, "ProductName": "Chang"}],
            "@odata.nextLink": None,
        }

        session.get.side_effect = [page1_response, page2_response]

        client = ODataV4Client("https://example.com/odata/v4", session)
        # Pre-set schema to avoid metadata fetch
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {
                "Product": {
                    "name": "Product",
                    "keys": ["ProductID"],
                    "properties": [
                        {"name": "ProductID", "type": "Edm.Int32", "nullable": False},
                        {"name": "ProductName", "type": "Edm.String", "nullable": True},
                    ],
                    "navigation_properties": [],
                },
            },
        }

        # First query
        entities1, next_url = client.query_entities("Products", top=1)
        assert len(entities1) == 1
        assert next_url is not None

        # Follow next link
        entities2, next_url2 = client.query_entities_from_url(next_url)
        assert len(entities2) == 1
        assert next_url2 is None


class TestODataV4Count:
    """Tests for entity count operations."""

    def test_count_entities_returns_integer(self):
        """count_entities returns integer count."""
        session = MagicMock(spec=requests.Session)

        count_response = MagicMock()
        count_response.status_code = 200
        count_response.text = "42"
        count_response.raise_for_status = MagicMock()

        session.get.return_value = count_response

        client = ODataV4Client("https://example.com/odata/v4", session)
        # Pre-set schema to avoid metadata fetch
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        count = client.count_entities("Products")

        assert count == 42

    def test_count_entities_returns_none_on_error(self):
        """count_entities returns None when count endpoint fails."""
        session = MagicMock(spec=requests.Session)
        session.get.side_effect = requests.ConnectionError("Network error")

        client = ODataV4Client("https://example.com/odata/v4", session)
        client._schema = {
            "entity_sets": [{"name": "Products", "entity_type": "Product"}],
            "entity_types": {"Product": {"keys": [], "properties": []}},
        }

        count = client.count_entities("Products")

        assert count is None


class TestODataV4ClientIntegration:
    """Integration tests combining multiple operations."""

    def test_full_workflow_metadata_and_query(self):
        """Test complete workflow: fetch metadata, query entities."""
        session = MagicMock(spec=requests.Session)

        # Mock metadata
        metadata_response = MagicMock()
        metadata_response.status_code = 200
        metadata_response.text = SAMPLE_METADATA_V4
        metadata_response.raise_for_status = MagicMock()

        # Mock query
        query_response = MagicMock()
        query_response.status_code = 200
        query_response.raise_for_status = MagicMock()
        query_response.json.return_value = {
            "value": [
                {"ProductID": 1, "ProductName": "Chai", "UnitPrice": 18.0, "UnitsInStock": 39},
            ],
        }

        session.get.side_effect = [metadata_response, query_response]

        client = ODataV4Client("https://example.com/odata/v4", session)

        # Get entity sets
        entity_sets = client.get_entity_set_names()
        assert "Products" in entity_sets

        # Get properties
        props = client.get_entity_properties("Products")
        assert "ProductID" in props
        assert "ProductName" in props

        # Query entities
        entities, _ = client.query_entities(
            "Products",
            select="ProductID,ProductName",
            top=10,
        )
        assert len(entities) == 1
        assert entities[0]["ProductName"] == "Chai"
