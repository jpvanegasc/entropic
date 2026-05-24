"""Edge-case unit tests for Store.

Happy-path coverage lives in test_e2e.py. These tests cover error paths
and specific behaviors that are hard to exercise in a normal workflow.
"""

from pathlib import Path

import pytest

from entropic import Store, Base, Mapped


class _StoreResult(Base):
    __tablename__ = "store_results"

    n: Mapped[int]


def _make_store(tmp_path: Path, runner) -> Store[_StoreResult]:
    return Store(
        runner=runner,
        result_cls=_StoreResult,
        results_dir=tmp_path / "results",
        db_url=f"sqlite:///{tmp_path}/db.sqlite3",
        file_suffix=".csv",
    )


def test_runner_exception_leaves_no_record(tmp_path: Path) -> None:
    """If the runner raises, the exception propagates and no record is stored."""

    def bad_runner(params: dict) -> None:
        raise ValueError("simulation exploded")

    store = _make_store(tmp_path, bad_runner)
    with pytest.raises(ValueError, match="simulation exploded"):
        store.run({"n": 5})

    assert store.retrieve({"n": 5}) is None


def test_delete_file_already_gone(tmp_path: Path) -> None:
    """delete(remove_file=True) doesn't crash if the file was already removed."""

    def writer(params: dict) -> None:
        Path(params["result_file"]).write_text("data")

    store = _make_store(tmp_path, writer)
    record = store.run({"n": 1})
    Path(record.result_file).unlink()  # remove file before delete

    assert store.delete({"n": 1}, remove_file=True)


def test_sweep_forwards_metadata(tmp_path: Path) -> None:
    """**custom_data kwargs are forwarded to each record in a sweep."""

    def writer(params: dict) -> None:
        Path(params["result_file"]).write_text("data")

    store = _make_store(tmp_path, writer)
    records = store.sweep(
        [{"n": 1}, {"n": 2}],
        experiment="test",
    )
    assert all(r.custom_data["experiment"] == "test" for r in records)


def test_register_missing_file_raises(tmp_path: Path) -> None:
    def runner(params: dict) -> None:
        Path(params["result_file"]).write_text("x")

    store = _make_store(tmp_path, runner)
    with pytest.raises(FileNotFoundError):
        store.register({"n": 42}, Path("/nonexistent.dat"))
