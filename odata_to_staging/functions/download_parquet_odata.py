import os
import json
import uuid
import logging
import base64
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Set

import polars as pl


logger = logging.getLogger("odata_to_staging.download_parquet")


def _to_jsonable(value: Any) -> Any:
    """Convert OData values to JSON-serializable Python types (no string wrapping).

    This is the inner conversion layer that produces Python dicts/lists
    for nested structures, which can then be JSON-serialized by the caller.
    """
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    # Handle lists
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    # Handle dicts
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    # Handle OData entity proxies or other objects with attributes
    try:
        if hasattr(value, "__dict__"):
            obj_dict = {
                k: _to_jsonable(v)
                for k, v in value.__dict__.items()
                if not k.startswith("_")
            }
            if obj_dict:
                return obj_dict
    except Exception:
        pass
    # Last resort: try str() representation
    try:
        return str(value)
    except Exception:
        return None


def _to_scalar(value: Any) -> Any:
    """Best-effort conversion of OData values to parquet-friendly scalars.

    - Keep None, bool, int, float, str
    - Keep Decimal, UUID (as str)
    - Keep datetime/date
    - Convert time to ISO string
    - Convert timedelta to total seconds (float)
    - Convert bytes to base64 string
    - Lists/dicts (from $expand or complex types) are JSON-serialized to string
    - Other objects (proxies, entity refs) are recursively converted to dict then JSON
    """
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Decimal):
        # Polars inference from python Decimals can be backend/version-dependent;
        # store as string to avoid silent NULLs or object dtypes in parquet.
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    # Handle lists (e.g., from $expand navigation properties returning collections)
    if isinstance(value, (list, tuple)):
        jsonable = [_to_jsonable(item) for item in value]
        return json.dumps(jsonable, default=str, ensure_ascii=False)
    # Handle dicts (e.g., complex types or already-converted entities)
    if isinstance(value, dict):
        jsonable = {k: _to_jsonable(v) for k, v in value.items()}
        return json.dumps(jsonable, default=str, ensure_ascii=False)
    # Handle OData entity proxies or other objects with attributes
    # Try to extract a dict representation for nested/expanded entities
    try:
        # pyodata entity proxies often have a way to get properties
        if hasattr(value, "__dict__"):
            # Filter out private/internal attributes
            obj_dict = {
                k: _to_jsonable(v)
                for k, v in value.__dict__.items()
                if not k.startswith("_")
            }
            if obj_dict:
                return json.dumps(obj_dict, default=str, ensure_ascii=False)
    except Exception:
        pass
    # Last resort: try str() representation
    try:
        return str(value)
    except Exception:
        return None


def _is_v4_client(client: Any) -> bool:
    """Check if client is OData v4 (ODataV4Client) vs pyodata v2.

    OData v4 client has query_entities method, pyodata v2 uses entity_sets attribute.
    """
    return hasattr(client, "query_entities") and hasattr(
        client, "get_entity_properties"
    )


def _entity_properties(
    client: Any, entity_set_name: str, select: Optional[str] = None
) -> List[str]:
    """Return ordered list of properties of an entity set (keys first).

    If select is provided (comma-separated property names from $select),
    only those properties are returned, preserving the order in select.
    Keys are always included first if present in select.
    """
    es = client.schema.entity_set(entity_set_name)
    typ = es.entity_type
    keys = [kp.name for kp in typ.key_proprties]
    # Remaining props (excluding keys) in schema order
    members = [mp.name for mp in typ.proprties() if mp.name not in set(keys)]
    all_props = keys + members

    if select:
        # Parse $select: comma-separated, may contain navigation paths like "Orders/OrderID"
        # We only take top-level property names (before any slash)
        selected_raw = [s.strip() for s in select.split(",") if s.strip()]
        selected_names: List[str] = []
        for s in selected_raw:
            # Handle navigation paths: "Orders/OrderID" -> "Orders"
            prop_name = s.split("/")[0].strip()
            if prop_name and prop_name not in selected_names:
                selected_names.append(prop_name)

        # Keep only those that exist in the entity type
        all_props_set = set(all_props)
        filtered = [p for p in selected_names if p in all_props_set]

        # Ensure keys come first (only those that are in the selection)
        keys_in_select = [k for k in keys if k in filtered]
        others_in_select = [p for p in filtered if p not in keys]
        return keys_in_select + others_in_select

    return all_props


