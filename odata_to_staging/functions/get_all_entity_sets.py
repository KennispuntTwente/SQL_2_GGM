"""Helper function to query all available entity sets from an OData schema."""

import logging
from typing import Any, List


logger = logging.getLogger("odata_to_staging.get_all_entity_sets")


def get_all_entity_sets(client: Any) -> List[str]:
    """
    Query the OData schema to return a list of all available EntitySet names.

    Supports both OData v2 (pyodata) and v4 (ODataV4Client) clients.

    Args:
        client: OData client instance (pyodata Client or ODataV4Client)

    Returns:
        List of EntitySet names available in the service

    Raises:
        RuntimeError: If schema or entity_sets cannot be accessed
    """
    # OData v4 client has get_entity_set_names method
    if hasattr(client, "get_entity_set_names"):
        try:
            names = client.get_entity_set_names()
            logger.debug("Discovered %d entity sets from OData v4 schema", len(names))
            return names
        except Exception as e:
            raise RuntimeError(
                f"Failed to get entity sets from OData v4 client: {e}"
            ) from e

    # OData v2 client (pyodata) uses schema.entity_sets
    try:
        entity_sets = client.schema.entity_sets
        names = [es.name for es in entity_sets]
        logger.debug("Discovered %d entity sets from OData v2 schema", len(names))
        return names
    except AttributeError as e:
        raise RuntimeError(
            "Failed to access schema.entity_sets on OData client; "
            "ensure the client is properly initialized"
        ) from e


__all__ = ["get_all_entity_sets"]
