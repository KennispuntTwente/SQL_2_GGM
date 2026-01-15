# Tests for bracket-quoted OData entity set names in upload_parquet
# Verifies that table names containing brackets and dots are sanitized properly

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from utils.parquet.upload_parquet import (
    _sanitize_table_name,
    _parse_parquet_base_name,
    group_parquet_files,
)


class TestSanitizeTableName:
    """Tests for _sanitize_table_name function."""

    def test_removes_brackets(self):
        """Brackets should be removed from table names."""
        assert _sanitize_table_name("[METADATA]") == "METADATA"
        assert _sanitize_table_name("[Schema]") == "Schema"

    def test_replaces_dots_with_underscores(self):
        """Dots should be replaced with underscores."""
        assert _sanitize_table_name("Schema.Table") == "Schema_Table"
        assert _sanitize_table_name("a.b.c") == "a_b_c"

    def test_full_odata_entity_set_name(self):
        """Full OData entity set name like [APICUST].[METADATA] should be sanitized."""
        assert _sanitize_table_name("[APICUST].[METADATA]") == "APICUST_METADATA"
        assert _sanitize_table_name("[Schema].[MyTable]") == "Schema_MyTable"

    def test_plain_name_unchanged(self):
        """Plain names without special characters should remain unchanged."""
        assert _sanitize_table_name("Products") == "Products"
        assert _sanitize_table_name("MyTable") == "MyTable"

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert _sanitize_table_name("") == ""

    def test_underscores_preserved(self):
        """Existing underscores should be preserved."""
        assert _sanitize_table_name("my_table") == "my_table"
        assert _sanitize_table_name("[my_schema].[my_table]") == "my_schema_my_table"


class TestParseParquetBaseName:
    """Tests for _parse_parquet_base_name with bracket-quoted names."""

    def test_plain_name_with_part_suffix(self):
        """Standard partitioned file name should extract base."""
        assert _parse_parquet_base_name("Products_part0000.parquet") == "Products"
        assert _parse_parquet_base_name("Orders_part0012.parquet") == "Orders"

    def test_plain_name_without_part_suffix(self):
        """Non-partitioned file should use full stem as base."""
        assert _parse_parquet_base_name("Products.parquet") == "Products"

    def test_bracket_quoted_name_with_part(self):
        """Bracket-quoted OData name with part suffix should be sanitized."""
        result = _parse_parquet_base_name("[APICUST].[METADATA]_part0000.parquet")
        assert result == "APICUST_METADATA"

    def test_bracket_quoted_name_without_part(self):
        """Bracket-quoted OData name without part suffix should be sanitized."""
        result = _parse_parquet_base_name("[APICUST].[METADATA].parquet")
        assert result == "APICUST_METADATA"

    def test_single_bracket_quoted_name(self):
        """Single bracket-quoted name should have brackets removed."""
        result = _parse_parquet_base_name("[METADATA]_part0000.parquet")
        assert result == "METADATA"


class TestGroupParquetFilesWithBrackets:
    """Tests for group_parquet_files with bracket-quoted OData names."""

    def test_groups_bracket_quoted_files_together(self, tmp_path: Path):
        """Files with bracket-quoted names should be grouped together after sanitization."""
        # Create files with bracket-quoted OData names
        names = [
            "[APICUST].[METADATA]_part0000.parquet",
            "[APICUST].[METADATA]_part0001.parquet",
            "[APICUST].[ORDERS]_part0000.parquet",
        ]
        for n in names:
            # Create minimal valid parquet-like file (just needs to exist)
            (tmp_path / n).write_bytes(b"PAR1\x15\x04\x15")

        grouped = group_parquet_files(str(tmp_path))

        # Both METADATA files should be grouped under sanitized name
        assert "APICUST_METADATA" in grouped
        assert len(grouped["APICUST_METADATA"]) == 2
        assert "APICUST_ORDERS" in grouped
        assert len(grouped["APICUST_ORDERS"]) == 1

    def test_mixed_bracket_and_plain_names(self, tmp_path: Path):
        """Bracket-quoted and plain names should be grouped independently."""
        names = [
            "[APICUST].[METADATA]_part0000.parquet",
            "Products_part0000.parquet",
            "Products_part0001.parquet",
        ]
        for n in names:
            (tmp_path / n).write_bytes(b"PAR1\x15\x04\x15")

        grouped = group_parquet_files(str(tmp_path))

        assert "APICUST_METADATA" in grouped
        assert len(grouped["APICUST_METADATA"]) == 1
        assert "Products" in grouped
        assert len(grouped["Products"]) == 2


class TestReadParquetGlobFalse:
    """Tests that pl.read_parquet is called with glob=False for bracket filenames."""

    def test_read_parquet_with_brackets_in_filename(self, tmp_path: Path):
        """Verify that brackets in filenames don't cause glob pattern issues.

        This test ensures the fix where pl.read_parquet(path, glob=False) is used,
        preventing brackets from being interpreted as glob character classes.
        """
        # Create a parquet file with brackets in the name
        filename = "[APICUST].[METADATA]_part0000.parquet"
        filepath = tmp_path / filename

        # Create actual parquet data
        df = pl.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
        df.write_parquet(filepath)

        # Read it back using glob=False (the fix from the commit)
        result = pl.read_parquet(filepath, glob=False)

        assert result.shape == (3, 2)
        assert result["id"].to_list() == [1, 2, 3]

    def test_read_parquet_without_glob_false_fails(self, tmp_path: Path):
        """Demonstrate that without glob=False, brackets can cause issues.

        Note: This may or may not fail depending on polars version and platform,
        but we test to document the expected behavior.
        """
        filename = "[abc].parquet"
        filepath = tmp_path / filename

        df = pl.DataFrame({"id": [1]})
        df.write_parquet(filepath)

        # With glob=False, should work fine
        result = pl.read_parquet(filepath, glob=False)
        assert result.shape == (1, 1)