def _rows_from_entities(
    entities: Iterable[Any], props: List[str]
) -> List[Dict[str, Any]]:
    """Convert pyodata v2 entity objects to row dicts."""
    rows: List[Dict[str, Any]] = []
    for ent in entities:
        row: Dict[str, Any] = {}
        for p in props:
            try:
                row[p] = _to_scalar(getattr(ent, p))
            except Exception:
                row[p] = None
        rows.append(row)
    return rows


def _rows_from_dicts(
    entities: List[Dict[str, Any]], props: List[str]
) -> List[Dict[str, Any]]:
    """Convert OData v4 entity dicts to row dicts with scalar conversion.

    OData v4 client returns entities as plain dicts, not proxy objects.
    We still need to apply _to_scalar for consistent data types.
    """
    rows: List[Dict[str, Any]] = []
    for ent in entities:
        row: Dict[str, Any] = {}
        for p in props:
            try:
                row[p] = _to_scalar(ent.get(p))
            except Exception:
                row[p] = None
        rows.append(row)
    return rows


def download_parquet_odata(
    client: Any,
    *,
    entity_sets: List[str],
    output_dir: str = "data",
    page_size: int = 5_000,
    row_limit: Optional[int] = None,
    log_row_count: bool = True,
    per_entity_options: Optional[Dict[str, Dict[str, str]]] = None,
) -> Optional[str]:
    """
    Stream OData entity sets to chunked Parquet files.

    Supports both OData v2 (pyodata) and v4 (ODataV4Client) services.

    - Keeps memory bounded by paging with $top/$skip or following next links
    - Writes part files as {EntitySet}_part0000.parquet, ... in output_dir
    - Emits a manifest JSON with file list and absolute output_dir

    per_entity_options allows providing per-EntitySet overrides like:
      {
        "Employees": {"select": "EmployeeID,LastName", "filter": "Active eq true", "expand": "Orders"}
      }
    """

    os.makedirs(output_dir, exist_ok=True)
    run_id = uuid.uuid4().hex
    created_files: List[str] = []

    # Detect client type once at the start
    is_v4 = _is_v4_client(client)
    if is_v4:
        logger.info("Using OData v4 client for data download")
    else:
        logger.info("Using OData v2 client (pyodata) for data download")

    for es_name in entity_sets:
        logger.info("📥 Dumping OData EntitySet: %s", es_name)

        # Resolve options for this entity set
        opts = (per_entity_options or {}).get(es_name, {})
        select = opts.get("select")
        expand = opts.get("expand")
        filter_txt = opts.get("filter")

        # Validate entity set exists and get properties based on client type
        if is_v4:
            # OData v4 client - uses case-insensitive lookup internally
            try:
                entity_set_names = client.get_entity_set_names()
                # Case-insensitive check for validation message
                entity_set_names_lower = {n.lower(): n for n in entity_set_names}
                if es_name.lower() not in entity_set_names_lower:
                    raise ValueError(
                        f"EntitySet {es_name!r} not found in OData service metadata. "
                        f"Available: {entity_set_names}"
                    )
            except Exception as e:
                if "not found" in str(e):
                    raise
                raise ValueError(
                    f"EntitySet {es_name!r} not found in OData service metadata"
                ) from e

            # Get properties from v4 client (handles case-insensitive matching internally)
            props = client.get_entity_properties(es_name, select=select)
        else:
            # OData v2 client (pyodata)
            try:
                es_proxy = getattr(client.entity_sets, es_name)
            except AttributeError as e:
                raise ValueError(
                    f"EntitySet {es_name!r} not found in OData service metadata"
                ) from e

            # Get properties from v2 client
            props = _entity_properties(client, es_name, select=select)

        # If $expand is specified, add navigation property names to props
        # so that expanded data is captured in the output
        if expand:
            expand_props = [
                e.strip().split("/")[0] for e in expand.split(",") if e.strip()
            ]
            for ep in expand_props:
                if ep not in props:
                    props.append(ep)

        # Optional total count (may be expensive on some services)
        total_count: Optional[int] = None
        if log_row_count:
            if row_limit and row_limit > 0:
                logger.info(
                    "   (row count skipped; ROW_LIMIT is set – using limit instead)"
                )
            else:
                try:
                    if is_v4:
                        total_count = client.count_entities(
                            es_name, filter_expr=filter_txt
                        )
                    else:
                        total_count = es_proxy.get_entities().count().execute()
                    if total_count is not None:
                        logger.info("   (total rows: %s)", f"{total_count:,}")
                    else:
                        logger.info("   (row count not available)")
                except Exception as e:
                    logger.warning("Failed to COUNT() for %s: %s", es_name, e)
        else:
            logger.info("   (row count skipped; LOG_ROW_COUNT disabled)")

        # Determine effective maximum rows for this export
        remaining: Optional[int] = None
        if row_limit and row_limit > 0:
            remaining = row_limit
        elif total_count is not None:
            remaining = total_count

        part_idx = 0
        skip = 0
        wrote_any = False

        # Primary paging using skip/top; additionally follow next links when provided
        next_url: Optional[str] = None
        while True:
            if remaining is None:
                top_n = page_size
            else:
                top_n = min(page_size, remaining)
                if top_n <= 0:
                    break

            # Execute query based on client type
            if is_v4:
                # OData v4 client - use query_entities method
                try:
                    if next_url:
                        # Follow @odata.nextLink for pagination
                        entity_dicts, next_url = client.query_entities_from_url(
                            next_url
                        )
                    else:
                        entity_dicts, next_url = client.query_entities(
                            es_name,
                            select=select,
                            expand=expand,
                            filter_expr=filter_txt,
                            skip=skip,
                            top=top_n,
                        )
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to fetch OData v4 page for {es_name}: {e}"
                    ) from e

                # Convert to rows using dict-based extraction
                rows = _rows_from_dicts(entity_dicts, props)
            else:
                # OData v2 client (pyodata)
                req = es_proxy.get_entities()
                if select:
                    req = req.select(select)
                if expand:
                    req = req.expand(expand)
                if filter_txt:
                    req = req.filter(filter_txt)

                if next_url:
                    # Continue server-driven paging (e.g., $skiptoken)
                    try:
                        req = es_proxy.get_entities().next_url(next_url)  # type: ignore[attr-defined]
                        # Re-apply options to the next_url request in case they're not preserved
                        if select:
                            try:
                                req = req.select(select)
                            except Exception:
                                pass
                        if expand:
                            try:
                                req = req.expand(expand)
                            except Exception:
                                pass
                        if filter_txt:
                            try:
                                req = req.filter(filter_txt)
                            except Exception:
                                pass
                    except Exception as e:
                        # Fallback to skip/top if next_url API not supported
                        logger.debug(
                            "Server-driven paging (next_url) not supported for %s, "
                            "falling back to $skip/$top: %s",
                            es_name,
                            e,
                        )
                        req = es_proxy.get_entities()
                        if select:
                            req = req.select(select)
                        if expand:
                            req = req.expand(expand)
                        if filter_txt:
                            req = req.filter(filter_txt)
                        req = req.skip(skip).top(top_n)
                        next_url = None
                else:
                    req = req.skip(skip).top(top_n)

                try:
                    entities = req.execute()
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to fetch OData v2 page for {es_name}: {e}"
                    ) from e

                # entities may be a ListWithTotalCount with attributes .next_url
                try:
                    next_url = getattr(entities, "next_url", None)
                except Exception:
                    next_url = None

                # Convert to rows using attribute-based extraction
                rows = _rows_from_entities(entities, props)

            if not rows:
                # No items in this page -> stop
                break

            df = pl.DataFrame(rows)
            # Include run_id in filename to avoid conflicts with concurrent runs
            out_path = os.path.join(
                output_dir, f"{es_name}_{run_id}_part{part_idx:04d}.parquet"
            )
            df.write_parquet(out_path)
            created_files.append(os.path.basename(out_path))
            wrote_any = True

            try:
                nrows = len(df)
            except Exception:
                nrows = "?"
            logger.info(
                "✅ OData chunk %s written: %s (%s rows)", part_idx, out_path, nrows
            )

            part_idx += 1
            skip += nrows if isinstance(nrows, int) else top_n
            if remaining is not None and isinstance(nrows, int):
                remaining -= nrows

            # Stop only when an explicit remaining limit is exhausted.
            # Previous logic also stopped when next_url was None AND remaining was None,
            # which truncated downloads for services that expect client-driven $skip/$top paging
            # without advertising a __next link or supporting $count. In that scenario we now
            # continue issuing skip/top requests until an empty page is returned (handled above)
            # or a row_limit is satisfied.
            if remaining is not None and remaining <= 0:
                break

        if not wrote_any:
            logger.info("   (no rows)")

    # Write manifest for this run
    manifest_path = os.path.join(
        output_dir, f".ggmpilot_parquet_manifest_{run_id}.json"
    )
    try:
        manifest = {
            "run_id": run_id,
            "output_dir": os.path.abspath(output_dir),
            "files": created_files,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        logger.info(
            "🧾 Manifest written: %s (%s files)", manifest_path, len(created_files)
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to write OData parquet manifest {manifest_path}: {e}. Aborting to avoid stale file uploads."
        ) from e

    logger.info("🎉 OData export complete – all entity sets written")
    return manifest_path
