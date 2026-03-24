"""Tests for entropic logging configuration."""

import logging

from entropic.logging import logger


def test_logger_name():
    assert isinstance(logger, logging.Logger)
    assert logger.name == "entropic"


def test_user_can_capture_messages(tmp_path):
    """Users can add a handler + set level and receive log messages."""
    from entropic import Store

    captured: list[str] = []
    handler = logging.Handler()
    handler.emit = lambda record: captured.append(record.getMessage())  # type: ignore[assignment]
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        store = Store(tmp_path / "results", tmp_path / "db.json")
        store.run({"n": 1}, lambda p, path: path.write_text("x"))
        assert any("Run completed" in msg for msg in captured)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(logging.NOTSET)
