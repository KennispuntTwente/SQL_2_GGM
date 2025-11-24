# Tests for upload_parquet grouping logic
# Focuses on parsing base names and grouping files by table
# This ensures correct handling of chunked and non-chunked Parquet files

from pathlib import Path

import pytest
from dotenv import load_dotenv

from utils.parquet.upload_parquet import group_parquet_files


load_dotenv("tests/.env")


@pytest.mark.parametrize(
    "names, expected",
    [
        (
            [
                "Client_part0000.parquet",
                "Client_part0001.parquet",
                "Orders_part0000.parquet",
                "user_partitions.parquet",
            ],
            {
                "Client": ["Client_part0000.parquet", "Client_part0001.parquet"],
                "Orders": ["Orders_part0000.parquet"],
                "user_partitions": ["user_partitions.parquet"],
            },
        ),
        (
            [
                "tbl.parquet",
                "tbl_part0009.parquet",
                "tbl_part0010.parquet",
                "tbl_extra.parquet",
            ],
            {
                "tbl": ["tbl.parquet", "tbl_part0009.parquet", "tbl_part0010.parquet"],
                "tbl_extra": ["tbl_extra.parquet"],
            },
        ),
    ],
)
def test_group_parquet_files(tmp_path: Path, names, expected):
    # Create files
    for n in names:
        (tmp_path / n).write_bytes(b"PAR1\x15\x04\x15")
    # Also create a non-parquet file to ensure it's ignored
    (tmp_path / "ignore.txt").write_text("x")

    grouped = group_parquet_files(str(tmp_path))

    # Compare keys and values (lists are sorted by the helper)
    assert set(grouped.keys()) == set(expected.keys())
    for k, v in expected.items():
        assert grouped[k] == v
