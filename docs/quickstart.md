# Quickstart

## Basic usage

Define a runner — a callable that accepts `(params, result_path)` and writes output to the given path — then hand it to `run_or_retrieve`:

```python
from pathlib import Path
import numpy as np
from entropic import Store

store = Store("./results", "./runs.json")

def my_sim(params: dict, result_path: Path) -> None:
    rng = np.random.default_rng(params["seed"])
    data = rng.standard_normal(params["n"])
    np.save(result_path, data)

record = store.run_or_retrieve(
    params={"n": 10_000, "seed": 42},
    runner=my_sim,
)

data = np.load(record.result_path)
```

The first call runs the simulation. Every subsequent call with the same parameters returns the cached result without re-running.

## The result record

`run_or_retrieve` (and all other methods that produce a result) returns a `RunRecord`:

```python
record.params         # {"n": 10_000, "seed": 42}
record.result_path    # Path("./results/1769854174.763568_a3f8c1d2e4b6f7a8.npy")
record.params_hash    # "a3f8c1d2e4b6f7a8"
record.created_at     # "2025-06-15T10:30:00+00:00"
record.metadata       # {"elapsed_seconds": 0.012}
```

## Querying runs

List all cached runs:

```python
records = store.list()
```

Filter by a partial parameter match — only the provided keys need to match:

```python
large_runs = store.list(where={"n": 10_000})
```

This returns every record where `n == 10_000` regardless of other parameters.

## Deleting runs

Remove a record from the index:

```python
store.delete(params={"n": 10_000, "seed": 42})
```

Pass `remove_file=True` to also delete the result file from disk:

```python
store.delete(params={"n": 10_000, "seed": 42}, remove_file=True)
```

Returns `True` if a matching record was found and removed, `False` otherwise.

## Registering external files

If you produced a result file outside entropic and want to index it:

```python
store.register(
    params={"n": 10_000, "seed": 42},
    result_path="./results/my_existing_run.npy",
)
```

The file must already exist. After registration it is retrievable via `store.retrieve()` or `store.list()` like any other run.
