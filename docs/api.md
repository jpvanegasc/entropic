# API Reference

## `Store`

```python
class Store(Generic[ModelT]):
    def __init__(
        self,
        runner: Callable[[dict[str, Any]], None],
        result_cls: type[ModelT],
        results_dir: str | Path = "./results",
        file_suffix: str = ".h5",
        db_url: str = "sqlite:///db.sqlite3",
    ) -> None
```

The main entry point. Creates `results_dir` if it does not exist and runs
`metadata.create_all` on the engine derived from `db_url`.

| Parameter     | Description                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------- |
| `runner`      | Callable invoked as `runner(params)`. The Store injects `params["result_file"]` before calling. |
| `result_cls`  | User-defined SQLAlchemy model subclassing `entropic.Base`. Columns must mirror `params` keys.   |
| `results_dir` | Directory where result files (and ingest sidecars) live. Created if missing.                    |
| `file_suffix` | Extension appended to auto-generated result filenames (e.g. `".h5"`, `".npy"`, `".csv"`).       |
| `db_url`      | SQLAlchemy URL for the backing database. SQLite by default; any dialect SQLAlchemy supports.    |

`Store` is generic in `ModelT`; methods that return a record are typed as
`ModelT` so your editor sees the user-defined columns.

### Methods

#### `run_or_retrieve`

```python
def run_or_retrieve(
    self,
    params: dict[str, Any],
    **custom_data: Any,
) -> ModelT
```

Returns the cached row if `params` hashes to an existing primary key. Otherwise
calls `run` and persists the new row. `custom_data` is forwarded to the runner
and stored on the row's `custom_data` column when a run actually happens.

#### `run`

```python
def run(
    self,
    params: dict[str, Any],
    **custom_data: Any,
) -> ModelT
```

Always executes the runner and persists. Same params hash to the same primary
key, so a re-run overwrites the existing row (and the file at the same path).

`elapsed_seconds` is automatically added to `custom_data`.

#### `retrieve`

```python
def retrieve(self, params: dict[str, Any]) -> ModelT | None
```

Look up a row by exact parameter match. Returns `None` on a miss.

If `params` contains an explicit `id` it is used verbatim and hashing is
skipped; otherwise the reserved keys (`result_file`, `created_at`, `custom_data`)
are stripped from a copy and the rest is hashed.

#### `register`

```python
def register(
    self,
    params: dict[str, Any],
    result_file: str | Path,
    **custom_data: Any,
) -> ModelT
```

Index an externally-produced result file. Raises `FileNotFoundError` if
`result_file` does not exist.

#### `sweep`

```python
def sweep(
    self,
    params_iter: Iterable[dict[str, Any]],
    **custom_data: Any,
) -> list[ModelT]
```

Run or retrieve results for each parameter set. Returns the rows in input
order; cached entries are reused, only misses invoke the runner.

#### `delete`

```python
def delete(self, params: dict[str, Any], remove_file: bool = False) -> bool
```

Delete a row by exact parameter match. If `remove_file=True`, also unlinks
the result file. Returns `True` if a row was removed.

## `Base` — record schema

```python
from entropic import Base, Mapped, mapped_column

class SimResult(Base):
    __tablename__ = "results"

    # your columns — must match keys in your params dicts
    n: Mapped[int]
    dt: Mapped[float]
```

`Base` is a SQLAlchemy `DeclarativeBase` subclass that defines four reserved
columns:

| Column        | Type                | Description                                                            |
| ------------- | ------------------- | ---------------------------------------------------------------------- |
| `id`          | `str` (PK)          | 16-character hex hash of params.                                       |
| `result_file` | `str`               | Path to the result file on disk.                                       |
| `created_at`  | `datetime`          | UTC timestamp, default `datetime.utcnow` at insert.                    |
| `custom_data` | `dict[str, Any]`    | Mutable JSON column. Always non-null; defaults to `{}`.                |

The four reserved column names cannot be redefined as user columns.

`Base` also provides `apply_patch(data)` and `_apply_custom_data_patch(patch)`
for partial updates: a `None` value on `custom_data` keys removes them, an
empty dict clears the column, otherwise keys are merged.

## Runner contract

```python
Runner = Callable[[dict[str, Any]], None]

def my_runner(params: dict[str, Any]) -> None:
    # params["result_file"] is the path to write to (auto-injected by the Store)
    # everything else is your simulation parameters
    ...
```

entropic is format-agnostic — HDF5, NumPy, Parquet, CSV, anything works.

## Parameter hashing

Parameters are normalized before hashing to ensure stability across Python runs:

- **Dict keys** are sorted recursively.
- **Floats** are rounded to 12 decimal digits (suppresses IEEE 754 noise).
- **Enums** are replaced by their `.value`.
- **Lists and tuples** preserve order; tuples become lists; each element is normalized.
- **Everything else** falls back to `str()`.

The normalized structure is serialized to compact JSON and hashed with SHA-256.
The first 16 hex characters (64 bits) are used as the row's primary key.

`{"dt": 0.1, "n": 100}` and `{"n": 100, "dt": 0.1}` produce the same hash.

## Reserved keys in `params`

`id`, `result_file`, `created_at`, and `custom_data` are stripped from a copy
of `params` before hashing (so passing them is harmless — they don't pollute
the hash). An explicit `id` short-circuits hashing and is used verbatim as the
primary key.

User-defined params keys must match column names on `result_cls`; extra keys
will fail the SQLAlchemy insert.
