"""
Backwards-compat shim for the historical `ggm_dev_server.preprocess_sql`.

Use `dev_sql_server.preprocess_sql` instead.
"""

from __future__ import annotations

from dev_sql_server.preprocess_sql import *  # noqa: F401,F403 re-export
