"""OData v4 client using direct HTTP requests.

This module provides a lightweight OData v4 client without external dependencies.
It uses the requests library (already in use for v2) for all HTTP operations.

OData v4 differs from v2 in several ways:
- Pagination uses @odata.nextLink instead of __next
- Count is requested via $count=true or /$count endpoint
- Metadata uses different XML namespaces (docs.oasis-open.org/odata/ns/edm)
- Response format uses "value" array for entity collections

Example:
    session = requests.Session()
    session.auth = ("user", "password")

    client = ODataV4Client("https://example.com/odata/v4/", session)

    # List all entity sets
    for name in client.get_entity_set_names():
        print(name)

    # Query entities with pagination
    entities, next_url = client.query_entities("Products", top=100)
    while next_url:
        more, next_url = client.query_entities_from_url(next_url)
        entities.extend(more)
"""

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urljoin, quote

import requests

log = logging.getLogger("odata_to_staging.odata_v4_client")


def _build_odata_url(base_url: str, params: Dict[str, str]) -> str:
    """Build OData URL with proper parameter encoding.

    OData uses $ prefix for system query options. While URL-encoding $ to %24
    is technically valid, many OData services expect the literal $ character.
    This function uses safe='$' to avoid encoding the $ prefix.

    Args:
        base_url: Base URL without query parameters
        params: Dict of query parameters (keys should include $ prefix)

    Returns:
        Full URL with properly encoded query string
    """
    if not params:
        return base_url
    # Use safe='$,' to avoid encoding $ (OData param prefix) and , (common in $select)
    query_string = urlencode(params, safe="$,")
    return f"{base_url}?{query_string}"


class ODataV4Error(Exception):
    """Raised when an OData v4 operation fails."""

    pass


