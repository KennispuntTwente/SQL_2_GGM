# Tests for upload_parquet Parquet file grouping logic
# Focuses on parsing base table names from *_partNNNN.parquet files and grouping by table
# This ensures chunked Parquet files are correctly associated with their source table

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


def test_group_parquet_files_missing_dir(tmp_path: Path):
    missing_dir = tmp_path / "not_created_yet"

    with pytest.raises(RuntimeError, match="Missing path"):
        group_parquet_files(str(missing_dir))
