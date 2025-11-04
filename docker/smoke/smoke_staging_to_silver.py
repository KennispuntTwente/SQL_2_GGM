import os
import sys
from typing import cast
from sqlalchemy import text

from utils.config.cli_ini_config import load_single_ini_config
from utils.config.get_config_value import get_config_value
from staging_to_silver.functions.engine_loaders import load_destination_engine
from staging_to_silver.functions.query_loader import load_queries


def main():
    # Load single config passed via command line
    args, cfg = load_single_ini_config()

    # Build engine via the same loader used in main.py
    engine = load_destination_engine(cfg)

    source_schema = cast(
        str,
        get_config_value(
            "DST_SCHEMA",
            section="database-destination",
            cfg_parser=cfg,
            default="staging",
        ),
    )
    target_schema = cast(
        str,
        get_config_value(
            "SILVER_SCHEMA", section="settings", cfg_parser=cfg, default="silver"
        ),
    )

    # Ensure we can import the local smoke query module by adding this folder to sys.path
    sys.path.insert(0, os.path.dirname(__file__))

    # Load only our synthetic query by pointing extra_modules to the local smoke module
    queries = load_queries(
        table_name_case="lower",  # silver table is created in lower case (demo_silver)
        column_name_case=None,
        # Note: module file is 'smoke_staging_to_silver__query.py' (double underscore)
        extra_modules=("smoke_staging_to_silver__query",),
        scan_package=False,  # limit to synthetic query only
    )

    # Execute within a single transaction
    with engine.begin() as conn:
        for name, query_fn in queries.items():
            select_stmt = query_fn(engine, source_schema=source_schema)
            # Reflect destination table and preserve column order
            from sqlalchemy import MetaData, Table

            md = MetaData()
            dest_table = Table(
                name,
                md,
                schema=target_schema,
                autoload_with=engine,
                extend_existing=True,
            )
            select_cols = [c.name for c in select_stmt.selected_columns]
            dest_map = {c.name.lower(): c for c in dest_table.columns}
            cols = []
            for col_name in select_cols:
                try:
                    cols.append(dest_table.columns[col_name])
                except KeyError:
                    ci = dest_map.get(col_name.lower())
                    if ci is None:
                        raise KeyError(
                            f"Destination column '{col_name}' not found in {dest_table.fullname}"
                        )
                    cols.append(ci)
            conn.execute(dest_table.insert().from_select(cols, select_stmt))

    # Verify rows were loaded
    with engine.connect() as conn:
        cnt = conn.execute(
            text(f"SELECT COUNT(*) FROM {target_schema}.demo_silver")
        ).scalar()
    print(f"[smoke] Rows in {target_schema}.demo_silver: {cnt}")
    assert cnt and cnt >= 2, "Expected at least two rows in silver.demo_silver"
    print("[smoke] staging_to_silver OK")


if __name__ == "__main__":
    main()
