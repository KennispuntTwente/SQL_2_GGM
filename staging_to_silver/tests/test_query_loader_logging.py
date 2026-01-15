# Tests for query_loader error logging on broken mapping files
# Focuses on verifying syntax errors in custom mappings are logged with file path
# This ensures users get clear error messages when custom query modules fail to import

import logging

from staging_to_silver.functions.query_loader import load_queries


def test_query_loader_logs_mapping_error(tmp_path, caplog):
    """A syntax error in a custom mapping file should be logged instead of silently skipped.

    We create one valid mapping file and one broken file; the broken file should trigger
    an error log mentioning the file path while the valid mapping still loads.
    """
    good = tmp_path / "good.py"
    bad = tmp_path / "bad.py"

    good.write_text(
        "from sqlalchemy import select, literal_column\n\n"
        "def builder(engine):\n"
        "    return select(literal_column('1').label('dummy'))\n\n"
        "__query_exports__ = {'OK_TABLE': builder}\n"
    )

    # Deliberate syntax error: missing closing brace
    bad.write_text("__query_exports__ = {'BROKEN': lambda engine: None\n")

    caplog.set_level(logging.ERROR)
    queries = load_queries(extra_files_or_dirs=[str(tmp_path)], scan_package=False)

    assert "OK_TABLE" in queries, "Valid mapping should still load"
    # Ensure an error log referencing the failed file occurred
    assert any(
        "Failed to import custom mapping file" in rec.message
        and "bad.py" in rec.message
        for rec in caplog.records
    ), "Expected error log for bad.py import failure"
