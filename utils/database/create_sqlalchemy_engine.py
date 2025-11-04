import sys
import logging

from sqlalchemy.engine import URL, Engine
from sqlalchemy import create_engine

from utils.database.initialize_oracle_client import try_init_oracle_client


def create_sqlalchemy_engine(
    driver: str,
    username: str | None,
    password: str | None,
    host: str | None,
    port: int | None,
    database: str | None,
    *,
    mssql_odbc_driver: str | None = None,
    oracle_tns_alias: bool | None = None,
) -> Engine:
    """
    Create a SQLAlchemy Engine for Oracle, PostgreSQL, SQL Server, MySQL or MariaDB,
    based on the given driver name and connection parameters.
    """
    d = driver.lower()

    # Oracle: initialize client if configured; support TNS alias via DSN
    if "oracle" in d:
        # Initialize Oracle Instant Client if configured (no-op otherwise)
        try_init_oracle_client()

        # If configured to use a TNS alias, treat host (or database) as alias name
        if oracle_tns_alias:
            alias_name = host or database
            if not alias_name:
                raise ValueError(
                    "Oracle TNS alias requested, but no alias name provided in host or database"
                )
            return create_engine(
                URL.create(
                    drivername=driver,
                    username=username,
                    password=password,
                    host=None,
                    port=None,
                    query={"dsn": alias_name},
                )
            )
        # Default: use service_name query parameter
        query_params: dict[str, str] = {}
        if database:
            query_params["service_name"] = database
        return create_engine(
            URL.create(
                drivername=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                query=query_params,
            )
        )

    # SQLite (file path or in-memory). Ignores username/host/port parameters.
    if "sqlite" in d:
        # Allow plain "sqlite" or "sqlite+pysqlite" driver strings
        drv = driver if "+" in driver else "sqlite+pysqlite"
        # database can be a file path (relative or absolute) or ":memory:"
        db = database or ""
        # Use 3 slashes for relative/absolute file path, special case for memory
        url = f"{drv}:///:memory:" if db == ":memory:" else f"{drv}:///{db}"
        return create_engine(url)

    # PostgreSQL
    elif "postgresql" in d or "postgres" in d:
        return create_engine(
            URL.create(
                drivername=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                database=database,
            )
        )

    # SQL Server (MSSQL)
    elif "mssql" in d or "sqlserver" in d:
        # Allow overriding the ODBC driver via config (e.g., "ODBC Driver 17 for SQL Server")
        # Default remains Driver 18 if not provided.
        odbc_drv = mssql_odbc_driver or "ODBC Driver 18 for SQL Server"
        return create_engine(
            URL.create(
                drivername=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                database=database,
                # TrustServerCertificate avoids local dev SSL chain issues; acceptable for dev/tests.
                # In production, provide a proper certificate and remove this override if desired.
                query={"driver": odbc_drv, "TrustServerCertificate": "yes"},
            )
        )

    # MySQL & MariaDB
    elif "mysql" in d or "mariadb" in d:
        return create_engine(
            URL.create(
                drivername=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                database=database,
                # optional: uncomment to enforce a charset
                # query={"charset": "utf8mb4"}
            )
        )

    else:
        logging.error(f"Unsupported database driver: {driver}")
        sys.exit(1)
