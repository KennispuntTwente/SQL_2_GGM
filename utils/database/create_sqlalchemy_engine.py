import sys
import logging

from sqlalchemy.engine import URL, Engine
from sqlalchemy import create_engine


def create_sqlalchemy_engine(
    driver: str, username: str, password: str, host: str, port: int, database: str
) -> Engine:
    """
    Create a SQLAlchemy Engine for Oracle, PostgreSQL, SQL Server, MySQL or MariaDB,
    based on the given driver name and connection parameters.
    """
    d = driver.lower()

    # Oracle: use service_name query parameter
    if "oracle" in d:
        return create_engine(
            URL.create(
                drivername=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                query={"service_name": database},
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
        return create_engine(
            URL.create(
                drivername=driver,
                username=username,
                password=password,
                host=host,
                port=port,
                database=database,
                query={"driver": "ODBC Driver 18 for SQL Server"},
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
