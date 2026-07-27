"""Edge-case unit tests for Store.

Happy-path coverage lives in test_e2e.py. These tests cover error paths
and specific behaviors that are hard to exercise in a normal workflow.
"""

from pathlib import Path

import pytest

from entropic import Store, Base, Mapped, expand_grid


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


def test_delete_by_hash(tmp_path: Path) -> None:
    """delete(hash=...) removes the record without needing the original params."""

    def writer(params: dict) -> None:
        Path(params["result_file"]).write_text("data")

    store = _make_store(tmp_path, writer)
    record = store.run({"n": 1})

    assert store.delete(hash=record.id)
    assert store.retrieve({"n": 1}) is None


def test_delete_by_hash_not_found(tmp_path: Path) -> None:
    """delete(hash=...) returns False for an unknown hash."""

    store = _make_store(tmp_path, lambda params: None)
    assert not store.delete(hash="deadbeefdeadbeef")


def test_delete_requires_params_or_hash(tmp_path: Path) -> None:
    """delete() with neither params nor hash raises ValueError."""

    store = _make_store(tmp_path, lambda params: None)
    with pytest.raises(ValueError, match="Either 'params' or 'hash' need to be set"):
        store.delete()


def test_delete_hash_takes_precedence_over_params(tmp_path: Path) -> None:
    """When both are given, hash is used and params is ignored."""

    def writer(params: dict) -> None:
        Path(params["result_file"]).write_text("data")

    store = _make_store(tmp_path, writer)
    record = store.run({"n": 1})

    assert store.delete(params={"n": 999}, hash=record.id)
    assert store.retrieve({"n": 1}) is None


def test_sweep_runs_all_param_sets(tmp_path: Path) -> None:
    """sweep runs every parameter set in the iterable."""

    def writer(params: dict) -> None:
        Path(params["result_file"]).write_text("data")

    store = _make_store(tmp_path, writer)
    records = store.sweep([{"n": 1}, {"n": 2}, {"n": 3}])
    assert len(records) == 3
    assert {r.n for r in records} == {1, 2, 3}


def test_sweep_with_expand_grid(tmp_path: Path) -> None:
    """expand_grid feeds the full Cartesian product into sweep."""

    def writer(params: dict) -> None:
        Path(params["result_file"]).write_text("data")

    store = _make_store(tmp_path, writer)
    records = store.sweep(expand_grid({"n": [1, 2, 3]}))
    assert len(records) == 3
    assert {r.n for r in records} == {1, 2, 3}


def test_sweep_reuses_cache(tmp_path: Path) -> None:
    """sweep skips runner for params already in cache."""
    call_count = 0

    def writer(params: dict) -> None:
        nonlocal call_count
        call_count += 1
        Path(params["result_file"]).write_text("data")

    store = _make_store(tmp_path, writer)
    store.run({"n": 1})
    assert call_count == 1

    store.sweep([{"n": 1}, {"n": 2}])
    assert call_count == 2  # n=1 cached, only n=2 is new


def test_register_missing_file_raises(tmp_path: Path) -> None:
    def runner(params: dict) -> None:
        Path(params["result_file"]).write_text("x")

    store = _make_store(tmp_path, runner)
    with pytest.raises(FileNotFoundError):
        store.register({"n": 42}, Path("/nonexistent.dat"))
