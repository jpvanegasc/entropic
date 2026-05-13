# entropic

Entropic is a minimal run cache for Python-driven simulations and scripts.
By hashing your input parameters, it automatically identifies duplicate runs and
skips unnecessary computation. It is completely agnostic to your simulation engine,
lightweight by design, and built to manage locally run research workflows without
getting in your way.

Storage is backed by SQLAlchemy: parameters and metadata live in a SQL database
(SQLite by default), result files live on disk next to it.

## Install

```bash
pip install entropic
# or
uv add entropic
```

## Quickstart

```python
from pathlib import Path
import numpy as np

from entropic import Store, Base, Mapped


# 1. Define a SQLAlchemy model for your simulation parameters.
#    The four reserved columns (id, result_file, created_at, custom_data)
#    come from Base — your columns are the parameters you want to query on.
class SimResult(Base):
    __tablename__ = "results"

    n: Mapped[int]
    steps: Mapped[int]
    dt: Mapped[float]


# 2. Define a runner. It receives a single dict; entropic injects
#    `params["result_file"]` (the target path) before calling.
def my_simulation(params: dict) -> None:
    data = np.random.randn(params["n"], params["steps"])
    np.save(params["result_file"], data)


store = Store(
    runner=my_simulation,
    result_cls=SimResult,
    results_dir="./results",
    db_url="sqlite:///./runs.sqlite3",
    file_suffix=".npy",
)

# 3. Run or retrieve from cache
record = store.run_or_retrieve({"n": 100, "steps": 5000, "dt": 0.01})
print(record.result_file)         # ./results/a3f8c1d2e4b6f7a8.npy
print(record.id)                  # a3f8c1d2e4b6f7a8
print(record.n, record.dt)        # 100  0.01
print(record.custom_data)         # {"elapsed_seconds": 0.042}

# Second call with same params → instant cache hit, runner not invoked
same = store.run_or_retrieve({"n": 100, "steps": 5000, "dt": 0.01})
```

## Core API

### `Store`

```python
store = Store(
    runner=my_simulation,
    result_cls=SimResult,
    results_dir="./results",            # where result files live
    file_suffix=".h5",                  # extension for auto-generated filenames
    db_url="sqlite:///./db.sqlite3",    # SQLAlchemy URL
)
```

`runner` is called as `runner(params)`; the Store passes a copy of your params
with `id` and `result_file` injected. The runner writes its output to
`params["result_file"]`.

`result_cls` must be a `Base` subclass. Its column names must match the keys of
the params dicts you pass to the Store — those columns are how `list(where=...)`
filters work.

#### `store.run_or_retrieve(params, **custom_data) → ModelT`

The main workhorse. Returns the cached record if `params` hashes to an existing
row, otherwise runs the simulation and persists the new row.

```python
record = store.run_or_retrieve(
    {"n": 50, "method": "rk4"},
    git_sha="abc123",   # stored on record.custom_data
)
```

#### `store.run(params, **custom_data) → ModelT`

Always runs the simulation and overwrites the cache for that hash.

#### `store.retrieve(params) → ModelT | None`

Look up a cached run by exact parameter match. Returns `None` on a miss.

#### `store.register(params, result_file, **custom_data) → ModelT`

Index an externally-produced result file. Raises `FileNotFoundError` if
`result_file` does not exist.

```python
store.register(
    {"n": 50, "method": "euler"},
    result_file="./results/my_external_run.h5",
)
```

#### `store.sweep(params_iter, **custom_data) → list[ModelT]`

Run or retrieve results for each parameter set in an iterable. Reuses cached
results where possible.

```python
records = store.sweep([{"n": 10, "dt": dt} for dt in [0.01, 0.005, 0.001]])
```

#### `store.list(where=None) → list[ModelT]`

Return all records, or those matching an exact column filter
(`where={"method": "rk4"}`). Filter keys must be column names on `result_cls`.

#### `store.delete(params, remove_file=False) → bool`

Delete a record by exact parameter match. Returns `True` if a row was removed.

### Record fields (from `Base`)

| Field         | Type            | Description                                                    |
| ------------- | --------------- | -------------------------------------------------------------- |
| `id`          | `str`           | 16-char hex hash of the parameters (primary key).              |
| `result_file` | `str`           | Path to the result file on disk.                               |
| `created_at`  | `datetime`      | UTC timestamp set on insert.                                   |
| `custom_data` | `dict[str,Any]` | JSON column. `elapsed_seconds` is added automatically on runs. |

Any user-defined columns on the model are populated from the matching keys in
`params`.

## How it works

Each run is keyed by a deterministic 16-char SHA-256 hash of its normalized
params (dict keys sorted, floats rounded to 12 digits, enums replaced by
`.value`, tuples flattened to lists, everything else `str()`-coerced).

When the runner finishes, entropic writes a sidecar JSON next to the result file
with the params + `custom_data`, then ingests it into the database. The sidecar
is unlinked on a successful insert. Sidecars left behind imply the result file
was missing or empty when ingestion ran — they will be re-ingested on the next
operation that triggers `_ingest_to_db`.

## Reserved keys in `params`

The four `Base` columns — `id`, `result_file`, `created_at`, `custom_data` —
are stripped from `params` before hashing. If you pass an explicit `id`, it
short-circuits hashing and is used verbatim as the row's primary key.

User-defined param keys must match column names on `result_cls`; extra keys will
fail the SQLAlchemy insert.

## Runner contract

```python
def runner(params: dict[str, Any]) -> None:
    # params["result_file"] is the path to write to
    # all other keys are your simulation parameters
    ...
```

The library generates `params["result_file"]` (`<results_dir>/<hash><suffix>`)
before invoking your runner.

## Logging

entropic uses a `NullHandler` by default (no output). To see what the library
is doing:

```python
import logging
logging.getLogger("entropic").addHandler(logging.StreamHandler())
logging.getLogger("entropic").setLevel(logging.INFO)
```

## Development

```bash
git clone https://github.com/jpvanegasc/entropic.git
cd entropic
uv sync --group dev
uv run pytest tests/ -v
```

## License

MIT
