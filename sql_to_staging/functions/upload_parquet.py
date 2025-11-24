"""sql_to_staging-facing wrapper around the shared parquet helpers.

The actual implementation now lives in utils.parquet.upload_parquet so
that other pipelines can depend on it without importing sql_to_staging.
"""

from __future__ import annotations

from utils.parquet.upload_parquet import *  # noqa: F401,F403
