# Tests for get_config_value configuration precedence and value interpretation
# Focuses on INI > ENV > default priority, empty value handling, and type coercion (booleans, lists)
# This ensures correct configuration resolution from multiple sources with proper fallback behavior

import builtins
from configparser import ConfigParser

import pytest

from utils.config.get_config_value import get_config_value, interpret_value


def make_cfg(text: str | None = None) -> ConfigParser:
    cfg = ConfigParser()
    if text:
        cfg.read_string(text)
    return cfg


def test_precedence_ini_over_env_over_default(monkeypatch):
    # ENV and default should be ignored when INI has a non-empty value
    monkeypatch.setenv("HOST", "envhost")
    cfg = make_cfg(
        """
        [database]
        HOST = db.example
        """
    )

    result = get_config_value("HOST", section="database", cfg_parser=cfg, default="defhost")

    assert result == "db.example"


def test_env_used_when_ini_missing(monkeypatch):
    monkeypatch.setenv("HOST", "envhost")
    cfg = make_cfg("""[database]\n# HOST not set\n""")

    result = get_config_value("HOST", section="database", cfg_parser=cfg, default="defhost")

    assert result == "envhost"


def test_env_used_when_ini_present_but_empty(monkeypatch):
    monkeypatch.setenv("HOST", "envhost")
    cfg = make_cfg(
        """
        [database]
        HOST =    
        """
    )

    result = get_config_value("HOST", section="database", cfg_parser=cfg, default="defhost")

    assert result == "envhost"


def test_default_used_when_all_missing(monkeypatch):
    monkeypatch.delenv("HOST", raising=False)
    cfg = make_cfg("""[database]\n# empty section\n""")

    result = get_config_value("HOST", section="database", cfg_parser=cfg, default="defhost")

    assert result == "defhost"


def test_section_prefix_for_env(monkeypatch):
    monkeypatch.setenv("DATABASE_PASSWORD", "s3cr3t")
    # Ensure unprefixed variant would be ignored
    monkeypatch.delenv("PASSWORD", raising=False)
    cfg = make_cfg("""[database]\n# no PASSWORD set\n""")

    result = get_config_value(
        "PASSWORD",
        section="database",
        cfg_parser=cfg,
        default=None,
        section_is_prefix_for_env=True,
    )

    assert result == "s3cr3t"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("true", True),
        ("TrUe", True),
        (" false ", False),
        ("0", False),
        ("1", True),
        ("yes", True),
        ("off", False),
        ("random", "random"),  # unchanged when not boolean-like
        ("  random  ", "  random  "),  # original string preserved
    ],
)
def test_interpret_value(text, expected):
    assert interpret_value(text) == expected


def test_command_line_input_overrides_all(monkeypatch):
    # When ask_in_command_line=True and user types a value, it should be used
    monkeypatch.setenv("HOST", "envhost")
    cfg = make_cfg(
        """
        [database]
        HOST = db.example
        """
    )

    # Simulate user entering a truthy value
    monkeypatch.setattr(builtins, "input", lambda _: " TrUe ")

    result = get_config_value(
        "HOST",
        section="database",
        cfg_parser=cfg,
        default="defhost",
        ask_in_command_line=True,
    )

    assert result is True


def test_command_line_blank_falls_back(monkeypatch):
    # Blank input should fall back to INI/ENV/default order
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.setenv("HOST", "envhost")
    cfg = make_cfg("""[database]\n# HOST not set\n""")
    monkeypatch.setattr(builtins, "input", lambda _: "   ")

    result = get_config_value(
        "HOST",
        section="database",
        cfg_parser=cfg,
        default="defhost",
        ask_in_command_line=True,
    )

    assert result == "envhost"


def test_env_empty_string_is_ignored(monkeypatch):
    monkeypatch.setenv("HOST", "   ")
    cfg = make_cfg("""[database]\n# HOST not set\n""")

    result = get_config_value("HOST", section="database", cfg_parser=cfg, default="defhost")

    assert result == "defhost"


def test_custom_section_ini(monkeypatch):
    monkeypatch.delenv("HOST", raising=False)
    cfg = make_cfg(
        """
        [custom]
        HOST = custom.example
        """
    )

    result = get_config_value("HOST", section="custom", cfg_parser=cfg, default="defhost")

    assert result == "custom.example"