class ODataV4Client:
    """OData v4 client using direct HTTP requests.

    This client provides a similar interface to pyodata but for OData v4 services.
    It handles metadata parsing, entity queries, pagination, and counting.

    Attributes:
        service_url: Base URL of the OData v4 service
        session: requests.Session with auth/SSL configuration
    """

    def __init__(self, service_url: str, session: requests.Session):
        """Initialize OData v4 client.

        Args:
            service_url: Base URL of the OData service (without $metadata)
            session: Configured requests.Session with auth, SSL, retries
        """
        self.service_url = service_url.rstrip("/")
        self.session = session
        self._schema: Optional[Dict[str, Any]] = None

    @staticmethod
    def _extract_type_name(full_type: str) -> str:
        """Extract type name from fully-qualified OData type.

        Handles standard "Namespace.TypeName" format as well as bracket-quoted
        identifiers like "[Schema].[Type]" or "Namespace.[Type]".

        Args:
            full_type: Fully-qualified type string (e.g., "Namespace.Type")

        Returns:
            Just the type name portion (without brackets)
        """
        if not full_type:
            return ""

        result: str

        # Handle bracket-quoted identifiers: "[Schema].[Type]" or "Namespace.[Type]"
        # Split on dots that are NOT inside brackets
        # Strategy: find the last segment, which may be bracket-quoted
        if "[" in full_type:
            # Find the last '[' that starts a bracket-quoted identifier
            last_bracket = full_type.rfind("[")
            if last_bracket > 0:
                # Check if there's a dot before the bracket
                if full_type[last_bracket - 1] == ".":
                    result = full_type[last_bracket:]
                    # Strip surrounding brackets if present
                    if result.startswith("[") and result.endswith("]"):
                        return result[1:-1]
                    return result
            # If the whole thing starts with '[', it might be the full type name
            if full_type.startswith("["):
                # Look for pattern like "[Schema].[Type]" - return last bracketed segment
                parts = []
                current = ""
                in_bracket = False
                for char in full_type:
                    if char == "[":
                        in_bracket = True
                        current += char
                    elif char == "]":
                        in_bracket = False
                        current += char
                    elif char == "." and not in_bracket:
                        if current:
                            parts.append(current)
                        current = ""
                    else:
                        current += char
                if current:
                    parts.append(current)
                if parts:
                    result = parts[-1]
                    # Strip surrounding brackets if present
                    if result.startswith("[") and result.endswith("]"):
                        return result[1:-1]
                    return result

        # Standard case: "Namespace.TypeName" -> "TypeName"
        return full_type.split(".")[-1]

    @property
    def schema(self) -> Dict[str, Any]:
        """Lazily load and return schema from $metadata."""
        if self._schema is None:
            self._schema = self._fetch_metadata()
        return self._schema

    def _fetch_metadata(self) -> Dict[str, Any]:
        """Fetch and parse $metadata endpoint.

        Returns:
            Dict with keys:
                - entity_sets: List of EntitySet definitions
                - entity_types: Dict of EntityType definitions (name -> properties)

        Raises:
            ODataV4Error: If metadata fetch or parsing fails
        """
        url = f"{self.service_url}/$metadata"
        log.info("Fetching OData v4 metadata from: %s", url)

        try:
            resp = self.session.get(url, headers={"Accept": "application/xml"})
            resp.raise_for_status()
        except requests.RequestException as e:
            raise ODataV4Error(f"Failed to fetch $metadata from {url}: {e}") from e

        try:
            return self._parse_metadata_xml(resp.text)
        except ET.ParseError as e:
            raise ODataV4Error(f"Failed to parse $metadata XML: {e}") from e

    def _parse_metadata_xml(self, xml_text: str) -> Dict[str, Any]:
        """Parse CSDL XML metadata to extract entity sets and types.

        Supports both OData v4 namespaces and some common variations.

        Args:
            xml_text: Raw XML content from $metadata

        Returns:
            Parsed schema dict with entity_types and entity_sets
        """
        # OData v4 uses these namespaces - try multiple variants for compatibility
        namespace_variants = [
            # Standard OData v4
            {
                "edmx": "http://docs.oasis-open.org/odata/ns/edmx",
                "edm": "http://docs.oasis-open.org/odata/ns/edm",
            },
            # Microsoft variant
            {
                "edmx": "http://schemas.microsoft.com/ado/2007/06/edmx",
                "edm": "http://docs.oasis-open.org/odata/ns/edm",
            },
            # Try without namespace (for simpler XML)
            {"edmx": "", "edm": ""},
        ]

        root = ET.fromstring(xml_text)

        entity_types: Dict[str, Dict[str, Any]] = {}
        entity_sets: List[Dict[str, str]] = []

        # Try each namespace variant
        for ns in namespace_variants:
            # Build namespace prefix for XPath
            ns_map = {k: v for k, v in ns.items() if v}

            # Try to find EntityType elements
            if ns_map:
                et_elements = root.findall(".//edm:EntityType", ns_map)
                es_elements = root.findall(".//edm:EntitySet", ns_map)
            else:
                # No namespace - use local names
                et_elements = [
                    el for el in root.iter() if el.tag.endswith("EntityType")
                ]
                es_elements = [el for el in root.iter() if el.tag.endswith("EntitySet")]

            if et_elements or es_elements:
                # Found elements with this namespace variant
                entity_types = self._parse_entity_types(et_elements, ns_map)
                entity_sets = self._parse_entity_sets(es_elements, ns_map)
                break

        log.info(
            "Parsed %d EntityTypes and %d EntitySets from metadata",
            len(entity_types),
            len(entity_sets),
        )

        return {
            "entity_types": entity_types,
            "entity_sets": entity_sets,
        }

    def _parse_entity_types(
        self, elements: List[ET.Element], ns: Dict[str, str]
    ) -> Dict[str, Dict[str, Any]]:
        """Parse EntityType elements from metadata.

        Args:
            elements: List of EntityType XML elements
            ns: Namespace mapping for XPath

        Returns:
            Dict mapping type name to type definition
        """
        entity_types: Dict[str, Dict[str, Any]] = {}

        for et in elements:
            type_name = et.get("Name")
            if not type_name:
                continue

            properties: List[Dict[str, Any]] = []
            key_names: List[str] = []

            # Get key properties
            if ns:
                key_elem = et.find("edm:Key", ns)
                if key_elem is not None:
                    for prop_ref in key_elem.findall("edm:PropertyRef", ns):
                        key_name = prop_ref.get("Name")
                        if key_name:
                            key_names.append(key_name)
            else:
                # No namespace
                key_elem = next(
                    (child for child in et if child.tag.endswith("Key")), None
                )
                if key_elem is not None:
                    for prop_ref in key_elem:
                        if prop_ref.tag.endswith("PropertyRef"):
                            key_name = prop_ref.get("Name")
                            if key_name:
                                key_names.append(key_name)

            # Get all properties
            if ns:
                prop_elements = et.findall("edm:Property", ns)
            else:
                prop_elements = [
                    child for child in et if child.tag.endswith("Property")
                ]

            for prop in prop_elements:
                prop_name = prop.get("Name")
                if prop_name:
                    properties.append(
                        {
                            "name": prop_name,
                            "type": prop.get("Type", "Edm.String"),
                            "nullable": prop.get("Nullable", "true").lower() == "true",
                        }
                    )

            # Get navigation properties
            if ns:
                nav_elements = et.findall("edm:NavigationProperty", ns)
            else:
                nav_elements = [
                    child for child in et if child.tag.endswith("NavigationProperty")
                ]

            nav_properties: List[Dict[str, Any]] = []
            for nav in nav_elements:
                nav_name = nav.get("Name")
                if nav_name:
                    nav_properties.append(
                        {
                            "name": nav_name,
                            "type": nav.get("Type", ""),
                        }
                    )

            entity_types[type_name] = {
                "name": type_name,
                "keys": key_names,
                "properties": properties,
                "navigation_properties": nav_properties,
            }

        return entity_types

    def _parse_entity_sets(
        self, elements: List[ET.Element], ns: Dict[str, str]
    ) -> List[Dict[str, str]]:
        """Parse EntitySet elements from metadata.

        Args:
            elements: List of EntitySet XML elements
            ns: Namespace mapping for XPath

        Returns:
            List of EntitySet definitions
        """
        entity_sets: List[Dict[str, str]] = []

        for es in elements:
            name = es.get("Name")
            entity_type = es.get("EntityType", "")

            if name:
                # EntityType format may be "Namespace.TypeName", extract just the type name
                # Handle bracket-quoted identifiers like "[Schema].[Type]" or "Namespace.[Type]"
                type_name = self._extract_type_name(entity_type) if entity_type else ""
                entity_sets.append(
                    {
                        "name": name,
                        "entity_type": type_name,
                    }
                )

        return entity_sets

    def get_entity_set_names(self) -> List[str]:
        """Return list of all EntitySet names.

        Returns:
            List of EntitySet names available in the service
        """
        return [es["name"] for es in self.schema["entity_sets"]]

    def _find_entity_set(self, entity_set_name: str) -> Optional[Dict[str, str]]:
        """Find EntitySet by name with case-insensitive fallback.

        Args:
            entity_set_name: Name of the EntitySet to find

        Returns:
            EntitySet dict if found, None otherwise
        """
        # Try exact match first
        entity_set = next(
            (es for es in self.schema["entity_sets"] if es["name"] == entity_set_name),
            None,
        )
        if entity_set:
            return entity_set

        # Try case-insensitive match
        entity_set = next(
            (
                es
                for es in self.schema["entity_sets"]
                if es["name"].lower() == entity_set_name.lower()
            ),
            None,
        )
        return entity_set

    def get_entity_properties(
        self, entity_set_name: str, select: Optional[str] = None
    ) -> List[str]:
        """Return ordered list of properties for an EntitySet (keys first).

        Args:
            entity_set_name: Name of the EntitySet
            select: Optional comma-separated list of properties to filter

        Returns:
            List of property names, with key properties first

        Raises:
            ValueError: If EntitySet or EntityType not found in schema
        """
        # Find the entity set with case-insensitive fallback
        entity_set = self._find_entity_set(entity_set_name)
        if not entity_set:
            raise ValueError(f"EntitySet {entity_set_name!r} not found in schema")

        type_name = entity_set["entity_type"]
        entity_type = self._find_entity_type(type_name)
        if not entity_type:
            raise ValueError(
                f"EntityType {type_name!r} not found in schema for EntitySet {entity_set_name!r}"
            )

        keys = entity_type.get("keys", [])
        all_props = [p["name"] for p in entity_type.get("properties", [])]

        # Order: keys first, then remaining properties
        ordered = list(keys) + [p for p in all_props if p not in keys]

        if select:
            # Filter to only selected properties
            selected = [s.strip() for s in select.split(",") if s.strip()]
            # Keep key properties that are in selection, then others
            keys_in_select = [k for k in keys if k in selected]
            others_in_select = [p for p in selected if p not in keys and p in ordered]
            ordered = keys_in_select + others_in_select

        return ordered

    def _find_entity_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Find EntityType by name with case-insensitive fallback.

        Also handles bracket-quoted names where the type might be stored with
        a full name like '[Schema].[Type]' but we're searching for 'Type'.

        Args:
            type_name: Name of the EntityType to find

        Returns:
            EntityType dict if found, None otherwise
        """
        # Try exact match first
        entity_type = self.schema["entity_types"].get(type_name)
        if entity_type:
            return entity_type

        # Try case-insensitive match
        entity_type = next(
            (
                et
                for name, et in self.schema["entity_types"].items()
                if name.lower() == type_name.lower()
            ),
            None,
        )
        if entity_type:
            return entity_type

        # Try matching against extracted type names (for bracket-quoted full names)
        # e.g., type_name='METADATA' should match stored name='[APICUST].[METADATA]'
        for name, et in self.schema["entity_types"].items():
            extracted_name = self._extract_type_name(name)
            if extracted_name == type_name:
                return et
            if extracted_name.lower() == type_name.lower():
                return et

        return None

    def get_navigation_properties(self, entity_set_name: str) -> List[str]:
        """Return list of navigation property names for an EntitySet.

        Args:
            entity_set_name: Name of the EntitySet

        Returns:
            List of navigation property names

        Raises:
            ValueError: If EntitySet or EntityType not found in schema
        """
        entity_set = self._find_entity_set(entity_set_name)
        if not entity_set:
            raise ValueError(f"EntitySet {entity_set_name!r} not found in schema")

        type_name = entity_set["entity_type"]
        entity_type = self._find_entity_type(type_name)
        if not entity_type:
            raise ValueError(
                f"EntityType {type_name!r} not found in schema for EntitySet {entity_set_name!r}"
            )

        return [np["name"] for np in entity_type.get("navigation_properties", [])]

    def query_entities(
        self,
        entity_set_name: str,
        *,
        select: Optional[str] = None,
        expand: Optional[str] = None,
        filter_expr: Optional[str] = None,
        skip: int = 0,
        top: int = 5000,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Query entities from an EntitySet.

        Args:
            entity_set_name: Name of the EntitySet to query
            select: $select parameter (comma-separated properties)
            expand: $expand parameter (navigation properties)
            filter_expr: $filter expression
            skip: Number of records to skip
            top: Maximum records to return

        Returns:
            Tuple of (list of entity dicts, next_url or None)

        Raises:
            ODataV4Error: If the query fails
        """
        # URL-encode entity set name to handle special characters like brackets
        encoded_name = quote(entity_set_name, safe="")
        base_url = f"{self.service_url}/{encoded_name}"

        params: Dict[str, str] = {}
        if select:
            params["$select"] = select
        if expand:
            params["$expand"] = expand
        if filter_expr:
            params["$filter"] = filter_expr
        if skip > 0:
            params["$skip"] = str(skip)
        if top:
            params["$top"] = str(top)

        url = _build_odata_url(base_url, params)

        log.debug("Querying OData v4: %s", url)

        try:
            resp = self.session.get(
                url,
                headers={
                    "Accept": "application/json",
                    "OData-MaxVersion": "4.0",
                    "OData-Version": "4.0",
                },
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise ODataV4Error(
                f"Failed to query EntitySet {entity_set_name!r}: {e}"
            ) from e

        try:
            data = resp.json()
        except ValueError as e:
            raise ODataV4Error(
                f"Invalid JSON response from EntitySet {entity_set_name!r}: {e}"
            ) from e

        # OData v4 response structure
        entities = data.get("value", [])
        next_url = data.get("@odata.nextLink")

        return entities, next_url

    def query_entities_from_url(
        self, url: str
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Query entities from a full URL (used for pagination with @odata.nextLink).

        Args:
            url: Full URL including any pagination tokens

        Returns:
            Tuple of (list of entity dicts, next_url or None)

        Raises:
            ODataV4Error: If the query fails
        """
        log.debug("Following OData v4 nextLink: %s", url)

        try:
            resp = self.session.get(
                url,
                headers={
                    "Accept": "application/json",
                    "OData-MaxVersion": "4.0",
                    "OData-Version": "4.0",
                },
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise ODataV4Error(f"Failed to follow nextLink: {e}") from e

        try:
            data = resp.json()
        except ValueError as e:
            raise ODataV4Error(f"Invalid JSON response from nextLink: {e}") from e

        entities = data.get("value", [])
        next_url = data.get("@odata.nextLink")

        return entities, next_url

    def count_entities(
        self, entity_set_name: str, filter_expr: Optional[str] = None
    ) -> Optional[int]:
        """Get count of entities in an EntitySet.

        Uses the /$count endpoint which returns a plain integer.

        Args:
            entity_set_name: Name of the EntitySet
            filter_expr: Optional $filter expression

        Returns:
            Count of entities, or None if count not supported by service
        """
        # URL-encode entity set name to handle special characters like brackets
        encoded_name = quote(entity_set_name, safe="")
        base_url = f"{self.service_url}/{encoded_name}/$count"

        params: Dict[str, str] = {}
        if filter_expr:
            params["$filter"] = filter_expr

        url = _build_odata_url(base_url, params)

        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            return int(resp.text.strip())
        except (requests.RequestException, ValueError) as e:
            log.warning("Failed to get count for %s: %s", entity_set_name, e)
            return None


__all__ = ["ODataV4Client", "ODataV4Error"]
