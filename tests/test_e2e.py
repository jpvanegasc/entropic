"""End-to-end test exercising the full entropic workflow.

Uses a self-contained logistic growth ODE solver as the runner.
Covers: Store (all 7 methods), RunRecord round-trip, TinyDBIndex,
parameter hashing, and logging — all through a realistic simulation flow.
"""

import csv
from pathlib import Path

from entropic.record import RunRecord
import pytest

from entropic import Store


# ---------------------------------------------------------------------------
# Runner: logistic growth  dx/dt = r*x*(1 - x/K), Euler integrator
# Writes time series to CSV (stdlib only, no numpy).
# ---------------------------------------------------------------------------


def logistic_runner(params: dict, result_path: Path) -> None:
    """Euler integrator for logistic growth. Writes t,x columns to CSV."""
    x = float(params["x0"])
    r = float(params["r"])
    k = float(params["K"])
    dt = float(params["dt"])
    steps = int(params["steps"])

    with open(result_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t", "x"])
        for i in range(steps):
            writer.writerow([round(i * dt, 6), round(x, 6)])
            x += r * x * (1 - x / k) * dt


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store(tmp_path: Path) -> Store:
    return Store(
        results_dir=tmp_path / "results",
        db_path=tmp_path / "index.json",
        file_suffix=".csv",
    )


PARAMS_A = {"r": 0.5, "K": 100.0, "x0": 2.0, "dt": 0.1, "steps": 200}
PARAMS_B = {"r": 1.0, "K": 50.0, "x0": 1.0, "dt": 0.05, "steps": 100}


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


def test_full_workflow(store: Store, tmp_path: Path) -> None:
    call_count = 0

    def counting_runner(params: dict, result_path: Path) -> None:
        nonlocal call_count
        call_count += 1
        logistic_runner(params, result_path)

    def find_max(record: RunRecord) -> float:
        max_x = 0.0
        with open(record.result_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if float(row["x"]) >= max_x:
                    max_x = float(row["x"])
        return max_x

    # 1. run_or_retrieve — cache miss
    r1 = store.run_or_retrieve(PARAMS_A, counting_runner, tag="first")
    assert call_count == 1
    assert r1.result_path.exists()
    assert r1.params == PARAMS_A
    assert "elapsed_seconds" in r1.metadata
    assert r1.metadata["tag"] == "first"
    assert len(r1.params_hash) == 16

    # Verify CSV content
    with open(r1.result_path) as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["t", "x"]
        rows = list(reader)
        assert len(rows) == PARAMS_A["steps"]

    # 2. run_or_retrieve — cache hit (runner NOT called)
    r1b = store.run_or_retrieve(PARAMS_A, counting_runner)
    assert call_count == 1  # no new call
    assert r1b.result_path == r1.result_path
    assert r1b.params_hash == r1.params_hash

    # 3. run — forced re-run, always creates new record
    r2 = store.run(PARAMS_A, counting_runner)
    assert call_count == 2
    assert r2.result_path != r1.result_path
    assert r2.result_path.exists()
    assert r1.result_path.exists()  # original still there

    # 4. retrieve — hit and miss
    found = store.retrieve(PARAMS_A)
    assert found is not None
    assert found.params_hash == r1.params_hash

    miss = store.retrieve({"r": 999.0, "K": 1.0, "x0": 1.0, "dt": 0.1, "steps": 10})
    assert miss is None

    # 5. register — index an external file
    external_path = tmp_path / "results" / "external.csv"
    with open(external_path, "w", newline="") as f:
        csv.writer(f).writerow(["t", "x"])
    r3 = store.register(PARAMS_B, external_path, source="external")
    assert r3.result_path == external_path
    assert r3.metadata["source"] == "external"
    assert store.retrieve(PARAMS_B) is not None

    # 6. list — all records and filtered
    all_records = store.list()
    assert len(all_records) == 3  # r1, r2 (forced), r3 (registered)

    filtered = store.list(where={"r": 0.5})
    assert len(filtered) == 2  # r1 and r2

    filtered_b = store.list(where={"r": 1.0})
    assert len(filtered_b) == 1
    assert filtered_b[0].params_hash == r3.params_hash

    # 7. sweep — run over a param grid, reuses cache
    sweep_params = [{**PARAMS_A, "x0": x0} for x0 in [2.0, 5.0, 10.0]]
    # x0=2.0 is already cached (same as PARAMS_A)
    records = list(store.sweep(sweep_params, counting_runner))
    assert len(records) == 3
    assert call_count == 4  # only x0=5.0 and x0=10.0 are new
    assert all(r.result_path.exists() for r in records)

    # map - apply a function to the results of a param grid
    results = list(store.map(find_max, sweep_params, counting_runner))
    assert len(results) == 3
    assert results == [99.779253, 99.918218, 99.9626]

    # delete — record only
    assert store.delete(PARAMS_B)
    assert store.retrieve(PARAMS_B) is None
    assert external_path.exists()  # file kept

    # delete — record + file
    r_to_delete = store.list(where={"x0": 5.0})[0]
    path_to_delete = r_to_delete.result_path
    assert path_to_delete.exists()
    assert store.delete({**PARAMS_A, "x0": 5.0}, remove_file=True)
    assert not path_to_delete.exists()

    # delete nonexistent
    assert not store.delete({"r": 999.0, "K": 1.0, "x0": 1.0, "dt": 0.1, "steps": 10})

    # 9. persistence — new Store instance with same paths finds existing records
    store2 = Store(
        results_dir=tmp_path / "results",
        db_path=tmp_path / "index.json",
        file_suffix=".csv",
    )
    found = store2.retrieve(PARAMS_A)
    assert found is not None
    assert found.result_path == r1.result_path
    assert found.result_path.exists()
