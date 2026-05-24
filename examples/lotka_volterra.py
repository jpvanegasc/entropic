"""Lotka-Volterra (predator-prey) example for entropic.

Demonstrates every public Store method:
  run_or_retrieve, run, retrieve, register, list, delete

Simulation: Euler integrator for the classic two-ODE system
  dx/dt =  alpha*x - beta*x*y   (prey)
  dy/dt = -delta*y + gamma*x*y  (predator)

Results saved as NumPy .npz files (arrays: prey, predator, time).
"""

from pathlib import Path

import numpy as np

from entropic import Store, Base, Mapped


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class LotkaVolterraResult(Base):
    __tablename__ = "lotka_volterra_results"

    alpha: Mapped[float]
    beta: Mapped[float]
    gamma: Mapped[float]
    delta: Mapped[float]
    x0: Mapped[float]
    y0: Mapped[float]
    dt: Mapped[float]
    steps: Mapped[int]


# ---------------------------------------------------------------------------
# Runner: Euler integrator for Lotka-Volterra
# ---------------------------------------------------------------------------


def euler_runner(params: dict) -> None:
    """Euler integrator. Writes prey/predator/time arrays to params['result_file']."""
    x = float(params["x0"])
    y = float(params["y0"])
    dt = float(params["dt"])
    steps = int(params["steps"])
    alpha = float(params["alpha"])
    beta = float(params["beta"])
    gamma = float(params["gamma"])
    delta = float(params["delta"])

    prey = np.empty(steps)
    predator = np.empty(steps)
    t = np.empty(steps)

    for i in range(steps):
        prey[i] = x
        predator[i] = y
        t[i] = i * dt
        dx = alpha * x - beta * x * y
        dy = -delta * y + gamma * x * y
        x += dx * dt
        y += dy * dt

    np.savez(params["result_file"], prey=prey, predator=predator, time=t)


# ---------------------------------------------------------------------------
# Store setup
# ---------------------------------------------------------------------------


EXAMPLES_DIR = Path(__file__).parent
store: Store[LotkaVolterraResult] = Store(
    runner=euler_runner,
    result_cls=LotkaVolterraResult,
    results_dir=EXAMPLES_DIR / "results",
    db_url=f"sqlite:///{EXAMPLES_DIR / 'entropic.sqlite3'}",
    file_suffix=".npz",
)


# ---------------------------------------------------------------------------
# Section 1: run_or_retrieve — cache miss then cache hit
# ---------------------------------------------------------------------------

print("=== run_or_retrieve (cache miss) ===")
params_classic = {
    "alpha": 1.0,
    "beta": 0.1,
    "gamma": 0.075,
    "delta": 1.5,
    "x0": 10.0,
    "y0": 5.0,
    "dt": 0.01,
    "steps": 5000,
}
record1 = store.run_or_retrieve(params_classic, tag="classic")
print(f"  id:          {record1.id}")
print(f"  result_file: {record1.result_file}")
print(f"  created_at:  {record1.created_at}")
print(f"  custom_data: {record1.custom_data}")

print("\n=== run_or_retrieve (cache hit) ===")
record1b = store.run_or_retrieve(params_classic)
print(f"  id:        {record1b.id}")
print(f"  same path: {record1b.result_file == record1.result_file}")

# ---------------------------------------------------------------------------
# Section 2: retrieve — pure cache lookup
# ---------------------------------------------------------------------------

print("\n=== retrieve (hit) ===")
hit = store.retrieve(params_classic)
assert hit is not None
print(f"  found:  {hit.id}")

print("\n=== retrieve (miss) ===")
miss = store.retrieve({**params_classic, "alpha": 99.0})
print(f"  result: {miss}")  # None

# ---------------------------------------------------------------------------
# Section 3: run — forced re-run, overwrites the row at the same hash
# ---------------------------------------------------------------------------

print("\n=== run (forced) ===")
params_fast = {
    "alpha": 2.0,
    "beta": 0.2,
    "gamma": 0.1,
    "delta": 1.0,
    "x0": 8.0,
    "y0": 4.0,
    "dt": 0.005,
    "steps": 2000,
}
record2 = store.run(params_fast, note="forced re-run demo")
print(f"  id:      {record2.id}")
print(f"  elapsed: {record2.custom_data.get('elapsed_seconds')}s")

# Re-run with same params — same hash → same row, overwritten
record2b = store.run(params_fast)
print(f"  re-run id:   {record2b.id}")
print(f"  same row:    {record2b.id == record2.id}")
print(f"  same path:   {record2b.result_file == record2.result_file}")

# ---------------------------------------------------------------------------
# Section 4: register — manually index an external result file
# ---------------------------------------------------------------------------

print("\n=== register (external result) ===")
params_external = {
    "alpha": 0.5,
    "beta": 0.05,
    "gamma": 0.04,
    "delta": 0.8,
    "x0": 20.0,
    "y0": 10.0,
    "dt": 0.02,
    "steps": 1000,
}

# Produce the result file manually (simulating an externally-run simulation)
external_path = EXAMPLES_DIR / "results" / "external_run.npz"
external_path.parent.mkdir(parents=True, exist_ok=True)
x, y = float(params_external["x0"]), float(params_external["y0"])
prey_arr = np.empty(params_external["steps"])
pred_arr = np.empty(params_external["steps"])
t_arr = np.empty(params_external["steps"])
for i in range(params_external["steps"]):
    prey_arr[i] = x
    pred_arr[i] = y
    t_arr[i] = i * params_external["dt"]
    dx = params_external["alpha"] * x - params_external["beta"] * x * y
    dy = -params_external["delta"] * y + params_external["gamma"] * x * y
    x += dx * params_external["dt"]
    y += dy * params_external["dt"]
np.savez(external_path, prey=prey_arr, predator=pred_arr, time=t_arr)

record3 = store.register(params_external, external_path, source="external")
print(f"  registered:  {record3.id}")
print(f"  result_file: {record3.result_file}")

# ---------------------------------------------------------------------------
# Section 5: list — all rows and filtered query
# ---------------------------------------------------------------------------

print("\n=== list() — all rows ===")
all_records = store.list()
print(f"  total rows: {len(all_records)}")
for r in all_records:
    print(f"  [{r.id}] alpha={r.alpha}  {Path(r.result_file).name}")

print("\n=== list(where=...) — filter by alpha=1.0 ===")
filtered = store.list(where={"alpha": 1.0})
print(f"  matching rows: {len(filtered)}")
for r in filtered:
    print(f"  [{r.id}] {Path(r.result_file).name}")

# ---------------------------------------------------------------------------
# Section 6: delete — remove row (with and without file)
# ---------------------------------------------------------------------------

print("\n=== delete (row only, keep file) ===")
deleted = store.delete(params_fast, remove_file=False)
print(f"  deleted: {deleted}")

print("\n=== delete (row + file) ===")
deleted2 = store.delete(params_external, remove_file=True)
print(f"  deleted: {deleted2}")
print(f"  external file still on disk? {external_path.exists()}")

# ---------------------------------------------------------------------------
# Teardown note
# ---------------------------------------------------------------------------

remaining = store.list()
print(f"\nFinal row count: {len(remaining)}")
print("Done. Results in:", EXAMPLES_DIR / "results")
