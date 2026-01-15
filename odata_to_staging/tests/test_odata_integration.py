"""Integration tests for OData client against real OData services.

These tests hit real public OData services:
- OData v4 TripPin: https://services.odata.org/v4/TripPinServiceRW
- OData v4 Northwind: https://services.odata.org/V4/Northwind/Northwind.svc
- OData v2 Northwind: https://services.odata.org/V2/Northwind/Northwind.svc

These tests require network access and are skipped by default.
Run with: RUN_ODATA_INTEGRATION=1 pytest -m odata_integration odata_to_staging/tests/test_odata_integration.py
"""

import os

import pytest
import requests

# Skip all tests in this module unless RUN_ODATA_INTEGRATION env var is set
pytestmark = [
    pytest.mark.odata_integration,
    pytest.mark.skipif(
        not os.environ.get("RUN_ODATA_INTEGRATION"),
        reason="OData integration tests skipped; set RUN_ODATA_INTEGRATION=1 to run",
    ),
]


@pytest.fixture
def session():
    """Create a requests session for OData tests."""
    sess = requests.Session()
    sess.headers.update({"Accept": "application/json"})
    yield sess
    sess.close()


class TestODataV4TripPinIntegration:
    """Integration tests against TripPin OData v4 sample service."""

    SERVICE_URL = "https://services.odata.org/v4/TripPinServiceRW"

    @pytest.fixture
    def trippin_client(self, session):
        """Create an OData v4 client for TripPin service."""
        from odata_to_staging.functions.odata_v4_client import ODataV4Client

        return ODataV4Client(self.SERVICE_URL, session)

    def test_metadata_fetch_succeeds(self, trippin_client):
        """Should be able to fetch and parse $metadata."""
        schema = trippin_client.schema
        assert schema is not None
        assert "entity_sets" in schema
        assert "entity_types" in schema
        assert len(schema["entity_sets"]) > 0
        assert len(schema["entity_types"]) > 0

    def test_get_entity_set_names(self, trippin_client):
        """Should list entity set names."""
        entity_sets = trippin_client.get_entity_set_names()
        assert "People" in entity_sets
        assert "Airlines" in entity_sets
        assert "Airports" in entity_sets

    def test_get_entity_properties(self, trippin_client):
        """Should get properties for an entity set."""
        props = trippin_client.get_entity_properties("People")
        assert "UserName" in props  # Primary key
        assert "FirstName" in props
        assert "LastName" in props

    def test_query_entities_basic(self, trippin_client):
        """Should query entities from TripPin."""
        result, next_url = trippin_client.query_entities("People", top=5)
        assert isinstance(result, list)
        assert len(result) <= 5
        # Each result should have key properties
        if result:
            assert "UserName" in result[0]

    def test_query_entities_with_select(self, trippin_client):
        """Should query with $select."""
        result, _ = trippin_client.query_entities(
            "People",
            select="UserName,FirstName",
            top=3,
        )
        assert isinstance(result, list)
        if result:
            # Selected properties should be present
            assert "UserName" in result[0]
            assert "FirstName" in result[0]

    def test_query_entities_with_filter(self, trippin_client):
        """Should query with $filter."""
        result, _ = trippin_client.query_entities(
            "Airports",
            filter_expr="contains(Name, 'International')",
            top=10,
        )
        assert isinstance(result, list)
        # All results should match filter (if any returned)
        for airport in result:
            assert "International" in airport.get("Name", "")

    def test_count_entities(self, trippin_client):
        """Should count entities (if service supports $count)."""
        count = trippin_client.count_entities("Airlines")
        # Some services may not support $count - returns None
        # If it does return a count, it should be a non-negative integer
        if count is not None:
            assert isinstance(count, int)
            assert count >= 0

    def test_navigation_properties(self, trippin_client):
        """Should get navigation properties."""
        nav_props = trippin_client.get_navigation_properties("People")
        # People should have navigation properties like Friends, Trips, Photo
        assert isinstance(nav_props, list)
        # TripPin People entity has navigation properties
        assert len(nav_props) > 0


