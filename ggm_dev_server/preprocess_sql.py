import re

# one-time compiled regex
_CREATE_TBL_RE = re.compile(
    r"""\bCREATE\s+TABLE\b(?!\s+IF\s+NOT\s+EXISTS)""",
    flags=re.IGNORECASE
)

def preprocess_sql(sql_text: str, db_type: str = "postgres") -> str:
    """
    Return *sql_text* with any   CREATE TABLE   statements made idempotent
    for the given *db_type*.  (Only Postgres needs the tweak so far.)
    """
    
    if db_type.lower() == "postgres":
        return _CREATE_TBL_RE.sub("CREATE TABLE IF NOT EXISTS", sql_text)

    return sql_text   
