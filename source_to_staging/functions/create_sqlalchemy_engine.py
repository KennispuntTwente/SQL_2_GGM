import sys
import logging

from sqlalchemy.engine import URL


def create_sqlalchemy_engine(
    driver: str,
    username: str,
    password: str,
    host: str,
    port: int,
    database: str
) -> URL:
    """
    Create a SQLAlchemy URL for Oracle, PostgreSQL, SQL Server, MySQL or MariaDB,
    based on the given driver name and connection parameters.
    """
    d = driver.lower()

    # Oracle: use service_name query parameter
    if "oracle" in d:
        return URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            query={"service_name": database}
        )

    # PostgreSQL
    elif "postgresql" in d or "postgres" in d:
        return URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database
        )

    # SQL Server (MSSQL)
    elif "mssql" in d or "sqlserver" in d:
        return URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            query={"driver": "ODBC Driver 17 for SQL Server"}
        )

    # MySQL & MariaDB
    elif "mysql" in d or "mariadb" in d:
        return URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            # optional: uncomment to enforce a charset
            # query={"charset": "utf8mb4"}
        )

    else:
        logging.error(f"Unsupported database driver: {driver}")
        sys.exit(1)