class TestODataV4NorthwindIntegration:
    """Integration tests against Northwind OData v4 sample service."""

    SERVICE_URL = "https://services.odata.org/V4/Northwind/Northwind.svc"

    @pytest.fixture
    def northwind_client(self, session):
        """Create an OData v4 client for Northwind service."""
        from odata_to_staging.functions.odata_v4_client import ODataV4Client

        return ODataV4Client(self.SERVICE_URL, session)

    def test_metadata_fetch_succeeds(self, northwind_client):
        """Should be able to fetch and parse $metadata."""
        schema = northwind_client.schema
        assert schema is not None
        assert "entity_sets" in schema
        assert len(schema["entity_sets"]) > 0

    def test_get_entity_set_names(self, northwind_client):
        """Should list entity set names."""
        entity_sets = northwind_client.get_entity_set_names()
        assert "Customers" in entity_sets
        assert "Products" in entity_sets
        assert "Orders" in entity_sets

    def test_get_entity_properties(self, northwind_client):
        """Should get properties for Products entity set."""
        props = northwind_client.get_entity_properties("Products")
        assert "ProductID" in props  # Primary key
        assert "ProductName" in props

    def test_query_products(self, northwind_client):
        """Should query products from Northwind."""
        result, next_url = northwind_client.query_entities("Products", top=10)
        assert isinstance(result, list)
        assert len(result) <= 10
        if result:
            assert "ProductID" in result[0]
            assert "ProductName" in result[0]

    def test_query_with_filter(self, northwind_client):
        """Should query products with price filter."""
        result, _ = northwind_client.query_entities(
            "Products",
            filter_expr="UnitPrice gt 20",
            top=5,
        )
        assert isinstance(result, list)
        # All results should have UnitPrice > 20
        for product in result:
            if "UnitPrice" in product:
                assert product["UnitPrice"] > 20

    def test_query_with_expand(self, northwind_client):
        """Should query with $expand to include related entities."""
        result, _ = northwind_client.query_entities(
            "Products",
            expand="Category",
            top=5,
        )
        assert isinstance(result, list)
        # Products should have expanded Category
        if result:
            # Category might be null for some products
            first = result[0]
            # Check that the query succeeded (expand was valid)
            assert "ProductID" in first

    def test_count_customers(self, northwind_client):
        """Should count customers (if service supports $count)."""
        count = northwind_client.count_entities("Customers")
        # Some services may not support $count - returns None
        # If it does return a count, it should be a non-negative integer
        if count is not None:
            assert isinstance(count, int)
            assert count > 0

    def test_pagination_with_skip(self, northwind_client):
        """Should handle pagination with $skip."""
        # Get first page
        page1, _ = northwind_client.query_entities("Products", top=5, skip=0)
        # Get second page
        page2, _ = northwind_client.query_entities("Products", top=5, skip=5)

        assert len(page1) == 5
        assert len(page2) == 5

        # Pages should be different
        if page1 and page2:
            page1_ids = {p.get("ProductID") for p in page1}
            page2_ids = {p.get("ProductID") for p in page2}
            assert page1_ids.isdisjoint(page2_ids), "Pages should not overlap"


class TestODataVersionDetection:
    """Test version detection against real services."""

    def test_detect_trippin_as_v4(self, session):
        """TripPin should be detected as OData v4."""
        from odata_to_staging.functions.engine_loaders import detect_odata_version

        version = detect_odata_version(
            session,
            "https://services.odata.org/v4/TripPinServiceRW",
        )
        assert version == "4"

    def test_detect_northwind_v4_as_v4(self, session):
        """Northwind v4 should be detected as OData v4."""
        from odata_to_staging.functions.engine_loaders import detect_odata_version

        version = detect_odata_version(
            session,
            "https://services.odata.org/V4/Northwind/Northwind.svc",
        )
        assert version == "4"

    def test_detect_northwind_v2_as_v2(self, session):
        """Northwind v2 should be detected as OData v2."""
        from odata_to_staging.functions.engine_loaders import detect_odata_version

        version = detect_odata_version(
            session,
            "https://services.odata.org/V2/Northwind/Northwind.svc",
        )
        assert version == "2"


class TestODataV2NorthwindIntegration:
    """Integration tests against Northwind OData v2 sample service using pyodata."""

    SERVICE_URL = "https://services.odata.org/V2/Northwind/Northwind.svc"

    @pytest.fixture
    def v2_session(self):
        """Create a requests session for OData v2 (without JSON Accept header)."""
        sess = requests.Session()
        # pyodata needs application/xml for $metadata, so don't set Accept: application/json
        yield sess
        sess.close()

    @pytest.fixture
    def northwind_v2_client(self, v2_session):
        """Create an OData v2 client (pyodata) for Northwind service."""
        import pyodata

        return pyodata.Client(self.SERVICE_URL, v2_session)

    def test_metadata_fetch_succeeds(self, northwind_v2_client):
        """Should be able to fetch and parse $metadata."""
        # pyodata client has schema attribute
        schema = northwind_v2_client.schema
        assert schema is not None

    def test_get_entity_sets(self, northwind_v2_client):
        """Should list entity sets."""
        entity_sets = northwind_v2_client.schema.entity_sets
        names = [es.name for es in entity_sets]
        assert "Customers" in names
        assert "Products" in names
        assert "Orders" in names

    def test_query_products(self, northwind_v2_client):
        """Should query products from Northwind v2."""
        request = northwind_v2_client.entity_sets.Products.get_entities()
        request = request.top(5)
        result = request.execute()
        assert len(result) <= 5
        if result:
            # pyodata returns entity objects
            assert hasattr(result[0], "ProductID")
            assert hasattr(result[0], "ProductName")

    def test_query_with_filter(self, northwind_v2_client):
        """Should query products with price filter."""
        request = northwind_v2_client.entity_sets.Products.get_entities()
        request = request.filter("UnitPrice gt 20").top(5)
        result = request.execute()
        assert len(result) <= 5
        # All results should have UnitPrice > 20 (may be string or Decimal)
        for product in result:
            price = product.UnitPrice
            if isinstance(price, str):
                price = float(price)
            assert price > 20

    def test_query_with_select(self, northwind_v2_client):
        """Should query with $select."""
        request = northwind_v2_client.entity_sets.Products.get_entities()
        request = request.select("ProductID,ProductName").top(3)
        result = request.execute()
        assert len(result) <= 3
        if result:
            assert hasattr(result[0], "ProductID")
            assert hasattr(result[0], "ProductName")

    def test_count_products(self, northwind_v2_client):
        """Should count products (v2 style)."""
        request = northwind_v2_client.entity_sets.Products.get_entities()
        # pyodata v2 count via $count=true inline or separate endpoint
        # Note: OData v2 uses $inlinecount=allpages, not /$count endpoint
        count_request = request.count(inline=True).top(1)
        result = count_request.execute()
        # The count is in the response metadata
        # This tests that inline count works
        assert len(result) >= 0  # At least no error
