"""Lotka-Volterra (predator-prey) example for entropic v2.

Demonstrates every public Store method:
  run_or_retrieve, run, retrieve, register, list, delete

Simulation: Euler integrator for the classic two-ODE system
  dx/dt =  alpha*x - beta*x*y   (prey)
  dy/dt = -delta*y + gamma*x*y  (predator)

Results saved as NumPy .npz files (arrays: prey, predator, time).
"""

from pathlib import Path

import numpy as np

from entropic import RunRecord, Store

# ---------------------------------------------------------------------------
# Store setup
# ---------------------------------------------------------------------------

EXAMPLES_DIR = Path(__file__).parent
store = Store(
    results_dir=EXAMPLES_DIR / "results",
    db_path=EXAMPLES_DIR / "entropic.json",
    file_suffix=".npz",
)

# ---------------------------------------------------------------------------
# Runner definition
# ---------------------------------------------------------------------------


def euler_runner(params: dict, path: Path) -> None:
    """Euler integrator for Lotka-Volterra. Writes prey/predator/time to path."""
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

    np.savez(path, prey=prey, predator=predator, time=t)


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
record1: RunRecord = store.run_or_retrieve(params_classic, euler_runner, tag="classic")
print(f"  hash:       {record1.params_hash}")
print(f"  result:     {record1.result_path}")
print(f"  created_at: {record1.created_at}")
print(f"  metadata:   {record1.metadata}")

print("\n=== run_or_retrieve (cache hit) ===")
record1b: RunRecord = store.run_or_retrieve(params_classic, euler_runner)
print(f"  hash:       {record1b.params_hash}")
print(f"  same path:  {record1b.result_path == record1.result_path}")

# ---------------------------------------------------------------------------
# Section 2: retrieve — pure cache lookup
# ---------------------------------------------------------------------------

print("\n=== retrieve (hit) ===")
hit = store.retrieve(params_classic)
assert hit is not None
print(f"  found:  {hit.params_hash}")

print("\n=== retrieve (miss) ===")
miss = store.retrieve(
    {
        "alpha": 99.0,
        "beta": 0.1,
        "gamma": 0.075,
        "delta": 1.5,
        "x0": 10.0,
        "y0": 5.0,
        "dt": 0.01,
        "steps": 5000,
    }
)
print(f"  result: {miss}")  # None

# ---------------------------------------------------------------------------
# Section 3: run — always creates a new record
# ---------------------------------------------------------------------------

print("\n=== run (forced, new record even for same params) ===")
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
record2: RunRecord = store.run(params_fast, euler_runner, note="forced re-run demo")
print(f"  hash:    {record2.params_hash}")
print(f"  elapsed: {record2.metadata.get('elapsed_seconds')}s")

# Run again with same params — run() always executes, yielding a second record
record2b: RunRecord = store.run(params_fast, euler_runner)
print(f"  second forced run hash: {record2b.params_hash}")
print(f"  same path? {record2b.result_path == record2.result_path}")  # False: new path

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

record3: RunRecord = store.register(params_external, external_path, source="external")
print(f"  registered: {record3.params_hash}")
print(f"  path:       {record3.result_path}")

# ---------------------------------------------------------------------------
# Section 5: list — all records and filtered query
# ---------------------------------------------------------------------------

print("\n=== list() — all records ===")
all_records = store.list()
print(f"  total records: {len(all_records)}")
for r in all_records:
    print(f"  [{r.params_hash}] alpha={r.params.get('alpha')}  {r.result_path.name}")

print("\n=== list(where=...) — filter by alpha=1.0 ===")
filtered = store.list(where={"alpha": 1.0})
print(f"  matching records: {len(filtered)}")
for r in filtered:
    print(f"  [{r.params_hash}] {r.result_path.name}")

# ---------------------------------------------------------------------------
# Section 6: delete — remove record (with and without file)
# ---------------------------------------------------------------------------

print("\n=== delete (record only, keep file) ===")
deleted = store.delete(params_fast, remove_file=False)
print(f"  deleted first record: {deleted}")
# record2b used same params — delete that one too (removes the file this time)

print("\n=== delete (record + file) ===")
deleted2 = store.delete(params_fast, remove_file=True)
print(f"  deleted second record + file: {deleted2}")

# ---------------------------------------------------------------------------
# Teardown note
# ---------------------------------------------------------------------------

remaining = store.list()
print(f"\nFinal record count: {len(remaining)}")
print("Done. Results in:", EXAMPLES_DIR / "results")
