# Tests for Oracle TNS alias configuration in create_sqlalchemy_engine
# Focuses on verifying correct URL construction for TNS alias vs direct host/port connections
# This ensures Oracle connections work correctly with both TNS naming and EZConnect-style URLs

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine


def test_oracle_engine_uses_dsn_when_tns_alias_flag():
    # Build an engine for oracle using a TNS alias; should place alias into DSN query param
    engine = create_sqlalchemy_engine(
        driver="oracle+oracledb",
        username="u",
        password="p",
        host="MYALIAS",  # alias provided via host
        port=1521,
        database="orclpdb1",
        oracle_tns_alias=True,
    )
    # URL should not contain host/port when using DSN alias
    assert engine.url.host is None
    assert engine.url.port is None
    assert engine.url.query.get("dsn") == "MYALIAS"


def test_oracle_engine_uses_service_name_by_default():
    # Default behavior: use host/port + service_name
    engine = create_sqlalchemy_engine(
        driver="oracle+oracledb",
        username="u",
        password="p",
        host="127.0.0.1",
        port=1521,
        database="orclpdb1",
    )
    assert engine.url.host == "127.0.0.1"
    assert engine.url.port == 1521
    assert engine.url.query.get("service_name") == "orclpdb1"
