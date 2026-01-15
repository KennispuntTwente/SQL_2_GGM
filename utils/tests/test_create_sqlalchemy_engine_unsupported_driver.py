# Tests for create_sqlalchemy_engine error handling with unsupported drivers
# Focuses on verifying that unsupported driver names raise clear ValueError exceptions
# This ensures users get actionable error messages instead of cryptic failures

from utils.database.create_sqlalchemy_engine import create_sqlalchemy_engine
import pytest


def test_unsupported_driver_raises_value_error():
    """Ensure unsupported driver name raises ValueError (not SystemExit)."""
    with pytest.raises(ValueError) as exc:
        create_sqlalchemy_engine(
            driver="unknown+driver",
            username="u",
            password="p",
            host="localhost",
            port=1234,
            database="db",
        )
    # Basic assertion on message content
    assert "Unsupported database driver" in str(exc.value)
    assert "unknown+driver" in str(exc.value)
