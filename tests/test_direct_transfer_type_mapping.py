import pytest
from sqlalchemy import MetaData, Table, Column
from sqlalchemy import types as satypes

# Import the internal helper for focused unit tests
from source_to_staging.functions.direct_transfer import _coerce_generic_type


def _mk_col(name: str, type_):
    meta = MetaData()
    t = Table("t", meta, Column(name, type_))
    return t.c[name]


@pytest.mark.parametrize(
    "src_type, source_dialect, dest_dialect, expected_type_cls, expected_attrs",
    [
        # Oracle NUMBER(1) should be treated as Boolean when source is oracle
        (satypes.Numeric(1, 0), "oracle", "postgresql", satypes.Boolean, {}),
        # Numeric integers map to Integer/Small/Big for generic destinations
        (satypes.Numeric(5, 0), "postgresql", "postgresql", satypes.SmallInteger, {}),
        (satypes.Numeric(10, 0), "postgresql", "postgresql", satypes.Integer, {}),
        (satypes.Numeric(19, 0), "postgresql", "postgresql", satypes.BigInteger, {}),
        # Float preserved generically
        (
            satypes.Float(precision=53),
            "postgresql",
            "postgresql",
            satypes.Float,
            {"precision": 53},
        ),
        # Strings preserve length
        (
            satypes.String(50),
            "postgresql",
            "postgresql",
            satypes.String,
            {"length": 50},
        ),
        (satypes.Text(), "postgresql", "postgresql", satypes.Text, {}),
        # Date/time
        (satypes.Date(), "postgresql", "postgresql", satypes.Date, {}),
        (satypes.DateTime(), "postgresql", "postgresql", satypes.DateTime, {}),
    ],
)
def test_generic_mappings(
    src_type, source_dialect, dest_dialect, expected_type_cls, expected_attrs
):
    col = _mk_col("x", src_type)
    mapped = _coerce_generic_type(col, source_dialect, dest_dialect)
    assert isinstance(mapped, expected_type_cls)
    for k, v in (expected_attrs or {}).items():
        assert getattr(mapped, k) == v


@pytest.mark.parametrize(
    "src_type, expected_repr_contains",
    [
        (satypes.Integer(), "NUMBER"),
        (satypes.SmallInteger(), "NUMBER"),
        (satypes.BigInteger(), "NUMBER"),
        (satypes.Boolean(), "NUMBER"),
        (satypes.Numeric(18, 5), "NUMBER"),
        (satypes.Float(), "BINARY"),  # float should become binary_float/double
        (satypes.String(50), "VARCHAR2"),
        (satypes.Text(), "CLOB"),
    ],
)
def test_oracle_destination_prefers_oracle_types(src_type, expected_repr_contains):
    col = _mk_col("x", src_type)
    mapped = _coerce_generic_type(
        col, source_dialect="postgresql", dest_dialect="oracle"
    )
    rep = repr(mapped).upper()
    assert expected_repr_contains in rep
