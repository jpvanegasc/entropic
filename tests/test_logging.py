"""Tests for entropic logging configuration."""

import logging
from pathlib import Path

from entropic import Store, Base, Mapped
from entropic.logging import logger


class _LogResult(Base):
    __tablename__ = "log_results"

    n: Mapped[int]


def test_logger_name():
    assert isinstance(logger, logging.Logger)
    assert logger.name == "entropic"


def test_user_can_capture_messages(tmp_path):
    """Users can add a handler + set level and receive log messages."""

    captured: list[str] = []
    handler = logging.Handler()
    handler.emit = lambda record: captured.append(record.getMessage())  # type: ignore[assignment]
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        store: Store[_LogResult] = Store(
            runner=lambda p: Path(p["result_file"]).write_text("x"),
            result_cls=_LogResult,
            results_dir=tmp_path / "results",
            db_url=f"sqlite:///{tmp_path}/db.sqlite3",
        )
        store.run({"n": 1})
        assert any("Run completed" in msg for msg in captured)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(logging.NOTSET)
