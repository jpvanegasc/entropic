"""Edge-case unit tests for Store.

Happy-path coverage lives in test_e2e.py. These tests cover error paths
and specific behaviors that are hard to exercise in a normal workflow.
"""

from pathlib import Path

import pytest

from entropic import Store


@pytest.fixture
def tmp_store(tmp_path: Path) -> Store:
    return Store(
        results_dir=tmp_path / "results",
        db_path=tmp_path / "test.json",
        file_suffix=".dat",
    )


def test_runner_exception_leaves_no_record(tmp_store: Store) -> None:
    """If the runner raises, the exception propagates and no record is stored."""

    def bad_runner(params: dict, result_path: Path) -> None:
        raise ValueError("simulation exploded")

    with pytest.raises(ValueError, match="simulation exploded"):
        tmp_store.run({"n": 5}, bad_runner)

    assert tmp_store.list() == []
    assert tmp_store.retrieve({"n": 5}) is None


def test_delete_file_already_gone(tmp_store: Store) -> None:
    """delete(remove_file=True) doesn't crash if the file was already removed."""

    def writer(params: dict, result_path: Path) -> None:
        result_path.write_text("data")

    record = tmp_store.run({"n": 1}, writer)
    record.result_path.unlink()  # remove file before delete

    assert tmp_store.delete({"n": 1}, remove_file=True)


def test_sweep_forwards_metadata(tmp_store: Store) -> None:
    """**metadata kwargs are forwarded to each record in a sweep."""

    def writer(params: dict, result_path: Path) -> None:
        result_path.write_text("data")

    records = tmp_store.sweep(
        [{"n": 1}, {"n": 2}],
        writer,
        experiment="test",
    )
    assert all(r.metadata["experiment"] == "test" for r in records)


def test_register_missing_file_raises(tmp_store: Store) -> None:
    with pytest.raises(FileNotFoundError):
        tmp_store.register({"n": 42}, Path("/nonexistent.dat"))
