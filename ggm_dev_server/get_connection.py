"""
Backwards-compat shim for the historical `ggm_dev_server` module.

This package was renamed to `dev_sql_server`.
Please update imports to:

    from dev_sql_server.get_connection import get_connection

The re-export below keeps older notebooks/scripts working, but will be
removed in a future release.
"""

from __future__ import annotations

from dev_sql_server.get_connection import *  # noqa: F401,F403 re-export
import warnings

warnings.warn(
    "ggm_dev_server is deprecated; use dev_sql_server instead",
    DeprecationWarning,
    stacklevel=2,
)
