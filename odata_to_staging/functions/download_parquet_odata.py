import os
import json
import uuid
import logging
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional

import polars as pl


logger = logging.getLogger("odata_to_staging.download_parquet")


def _to_scalar(value: Any) -> Any:
    """Best-effort conversion of OData values to parquet-friendly scalars.

    - Keep None, bool, int, float, str
    - Keep datetime/date
    - For other objects (proxies, nested collections), return None
    """
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (datetime, date)):
        return value
    # Fallback: not a scalar we handle
    return None


def _entity_properties(client: Any, entity_set_name: str) -> List[str]:
    """Return ordered list of properties of an entity set (keys first)."""
    es = client.schema.entity_set(entity_set_name)
    typ = es.entity_type
    keys = [kp.name for kp in typ.key_proprties]
    # Remaining props (excluding keys) in schema order
    members = [mp.name for mp in typ.proprties() if mp.name not in set(keys)]
    return keys + members


def _rows_from_entities(
    entities: Iterable[Any], props: List[str]
) -> List[Dict[str, Any]]:
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
    Stream OData entity sets to chunked Parquet files using pyodata.

    - Keeps memory bounded by paging with $top/$skip or following __next links
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

    for es_name in entity_sets:
        logger.info("📥 Dumping OData EntitySet: %s", es_name)

        # Resolve options for this entity set
        opts = (per_entity_options or {}).get(es_name, {})
        select = opts.get("select")
        expand = opts.get("expand")
        filter_txt = opts.get("filter")

        try:
            es_proxy = getattr(client.entity_sets, es_name)
        except AttributeError as e:
            raise ValueError(
                f"EntitySet {es_name!r} not found in OData service metadata"
            ) from e

        props = _entity_properties(client, es_name)

        # Optional total count (may be expensive on some services)
        total_count: Optional[int] = None
        if log_row_count:
            try:
                total_count = es_proxy.get_entities().count().execute()
                logger.info("   (total rows: %s)", f"{total_count:,}")
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

        # Primary paging using skip/top; additionally follow __next when provided
        next_url: Optional[str] = None
        while True:
            if remaining is None:
                top_n = page_size
            else:
                top_n = min(page_size, remaining)
                if top_n <= 0:
                    break

            req = es_proxy.get_entities()
            if select:
                req = req.select(select)
            if expand:
                req = req.expand(expand)
            if filter_txt:
                req = req.filter(filter_txt)

            if next_url:
                # Continue server-driven paging
                try:
                    req = es_proxy.get_entities().next_url(next_url)  # type: ignore[attr-defined]
                except Exception:
                    # Fallback to skip/top if next_url API not supported
                    req = es_proxy.get_entities().skip(skip).top(top_n)
                    next_url = None
            else:
                req = req.skip(skip).top(top_n)

            try:
                entities = req.execute()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to fetch OData page for {es_name}: {e}"
                ) from e

            # entities may be a ListWithTotalCount with attributes .next_url and is iterable
            try:
                next_url = getattr(entities, "next_url", None)
            except Exception:
                next_url = None

            # Convert current page to rows
            rows = _rows_from_entities(entities, props)
            if not rows:
                # No items in this page -> stop
                break

            df = pl.DataFrame(rows)
            out_path = os.path.join(output_dir, f"{es_name}_part{part_idx:04d}.parquet")
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
