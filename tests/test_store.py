"""Tests for the Store class."""

from pathlib import Path

import pytest

from entropic import Store


@pytest.fixture
def tmp_store(tmp_path: Path) -> Store:
    """Create a Store with temp directories."""
    return Store(
        results_dir=tmp_path / "results",
        db_path=tmp_path / "test.json",
        file_suffix=".dat",
    )


def _dummy_runner(params: dict, result_path: Path) -> None:
    """A trivial runner that writes params as text."""
    result_path.write_text(f"n={params['n']}")


class TestRetrieve:
    def test_miss_returns_none(self, tmp_store: Store):
        assert tmp_store.retrieve({"n": 10}) is None

    def test_hit_after_run(self, tmp_store: Store):
        tmp_store.run({"n": 10}, _dummy_runner)
        record = tmp_store.retrieve({"n": 10})
        assert record is not None
        assert record.params == {"n": 10}
        assert record.result_path.exists()


class TestRun:
    def test_creates_result_file(self, tmp_store: Store):
        record = tmp_store.run({"n": 5}, _dummy_runner)
        assert record.result_path.exists()
        assert record.result_path.read_text() == "n=5"

    def test_records_elapsed_time(self, tmp_store: Store):
        record = tmp_store.run({"n": 5}, _dummy_runner)
        assert "elapsed_seconds" in record.metadata

    def test_custom_metadata(self, tmp_store: Store):
        record = tmp_store.run({"n": 5}, _dummy_runner, git_sha="abc123")
        assert record.metadata["git_sha"] == "abc123"

    def test_run_always_creates_new(self, tmp_store: Store):
        r1 = tmp_store.run({"n": 5}, _dummy_runner)
        r2 = tmp_store.run({"n": 5}, _dummy_runner)
        # Two separate records (different timestamps/paths)
        assert r1.result_path != r2.result_path


class TestRunOrRetrieve:
    def test_first_call_runs(self, tmp_store: Store):
        record = tmp_store.run_or_retrieve({"n": 10}, _dummy_runner)
        assert record.result_path.exists()

    def test_second_call_retrieves(self, tmp_store: Store):
        r1 = tmp_store.run_or_retrieve({"n": 10}, _dummy_runner)
        r2 = tmp_store.run_or_retrieve({"n": 10}, _dummy_runner)
        assert r1.result_path == r2.result_path

    def test_different_params_run_separately(self, tmp_store: Store):
        r1 = tmp_store.run_or_retrieve({"n": 10}, _dummy_runner)
        r2 = tmp_store.run_or_retrieve({"n": 20}, _dummy_runner)
        assert r1.result_path != r2.result_path


class TestSweep:
    def test_sweep_runs_all(self, tmp_store: Store):
        params = [{"n": 1}, {"n": 2}, {"n": 3}]
        records = tmp_store.sweep(params, _dummy_runner)
        assert len(records) == 3
        assert all(r.result_path.exists() for r in records)

    def test_sweep_uses_cache(self, tmp_store: Store):
        call_count = 0

        def counting_runner(params: dict, result_path: Path) -> None:
            nonlocal call_count
            call_count += 1
            result_path.write_text(f"n={params['n']}")

        # Pre-cache one combination
        tmp_store.run({"n": 2}, counting_runner)
        assert call_count == 1

        # Sweep includes the cached one
        records = tmp_store.sweep([{"n": 1}, {"n": 2}, {"n": 3}], counting_runner)
        assert len(records) == 3
        # Only n=1 and n=3 should have triggered new runs
        assert call_count == 3

    def test_sweep_empty(self, tmp_store: Store):
        assert tmp_store.sweep([], _dummy_runner) == []

    def test_sweep_preserves_order(self, tmp_store: Store):
        params = [{"n": 30}, {"n": 10}, {"n": 20}]
        records = tmp_store.sweep(params, _dummy_runner)
        assert [r.params["n"] for r in records] == [30, 10, 20]


class TestRegister:
    def test_register_existing_file(self, tmp_store: Store):
        # Create a file externally
        ext_file = tmp_store.results_dir / "external.dat"
        ext_file.write_text("external data")

        record = tmp_store.register({"n": 42}, ext_file)
        assert record.result_path == ext_file

        # Should be retrievable
        found = tmp_store.retrieve({"n": 42})
        assert found is not None
        assert found.result_path == ext_file

    def test_register_missing_file_raises(self, tmp_store: Store):
        with pytest.raises(FileNotFoundError):
            tmp_store.register({"n": 42}, Path("/nonexistent.dat"))


class TestList:
    def test_empty_store(self, tmp_store: Store):
        assert tmp_store.list() == []

    def test_list_all(self, tmp_store: Store):
        tmp_store.run({"n": 5, "method": "euler"}, _dummy_runner)
        tmp_store.run({"n": 10, "method": "rk4"}, _dummy_runner)
        assert len(tmp_store.list()) == 2

    def test_list_with_filter(self, tmp_store: Store):
        tmp_store.run({"n": 5, "method": "euler"}, _dummy_runner)
        tmp_store.run({"n": 10, "method": "rk4"}, _dummy_runner)
        tmp_store.run({"n": 20, "method": "rk4"}, _dummy_runner)

        rk4_runs = tmp_store.list(where={"method": "rk4"})
        assert len(rk4_runs) == 2
        assert all(r.params["method"] == "rk4" for r in rk4_runs)

    def test_list_multi_field_filter(self, tmp_store: Store):
        tmp_store.run({"n": 5, "method": "rk4"}, _dummy_runner)
        tmp_store.run({"n": 10, "method": "rk4"}, _dummy_runner)

        results = tmp_store.list(where={"n": 10, "method": "rk4"})
        assert len(results) == 1


class TestDelete:
    def test_delete_existing(self, tmp_store: Store):
        tmp_store.run({"n": 5}, _dummy_runner)
        assert tmp_store.delete({"n": 5})
        assert tmp_store.retrieve({"n": 5}) is None

    def test_delete_nonexistent(self, tmp_store: Store):
        assert not tmp_store.delete({"n": 999})

    def test_delete_with_file_removal(self, tmp_store: Store):
        record = tmp_store.run({"n": 5}, _dummy_runner)
        path = record.result_path
        assert path.exists()

        tmp_store.delete({"n": 5}, remove_file=True)
        assert not path.exists()
