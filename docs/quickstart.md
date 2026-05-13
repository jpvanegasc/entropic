# Quickstart

## Basic usage

Define a SQLAlchemy model whose columns mirror the params your simulation takes,
then a runner that writes its output to `params["result_file"]`. Hand both to a
`Store`:

```python
from pathlib import Path

import numpy as np

from entropic import Store, Base, Mapped


class SimResult(Base):
    __tablename__ = "results"

    n: Mapped[int]
    steps: Mapped[int]
    dt: Mapped[float]


def my_sim(params: dict) -> None:
    data = np.random.randn(params["n"], params["steps"])
    np.save(params["result_file"], data)


store = Store(
    runner=my_sim,
    result_cls=SimResult,
    results_dir="./results",
    db_url="sqlite:///./runs.sqlite3",
    file_suffix=".npy",
)

record = store.run_or_retrieve({"n": 100, "steps": 5000, "dt": 0.01})
data = np.load(record.result_file)
```

The first call runs the simulation. Every subsequent call with the same
parameters returns the cached row without re-running.

## The result record

Every `Store` method that returns a record returns an instance of your
`result_cls`. The four reserved columns from `Base` are always present; the
rest come from your model.

```python
record.id            # "a3f8c1d2e4b6f7a8" — 16-char hash, primary key
record.result_file   # "./results/a3f8c1d2e4b6f7a8.npy"
record.created_at    # datetime — UTC, set on insert
record.custom_data   # {"elapsed_seconds": 0.042}
record.n             # 100
record.dt            # 0.01
```

## Retrieving without running

```python
record = store.retrieve({"n": 100, "steps": 5000, "dt": 0.01})
```

Returns the model instance on a hit, `None` on a miss.

## Forcing a re-run

`run` always invokes the runner. Same params hash to the same row, so a forced
re-run overwrites the existing record (and result file) for that hash:

```python
record = store.run({"n": 100, "steps": 5000, "dt": 0.01})
```

## Querying runs

List all rows:

```python
records = store.list()
```

Filter by an exact column match — keys must be column names on `result_cls`:

```python
fine_dt_runs = store.list(where={"dt": 0.01})
```

For richer queries, drop down to SQLAlchemy directly against your model.

## Deleting runs

```python
store.delete({"n": 100, "steps": 5000, "dt": 0.01})
```

Pass `remove_file=True` to also delete the result file from disk:

```python
store.delete({"n": 100, "steps": 5000, "dt": 0.01}, remove_file=True)
```

Returns `True` if a row was removed, `False` otherwise.

## Registering external files

If a result file was produced outside entropic, index it via `register`:

```python
store.register(
    {"n": 100, "steps": 5000, "dt": 0.01},
    result_file="./results/my_existing_run.npy",
)
```

The file must already exist. After registration the row is reachable via
`retrieve` / `list` like any other run.

## Parameter sweeps

Run or retrieve results for a batch of parameter sets — cached rows are reused,
new ones invoke the runner:

```python
records = store.sweep(
    [{"n": 100, "steps": 5000, "dt": dt} for dt in [0.01, 0.005, 0.001]],
)
```

## Custom metadata

Any keyword argument to `run`, `run_or_retrieve`, `sweep`, or `register` lands
on the row's `custom_data` JSON column:

```python
record = store.run_or_retrieve(
    {"n": 100, "steps": 5000, "dt": 0.01},
    git_sha="abc123",
    note="initial sweep",
)
record.custom_data
# {"elapsed_seconds": 0.042, "git_sha": "abc123", "note": "initial sweep"}
```

`elapsed_seconds` is added automatically on actual runs.

## Logging

entropic uses a `NullHandler` by default (silent). To enable logging:

```python
import logging
logging.getLogger("entropic").addHandler(logging.StreamHandler())
logging.getLogger("entropic").setLevel(logging.INFO)
```

This logs cache hits, run completions, ingestion, and file operations.
