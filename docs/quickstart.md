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

## Deleting runs

```python
store.delete({"n": 100, "steps": 5000, "dt": 0.01})
```

Pass `remove_file=True` to also delete the result file from disk:

```python
store.delete({"n": 100, "steps": 5000, "dt": 0.01}, remove_file=True)
```

Returns `True` if a row was removed, `False` otherwise.

You can also delete by hash directly, via the `hash` argument instead of `params`:

```python
store.delete(hash="a1b2c3d4e5f6a7b8")
```

### Deleting by a broader query

`delete` only matches a single, exact parameter set — there's no built-in
support for matching a subset of parameters (e.g. "every run with
`alpha=1`, regardless of `beta`"). For that, query `result_cls` directly with
SQLAlchemy and feed the matching hashes to `delete`:

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///db.sqlite3")
with Session(engine) as session:
    hashes = session.scalars(
        select(SimResult.id).where(SimResult.alpha == 1)
    ).all()

for h in hashes:
    store.delete(hash=h, remove_file=True)
```

Use the same `db_url` and `result_cls` you passed to `Store`.

## Registering external files

If a result file was produced outside entropic, index it via `register`:

```python
store.register(
    {"n": 100, "steps": 5000, "dt": 0.01},
    result_file="./results/my_existing_run.npy",
)
```

The file must already exist. After registration the row is reachable via
`retrieve` like any other run.

## Parameter sweeps

`sweep` is the batch counterpart to `run_or_retrieve`: it takes an **iterable of
param dicts**, reuses cached entries, and only invokes the runner for new
parameter sets. It makes no assumption about how the sets relate, so any sweep
shape is just an iterable.

For the common full-product case, build the iterable with `expand_grid` — each
key maps to a list of candidate values, and it returns one dict per combination:

```python
from entropic import expand_grid

records = store.sweep(
    expand_grid({"n": [100], "steps": [5000], "dt": [0.01, 0.005, 0.001]})
)
# runs 3 combinations: (n=100, steps=5000, dt=0.01), (…, dt=0.005), (…, dt=0.001)
```

For a multi-axis product:

```python
records = store.sweep(expand_grid({"n": [50, 100], "dt": [0.01, 0.005]}))
# runs 4 combinations: (50, 0.01), (50, 0.005), (100, 0.01), (100, 0.005)
```

Because `sweep` takes a plain iterable, non-product sweeps need no special
support — build the dicts however you like:

```python
# zipped / diagonal sweep
records = store.sweep([{"n": n, "dt": dt} for n, dt in zip([50, 100], [0.01, 0.005])])

# filtered product (drop unstable regions)
records = store.sweep(p for p in expand_grid(grid) if p["dt"] * p["n"] < 1.0)
```

To parallelise with Dask:

```python
from dask.distributed import Client
with Client() as dask_client:
    records = store.sweep(
        expand_grid({"n": [50, 100], "dt": [0.01, 0.005]}), client=dask_client
    )
```

## Custom metadata

Any keyword argument to `run`, `run_or_retrieve`, or `register` lands
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
