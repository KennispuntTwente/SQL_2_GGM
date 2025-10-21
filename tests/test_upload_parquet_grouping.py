from pathlib import Path

import pytest
from dotenv import load_dotenv

from source_to_staging.functions.upload_parquet import (
    _parse_parquet_base_name,
    group_parquet_files,
)


load_dotenv("tests/.env")


def test_parse_parquet_base_name_simple():
    assert _parse_parquet_base_name("client.parquet") == "client"


def test_parse_parquet_base_name_chunked():
    assert _parse_parquet_base_name("client_part0000.parquet") == "client"
    assert _parse_parquet_base_name("client_part0012.parquet") == "client"


def test_parse_parquet_base_name_embedded_part():
    # Should not strip _part in the middle
    assert _parse_parquet_base_name("user_partitions.parquet") == "user_partitions"
    assert _parse_parquet_base_name("user_partitions_part0001.parquet") == "user_partitions"


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
