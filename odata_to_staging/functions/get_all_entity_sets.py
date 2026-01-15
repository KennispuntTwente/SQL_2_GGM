"""Helper function to query all available entity sets from an OData schema."""

import logging
from typing import Any, List


logger = logging.getLogger("odata_to_staging.get_all_entity_sets")


def get_all_entity_sets(client: Any) -> List[str]:
    """
    Query the OData schema to return a list of all available EntitySet names.

    Args:
        client: pyodata Client instance with loaded schema

    Returns:
        List of EntitySet names available in the service

    Raises:
        RuntimeError: If schema or entity_sets cannot be accessed
    """
    try:
        entity_sets = client.schema.entity_sets
        names = [es.name for es in entity_sets]
        logger.debug("Discovered %d entity sets from schema", len(names))
        return names
    except AttributeError as e:
        raise RuntimeError(
            "Failed to access schema.entity_sets on OData client; "
            "ensure the client is properly initialized"
        ) from e


__all__ = ["get_all_entity_sets"]
