import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from dotenv import load_dotenv

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value
from utils.logging.setup_logging import setup_logging

# Reuse shared destination engine loader and parquet uploader
from odata_to_staging.functions.engine_loaders import load_odata_client
from utils.database.destination_engine import load_destination_engine
from utils.parquet.upload_parquet import upload_parquet

from odata_to_staging.functions.download_parquet_odata import (
    download_parquet_odata,
)


def _collect_entity_options(cfg: Any, entities: List[str]) -> Dict[str, Dict[str, str]]:
    per_entity: Dict[str, Dict[str, str]] = {}
    for es_name in entities:
        es_opts: Dict[str, str] = {}
        # Prefer [odata-export], fallback to legacy [odata-source]
        sel = cast(
            Optional[str],
            get_config_value(
                f"ODATA_SELECT_{es_name}",
                section="odata-export",
                cfg_parser=cfg,
                allow_none_if_cast_fails=True,
            )
            or cast(
                Optional[str],
                get_config_value(
                    f"ODATA_SELECT_{es_name}",
                    section="odata-source",
                    cfg_parser=cfg,
                    allow_none_if_cast_fails=True,
                ),
            ),
        )
        if sel:
            es_opts["select"] = sel
        exp = cast(
            Optional[str],
            get_config_value(
                f"ODATA_EXPAND_{es_name}",
                section="odata-export",
                cfg_parser=cfg,
                allow_none_if_cast_fails=True,
            )
            or cast(
                Optional[str],
                get_config_value(
                    f"ODATA_EXPAND_{es_name}",
                    section="odata-source",
                    cfg_parser=cfg,
                    allow_none_if_cast_fails=True,
                ),
            ),
        )
        if exp:
            es_opts["expand"] = exp
        fil = cast(
            Optional[str],
            get_config_value(
                f"ODATA_FILTER_{es_name}",
                section="odata-export",
                cfg_parser=cfg,
                allow_none_if_cast_fails=True,
            )
            or cast(
                Optional[str],
                get_config_value(
                    f"ODATA_FILTER_{es_name}",
                    section="odata-source",
                    cfg_parser=cfg,
                    allow_none_if_cast_fails=True,
                ),
            ),
        )
        if fil:
            es_opts["filter"] = fil
        if es_opts:
            per_entity[es_name] = es_opts
    return per_entity


def main() -> None:
    module_dir = Path(__file__).resolve().parent
    env_path = module_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.getLogger(__name__).info(
            "Loaded environment variables from %s", env_path
        )

    args, cfg = load_single_ini_config(prog_desc="Run OData to staging data migration")

    setup_logging(app_name="odata_to_staging", cfg_parsers=[cfg])
    log = logging.getLogger("odata_to_staging")
    # Read source entity sets
    entities_str = cast(
        Optional[str],
        get_config_value(
            "ODATA_ENTITY_SETS",
            section="odata-export",
            cfg_parser=cfg,
            allow_none_if_cast_fails=True,
        )
        or cast(
            Optional[str],
            get_config_value(
                "ODATA_ENTITY_SETS",
                section="odata-source",
                cfg_parser=cfg,
                allow_none_if_cast_fails=True,
            ),
        ),
    )
    if not entities_str:
        raise ValueError(
            "ODATA_ENTITY_SETS must be a comma-separated list of EntitySet names"
        )

    raw_entities = [e.strip() for e in entities_str.split(",")]
    entities = [e for e in raw_entities if e]
    if not entities or len(entities) != len(raw_entities):
        raise ValueError(f"ODATA_ENTITY_SETS contains empty items: {entities_str!r}")

    page_size = cast(
        int,
        get_config_value(
            "ODATA_PAGE_SIZE",
            section="odata-network",
            cfg_parser=cfg,
            default=5000,
            cast_type=int,
        ),
    )

    row_limit = cast(
        Optional[int],
        get_config_value(
            "ROW_LIMIT",
            section="settings",
            cfg_parser=cfg,
            cast_type=int,
            allow_none_if_cast_fails=True,
        ),
    )

    log_row_count = cast(
        bool,
        get_config_value(
            "LOG_ROW_COUNT",
            section="settings",
            cfg_parser=cfg,
            default=True,
            cast_type=bool,
        ),
    )

    client = load_odata_client(cfg)
    per_entity = _collect_entity_options(cfg, entities)

    manifest_path = download_parquet_odata(
        client,
        entity_sets=entities,
        output_dir="data",
        page_size=page_size,
        row_limit=row_limit,
        log_row_count=log_row_count,
        per_entity_options=per_entity,
    )

    # Destination engine and upload
    dest_engine = load_destination_engine(cfg)

    write_mode = cast(
        str,
        get_config_value(
            "WRITE_MODE", section="settings", cfg_parser=cfg, default="replace"
        ),
    ).lower()
    if write_mode not in {"replace", "truncate", "append"}:
        raise ValueError(
            f"WRITE_MODE must be one of ['replace','truncate','append']; got {write_mode!r}"
        )

    admin_db_override = cast(
        Optional[str],
        get_config_value(
            "DST_ADMIN_DB", section="database-destination", cfg_parser=cfg
        ),
    )

    upload_parquet(
        dest_engine,
        schema=get_config_value(
            "DST_SCHEMA", section="database-destination", cfg_parser=cfg
        ),
        input_dir="data",
        cleanup=cast(
            bool,
            get_config_value(
                "CLEANUP_PARQUET_FILES",
                section="settings",
                cfg_parser=cfg,
                default=True,
                cast_type=bool,
            ),
        ),
        manifest_path=manifest_path,
        write_mode=write_mode,
        admin_database=admin_db_override,
        # Normalize table names to lower-case in staging (configurable; default True)
        lower_table_names=cast(
            bool,
            get_config_value(
                "LOWER_TABLE_NAMES",
                section="settings",
                cfg_parser=cfg,
                default=True,
                cast_type=bool,
            ),
        ),
    )


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
