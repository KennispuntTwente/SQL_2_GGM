import logging
import os
import configparser
from pathlib import Path

from utils.logging.setup_logging import setup_logging


def reset_logging():
    root = logging.getLogger()
    for h in list(root.handlers):
        if getattr(h, "_ggmpilot_managed", False):
            try:
                h.flush()
            except Exception:
                pass
            try:
                h.close()
            except Exception:
                pass
            root.removeHandler(h)
    logging.shutdown()


def test_setup_logging_adds_console_handler(caplog):
    reset_logging()
    caplog.set_level(logging.INFO)

    setup_logging(app_name="unit-test", cfg_parsers=[])

    root = logging.getLogger()
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers), (
        "Console handler missing"
    )

    logger = logging.getLogger("test.console")
    logger.info("hello console")
    assert any("hello console" in r.getMessage() for r in caplog.records)


def test_setup_logging_file_logging_with_env(tmp_path: Path):
    reset_logging()

    log_file = tmp_path / "mylog.log"
    os.environ["LOG_TO_FILE"] = "true"
    os.environ["LOG_FILE"] = str(log_file)

    try:
        setup_logging(app_name="unit-test-env", cfg_parsers=[])
        logger = logging.getLogger("test.file")
        logger.info("hello file")

        # Ensure handlers flush
        for h in logging.getLogger().handlers:
            try:
                h.flush()
            except Exception:
                pass

        assert log_file.exists(), "Log file was not created"
        content = log_file.read_text(encoding="utf-8")
        assert "hello file" in content
    finally:
        os.environ.pop("LOG_TO_FILE", None)
        os.environ.pop("LOG_FILE", None)


def test_setup_logging_ini_precedence_over_env(tmp_path: Path):
    reset_logging()

    # ENV says DEBUG, but INI says ERROR; INI should win
    os.environ["LOG_LEVEL"] = "DEBUG"
    try:
        cfg = configparser.ConfigParser()
        cfg.add_section("logging")
        cfg.set("logging", "LOG_LEVEL", "ERROR")

        setup_logging(app_name="unit-test-ini", cfg_parsers=[cfg])

        root = logging.getLogger()
        assert root.level == logging.ERROR
    finally:
        os.environ.pop("LOG_LEVEL", None)
