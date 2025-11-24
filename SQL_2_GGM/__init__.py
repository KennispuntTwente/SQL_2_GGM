"""Top-level package for SQL_2_GGM.

This namespace provides access to the pipeline entrypoints and shared utilities
from the SQL_2_GGM project.
"""

from . import odata_to_staging  # noqa: F401
from . import sql_to_staging  # noqa: F401
from . import staging_to_silver  # noqa: F401
from . import synthetic  # noqa: F401
from . import utils  # noqa: F401
