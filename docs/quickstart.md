# Quickstart

## Basic usage

Define a runner — a callable that accepts `(params, result_path)` and writes output to the given path — then hand it to `run_or_retrieve`:

```python
from pathlib import Path
import numpy as np
from entropic import Store

store = Store("./results", "./runs.json")

def my_sim(params: dict, result_path: Path) -> None:
    data = np.random.randn(params["n"], params["steps"])
    np.save(result_path, data)

record = store.run_or_retrieve(
    params={"n": 100, "steps": 5000, "dt": 0.01},
    runner=my_sim,
)

data = np.load(record.result_path)
```

The first call runs the simulation. Every subsequent call with the same parameters returns the cached result without re-running.

## The result record

`run_or_retrieve` (and all other methods that produce a result) returns a `RunRecord`:

```python
record.params         # {"n": 100, "steps": 5000, "dt": 0.01}
record.result_path    # Path("./results/1769854174.763568_a3f8c1d2e4b6f7a8.npy")
record.params_hash    # "a3f8c1d2e4b6f7a8"
record.created_at     # "2025-06-15T10:30:00+00:00"
record.metadata       # {"elapsed_seconds": 0.042}
```

## Retrieving without running

Look up a cached run without triggering execution:

```python
record = store.retrieve(params={"n": 100, "steps": 5000, "dt": 0.01})
```

Returns the `RunRecord` on a hit, `None` on a miss.

## Forcing a re-run

To always execute the runner regardless of the cache — useful for stochastic simulations where you want multiple independent runs with identical parameters:

```python
record = store.run(
    params={"n": 100, "steps": 5000, "dt": 0.01},
    runner=my_sim,
)
```

## Querying runs

List all cached runs:

```python
records = store.list()
```

Filter by a partial parameter match — only the provided keys need to match:

```python
fine_dt_runs = store.list(where={"dt": 0.01})
```

This returns every record where `dt == 0.01` regardless of other parameters.

## Deleting runs

Remove a record from the index:

```python
store.delete(params={"n": 100, "steps": 5000, "dt": 0.01})
```

Pass `remove_file=True` to also delete the result file from disk:

```python
store.delete(params={"n": 100, "steps": 5000, "dt": 0.01}, remove_file=True)
```

Returns `True` if a matching record was found and removed, `False` otherwise.

## Registering external files

If you produced a result file outside entropic and want to index it:

```python
store.register(
    params={"n": 100, "steps": 5000, "dt": 0.01},
    result_path="./results/my_existing_run.npy",
)
```

The file must already exist. After registration it is retrievable via `store.retrieve()` or `store.list()` like any other run.

## Parameter sweeps

Run or retrieve results for a batch of parameter sets:

```python
records = store.sweep(
    [{"n": 100, "steps": 5000, "dt": dt} for dt in [0.01, 0.005, 0.001]],
    runner=my_sim,
)
```

Cached results are reused — only new parameter combinations trigger the runner.

## Logging

entropic uses a `NullHandler` by default (silent). To enable logging:

```python
import logging
logging.getLogger("entropic").addHandler(logging.StreamHandler())
logging.getLogger("entropic").setLevel(logging.INFO)
```

This logs cache hits, run completions, and file operations.
