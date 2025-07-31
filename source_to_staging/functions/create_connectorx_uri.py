from urllib.parse import quote_plus
from typing import Optional, Mapping


def create_connectorx_uri(
    driver: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    *,
    #—extra knobs taken straight from the docs —
    protocol: Optional[str] = None,          # MySQL / Postgres
    sslmode: Optional[str] = None,           # Postgres
    trusted_connection: bool = False,        # MsSQL
    encrypt: bool = False,                   # MsSQL
    alias: bool = False,                     # Oracle TNS alias
    extra: Optional[Mapping[str, str]] = None,  # any other key=value pairs
) -> str:
    """
    Build a ConnectorX connection‑URI.

    Args:
        driver: A hint such as 'mssql', 'sqlserver', 'mysql', 'oracle', 
                'postgres', 'redshift', or 'sqlite'.
        username/password/host/port/database: familiar pieces of the DSN.
        protocol: 'binary' or 'text' for MySQL; 'binary', 'csv', or 'cursor' for Postgres.
        sslmode: Postgres SSL mode ('require', 'disable', …).
        trusted_connection / encrypt: MS‑SQL specific flags from the docs.
        alias: When True, create an Oracle *TNS alias* URI and append 'alias=true'.
        extra: dict of additional query‑string parameters.

    Returns:
        str – a ready‑to‑pass URI for cx.read_sql().
    """
    drv = driver.lower()

    if "mssql" in drv or "sqlserver" in drv:
        scheme = "mssql"
    elif "mysql" in drv or "mariadb" in drv:
        scheme = "mysql"
    elif "oracle" in drv:
        scheme = "oracle"
    elif "postgres" in drv or "postgresql" in drv:
        scheme = "postgres"
    elif "redshift" in drv:
        scheme = "redshift"
    elif "sqlite" in drv:
        scheme = "sqlite"
    else:
        raise ValueError(f"Unsupported driver: {driver}")

    # SQLite is just the file path after the scheme.
    if scheme == "sqlite":
        return f"sqlite://{database or ''}"

    # credentials part – quote password for safety (esp. MsSQL tip).
    cred = ""
    if username:
        cred = quote_plus(username)
        if password is not None:
            cred += f":{quote_plus(password)}"
        cred += "@"

    # host:port
    netloc = host or ""
    if port:
        netloc += f":{port}"

    # database / service name / alias
    path = database or ""
    query_params: list[str] = []

    # scheme‑specific switches
    if scheme == "mssql":
        if encrypt:
            query_params.append("encrypt=true")
        if trusted_connection:
            query_params.append("trusted_connection=true")
    elif scheme in ("mysql", "postgres"):
        if protocol:
            query_params.append(f"protocol={protocol}")
    if scheme == "postgres" and sslmode:
        query_params.append(f"sslmode={sslmode}")
    if scheme == "oracle" and alias:
        query_params.append("alias=true")

    # arbitrary extras
    if extra:
        query_params.extend([f"{k}={quote_plus(str(v))}" for k, v in extra.items()])

    query_str = f"?{'&'.join(query_params)}" if query_params else ""
    return f"{scheme}://{cred}{netloc}/{path}{query_str}"