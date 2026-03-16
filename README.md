# entropic

Simulation-agnostic run cache. Manage, retrieve, and deduplicate simulation results without caring about what your simulation does or how it stores data.

`entropic` handles the mapping **parameters → result file**. It doesn't touch what's inside your result files — that's your business.

## Install

```bash
pip install entropic
```

Requires Python 3.10+ and TinyDB (installed automatically).

## Quickstart

```python
from entropic import Store

store = Store("./results", "./runs.json")

# Define a runner: receives (params, result_path), writes results to result_path
def my_simulation(params, result_path):
    import numpy as np
    data = np.random.randn(params["n"], params["steps"])
    np.save(result_path, data)

# Run or retrieve from cache
record = store.run_or_retrieve(
    params={"n": 100, "steps": 5000, "dt": 0.01},
    runner=my_simulation,
)
print(record.result_path)   # ./results/1769854174.763568_a3f8c1d2e4b6f7a8.npy
print(record.params)         # {"n": 100, "steps": 5000, "dt": 0.01}
print(record.metadata)       # {"elapsed_seconds": 0.042}

# Second call with same params → instant cache hit, no re-run
record = store.run_or_retrieve(
    params={"n": 100, "steps": 5000, "dt": 0.01},
    runner=my_simulation,
)
```

## Core API

### `Store`

```python
store = Store(
    results_dir="./results",     # where result files live
    db_path="./entropic.json",   # TinyDB metadata index
    file_suffix=".h5",           # extension for auto-generated filenames
    index=None,                  # custom IndexBackend (default: TinyDB)
)
```

#### `store.run_or_retrieve(params, runner, **metadata) → RunRecord`

The main workhorse. Returns a cached result if one exists for the given params, otherwise calls `runner(params, result_path)` and caches the result.

```python
record = store.run_or_retrieve(
    params={"n": 50, "method": "rk4"},
    runner=my_sim,
    git_sha="abc123",  # optional metadata
)
```

#### `store.run(params, runner, **metadata) → RunRecord`

Always runs the simulation, even if a cached result exists. Useful for re-running with the same parameters (e.g., stochastic simulations).

#### `store.retrieve(params) → RunRecord | None`

Look up a cached run by exact parameter match. Returns `None` on cache miss.

#### `store.register(params, result_path, **metadata) → RunRecord`

Manually register an externally-produced result file. Use this when you run simulations outside the library and want to index them for later retrieval.

```python
store.register(
    params={"n": 50, "method": "euler"},
    result_path="./results/my_external_run.h5",
)
```

#### `store.list(where=None) → list[RunRecord]`

List all runs, optionally filtered by partial parameter match. This is how you query by a subset of parameters — e.g., all runs with a specific grid size regardless of other settings.

```python
all_runs = store.list()
rk4_runs = store.list(where={"method": "rk4"})
specific = store.list(where={"method": "rk4", "n": 50})
```

#### `store.delete(params, remove_file=False) → bool`

Delete a run record by exact parameter match. Optionally removes the result file from disk.

### `RunRecord`

Frozen dataclass returned by all `Store` methods.

```python
record.params        # dict — the simulation parameters
record.result_path   # Path — path to the result file
record.params_hash   # str — 16-char hex hash of params
record.created_at    # str — ISO 8601 timestamp
record.metadata      # dict — user-defined extras (elapsed_seconds auto-added)
```

## How it works

Parameters are stored as **flat fields** in a TinyDB JSON file, plus a deterministic SHA-256 hash for fast exact lookups. This gives you both:

- **O(1) exact match** via `retrieve()` / `run_or_retrieve()` (hash lookup)
- **Flexible partial queries** via `list(where=...)` (field-by-field TinyDB search)

Parameter hashing normalizes values before hashing: dict keys are sorted, floats are rounded to 12 digits (avoiding IEEE 754 noise), enums are converted to their `.value`, and everything is serialized to canonical JSON.

## Custom index backends

The default TinyDB backend works well for local workflows. For larger-scale use (remote databases, shared teams), implement the `IndexBackend` protocol:

```python
from entropic.index import IndexBackend
from entropic.record import RunRecord

class PostgresIndex:
    def find_by_hash(self, params_hash: str) -> RunRecord | None: ...
    def find_by_params(self, params: dict) -> list[RunRecord]: ...
    def insert(self, record: RunRecord) -> None: ...
    def all(self) -> list[RunRecord]: ...
    def delete_by_hash(self, params_hash: str) -> bool: ...

store = Store("./results", index=PostgresIndex(conn_string="..."))
```

## Runner contract

A runner is any callable with this signature:

```python
def runner(params: dict[str, Any], result_path: Path) -> None:
    # 1. Use `params` to configure your simulation
    # 2. Write results to `result_path` (any format you want)
    # 3. Return nothing — entropic handles the rest
    ...
```

The library generates `result_path` for you (timestamp + hash + suffix). You just write to it.

## Development

```bash
git clone https://github.com/your-org/entropic.git
cd entropic
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
