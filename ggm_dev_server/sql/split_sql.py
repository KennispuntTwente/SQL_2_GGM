import re
from pathlib import Path

def split_sql_schema(input_dir: str = "ggm_db/sql/postgres_correctie", output_dir: str = "ggm_db/sql/postgres_split"):
    input_path = Path(input_dir)
    if not input_path.is_dir():
        raise ValueError(f"Input path '{input_dir}' is not a directory.")

    # Read and combine all SQL files in the folder
    all_sql_text = ""
    for sql_file in sorted(input_path.glob("*.sql")):
        all_sql_text += sql_file.read_text(encoding="utf-8") + "\n"

    # Remove block comments
    all_sql_text = re.sub(r'/\*.*?\*/', '', all_sql_text, flags=re.DOTALL)

    # Split into individual statements
    statements = smart_split_sql(all_sql_text)

    # Categorize statements
    create_tables = []
    alter_constraints = []
    other = []

    for stmt in statements:
        clean_stmt = stmt.strip()
        if not clean_stmt:
            continue
        if clean_stmt.lower().startswith("create table"):
            create_tables.append(clean_stmt + ';')
        elif clean_stmt.lower().startswith("alter table"):
            alter_constraints.append(clean_stmt + ';')
        else:
            other.append(clean_stmt + ';')

    # Create output directory
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # Write categorized SQL
    Path(output / "01_create_tables.sql").write_text(
        "\n\n".join(create_tables + [s for s in other if s.lower().startswith("comment")]), encoding="utf-8"
    )

    Path(output / "02_create_constraints.sql").write_text(
        "\n\n".join(alter_constraints), encoding="utf-8"
    )

    # Optional: handle drop statements
    drops = [s for s in other if s.lower().startswith("drop table")]
    if drops:
        Path(output / "00_drop_tables.sql").write_text(
            "\n\n".join(drops), encoding="utf-8"
        )

    print(f"Split complete. Files written to '{output_dir}'.")

def smart_split_sql(sql_text: str) -> list:
    """Splits SQL into individual statements, ignoring semicolons in comments or strings."""
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False
    in_comment = False

    i = 0
    while i < len(sql_text):
        char = sql_text[i]
        next_char = sql_text[i+1] if i+1 < len(sql_text) else ''

        # Handle line comments --
        if not in_single_quote and not in_double_quote and char == '-' and next_char == '-':
            while i < len(sql_text) and sql_text[i] != '\n':
                current.append(sql_text[i])
                i += 1
            continue

        # Handle block comments /* ... */
        if not in_single_quote and not in_double_quote and char == '/' and next_char == '*':
            in_comment = True
        if in_comment:
            if char == '*' and next_char == '/':
                in_comment = False
                i += 2
                continue
            current.append(char)
            i += 1
            continue

        # Handle string quotes
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote

        # Detect statement end
        if char == ';' and not in_single_quote and not in_double_quote and not in_comment:
            statements.append(''.join(current).strip() + ';')
            current = []
        else:
            current.append(char)

        i += 1

    # Final buffer
    if current:
        tail = ''.join(current).strip()
        if tail:
            statements.append(tail)

    return statements
