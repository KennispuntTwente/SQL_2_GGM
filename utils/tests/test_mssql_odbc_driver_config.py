from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine


def test_mssql_engine_uses_default_driver_when_not_overridden():
    engine = create_sqlalchemy_engine(
        driver="mssql+pyodbc",
        username="u",
        password="p",
        host="localhost",
        port=1433,
        database="db",
    )
    # SQLAlchemy URL should include the default ODBC driver in query params
    assert engine.url.query.get("driver") == "ODBC Driver 18 for SQL Server"


def test_mssql_engine_uses_custom_odbc_driver():
    custom = "ODBC Driver 17 for SQL Server"
    engine = create_sqlalchemy_engine(
        driver="mssql+pyodbc",
        username="u",
        password="p",
        host="localhost",
        port=1433,
        database="db",
        mssql_odbc_driver=custom,
    )
    assert engine.url.query.get("driver") == custom
