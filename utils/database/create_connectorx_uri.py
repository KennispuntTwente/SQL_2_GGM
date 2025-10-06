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
    protocol: Optional[str] = None,      # MySQL / Postgres
    sslmode: Optional[str] = None,        # Postgres
    trusted_connection: bool = False,     # MsSQL
    encrypt: bool = False,                # MsSQL
    alias: bool = False,                  # Oracle TNS alias/DNS
    extra: Optional[Mapping[str, str]] = None,  # any other key=value pairs
) -> str:
    """
    Build a ConnectorX connection-URI.
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

    # credentials part – quote for safety.
    cred = ""
    if username:
        cred = quote_plus(username)
        if password is not None:
            cred += f":{quote_plus(password)}"
        cred += "@"

    # collect query params as (k, v) pairs to preserve order
    query_params: list[tuple[str, str]] = []

    # scheme-specific switches
    if scheme == "mssql":
        if encrypt:
            query_params.append(("encrypt", "true"))
        if trusted_connection:
            query_params.append(("trusted_connection", "true"))
    elif scheme in ("mysql", "postgres"):
        if protocol:
            query_params.append(("protocol", protocol))
    if scheme == "postgres" and sslmode:
        query_params.append(("sslmode", sslmode))

    # append arbitrary extras (before hard-coded flags so flags take precedence)
    if extra:
        for k, v in extra.items():
            query_params.append((k, str(v)))

    def build_query(pairs: list[tuple[str, str]]) -> str:
        if not pairs:
            return ""
        return "?" + "&".join(f"{k}={quote_plus(v)}" for k, v in pairs)

    # ORACLE alias form
    if scheme == "oracle" and alias:
        alias_name = host or database
        if not alias_name:
            raise ValueError("For Oracle alias URIs, provide alias name via `host` or `database`.")
        # ensure alias=true is present (and wins)
        query_params = [(k, v) for k, v in query_params if k.lower() != "alias"]
        query_params.append(("alias", "true"))
        return f"oracle://{cred}{alias_name}{build_query(query_params)}"

    # Generic (and Oracle non-alias) host:port + /database path
    netloc = host or ""
    if port:
        netloc += f":{port}"
    path = database or ""

    return f"{scheme}://{cred}{netloc}/{path}{build_query(query_params)}"
