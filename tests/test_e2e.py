"""End-to-end test exercising the full entropic workflow.

Uses a self-contained logistic growth ODE solver as the runner.
Covers: Store (all public methods), parameter hashing, custom_data round-trip,
and SQLAlchemy persistence — through a realistic simulation flow.
"""

import csv
from pathlib import Path


from entropic import Store, Base, Mapped, expand_grid


# ---------------------------------------------------------------------------
# Runner: logistic growth  dx/dt = r*x*(1 - x/K), Euler integrator
# Writes time series to CSV (stdlib only, no numpy).
# ---------------------------------------------------------------------------


class Result(Base):
    __tablename__ = "results"

    r: Mapped[float]
    K: Mapped[float]
    x0: Mapped[float]
    dt: Mapped[float]
    steps: Mapped[int]


def logistic_runner(params: dict) -> None:
    """Euler integrator for logistic growth. Writes t,x columns to CSV."""
    x = float(params["x0"])
    r = float(params["r"])
    k = float(params["K"])
    dt = float(params["dt"])
    steps = int(params["steps"])

    with open(params["result_file"], "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t", "x"])
        for i in range(steps):
            writer.writerow([round(i * dt, 6), round(x, 6)])
            x += r * x * (1 - x / k) * dt


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _params_a() -> dict:
    return {"r": 0.5, "K": 100.0, "x0": 2.0, "dt": 0.1, "steps": 200}


def _params_b() -> dict:
    return {"r": 1.0, "K": 50.0, "x0": 1.0, "dt": 0.05, "steps": 100}


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


def test_full_workflow(tmp_path: Path) -> None:
    call_count = 0

    def counting_runner(params: dict) -> None:
        nonlocal call_count
        call_count += 1
        logistic_runner(params)

    store: Store[Result] = Store(
        runner=counting_runner,
        result_cls=Result,
        results_dir=tmp_path / "results",
        db_url=f"sqlite:///{tmp_path}/db.sqlite3",
        file_suffix=".csv",
    )

    # 1. run_or_retrieve — cache miss
    r1 = store.run_or_retrieve(_params_a(), tag="first")
    assert call_count == 1
    assert Path(r1.result_file).exists()
    assert r1.r == 0.5
    assert r1.K == 100.0
    assert r1.steps == 200
    assert "elapsed_seconds" in r1.custom_data
    assert r1.custom_data["tag"] == "first"
    assert len(r1.id) == 16

    # Verify CSV content
    with open(r1.result_file) as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["t", "x"]
        rows = list(reader)
        assert len(rows) == 200

    r1_id = r1.id
    r1_file = r1.result_file

    # 2. run_or_retrieve — cache hit (runner NOT called)
    r1b = store.run_or_retrieve(_params_a())
    assert call_count == 1  # no new call
    assert r1b.result_file == r1_file
    assert r1b.id == r1_id

    # 3. run — forced re-run, overwrites the existing record (same hash)
    r2 = store.run(_params_a())
    assert call_count == 2
    assert r2.id == r1_id  # same params → same id
    assert Path(r2.result_file).exists()

    # 4. retrieve — hit and miss
    found = store.retrieve(_params_a())
    assert found is not None
    assert found.id == r1_id

    miss = store.retrieve({"r": 999.0, "K": 1.0, "x0": 1.0, "dt": 0.1, "steps": 10})
    assert miss is None

    # 5. register — index an external file
    external_path = tmp_path / "results" / "external.csv"
    with open(external_path, "w", newline="") as f:
        csv.writer(f).writerow(["t", "x"])
    r3 = store.register(_params_b(), external_path, source="external")
    assert r3.result_file == str(external_path)
    assert r3.custom_data["source"] == "external"
    assert store.retrieve(_params_b()) is not None

    # 7. sweep — run over a param grid, reuses cache
    base = _params_a()
    records = store.sweep(
        expand_grid(
            {
                "r": [base["r"]],
                "K": [base["K"]],
                "x0": [2.0, 5.0, 10.0],
                "dt": [base["dt"]],
                "steps": [base["steps"]],
            }
        )
    )
    assert len(records) == 3
    assert call_count == 4  # only x0=5.0 and x0=10.0 are new
    assert all(Path(r.result_file).exists() for r in records)

    # delete — record only
    assert store.delete(_params_b())
    assert store.retrieve(_params_b()) is None
    assert external_path.exists()  # file kept

    # delete — record + file
    r_to_delete = store.retrieve({**_params_a(), "x0": 5.0})
    path_to_delete = Path(r_to_delete.result_file)
    assert path_to_delete.exists()
    assert store.delete({**_params_a(), "x0": 5.0}, remove_file=True)
    assert not path_to_delete.exists()

    # delete nonexistent
    assert not store.delete({"r": 999.0, "K": 1.0, "x0": 1.0, "dt": 0.1, "steps": 10})

    # 8. delete by a broader query — recipe from docs/quickstart.md: query
    # result_cls directly with SQLAlchemy for a partial parameter match
    # (every remaining run with K=100.0, regardless of x0), then feed the
    # matching hashes to delete(hash=...). x0=2.0 and x0=10.0 are what's left
    # from the sweep above (x0=5.0 was already deleted).
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    engine = create_engine(f"sqlite:///{tmp_path}/db.sqlite3")
    with Session(engine) as session:
        hashes = session.scalars(select(Result.id).where(Result.K == 100.0)).all()
    assert len(hashes) == 2

    for h in hashes:
        assert store.delete(hash=h)

    with Session(engine) as session:
        assert session.scalars(select(Result)).all() == []
