from utils.database.execute_sql_folder import _split_sql_statements


def test_split_oracle_plsql_block_keeps_terminating_semicolon():
    sql = (
        """
        BEGIN
          EXECUTE IMMEDIATE 'DROP TABLE FOO_OR';
        EXCEPTION WHEN OTHERS THEN NULL; END;
        /
        CREATE TABLE FOO_OR(id NUMBER(10) PRIMARY KEY);
        INSERT INTO FOO_OR(id) VALUES (9);
        """
    )
    parts = _split_sql_statements(sql, db_type="oracle")
    # Expect three statements: the anonymous block, CREATE TABLE, and INSERT
    assert len(parts) == 3
    # The PL/SQL block must keep its terminating semicolon after END;
    assert parts[0].strip().endswith("END;")
    # Non-block statements should not end with a semicolon
    assert not parts[1].strip().endswith(";")
    assert not parts[2].strip().endswith(";")
