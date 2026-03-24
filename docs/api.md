# API Reference

## `Store`

```python
class Store:
    def __init__(
        self,
        results_dir: str | Path = "./results",
        db_path: str | Path = "./entropic.json",
        file_suffix: str = ".h5",
        index: IndexBackend | None = None,
    ) -> None
```

The main entry point. Creates `results_dir` if it does not exist.

| Parameter | Description |
|-----------|-------------|
| `results_dir` | Directory where result files are stored and auto-generated paths are placed. |
| `db_path` | Path to the TinyDB JSON index file. Ignored if `index` is provided. |
| `file_suffix` | Extension appended to auto-generated result filenames (e.g. `".h5"`, `".npy"`). |
| `index` | Custom `IndexBackend` instance. Pass this to use a non-TinyDB backend. |

### Methods

#### `run_or_retrieve`

```python
def run_or_retrieve(
    self,
    params: dict[str, Any],
    runner: Runner,
    **metadata: Any,
) -> RunRecord
```

The main workhorse. Checks the cache first; runs the simulation only on a miss.

Returns the cached `RunRecord` if `params` hash matches an existing record. Otherwise calls `runner(params, generated_path)`, stores the result, and returns the new `RunRecord`.

Extra keyword arguments are stored as metadata on the record.

#### `run`

```python
def run(
    self,
    params: dict[str, Any],
    runner: Runner,
    **metadata: Any,
) -> RunRecord
```

Always executes the runner, even if a cached record exists. Use this for stochastic simulations where you want multiple independent runs with identical parameters.

`elapsed_seconds` is automatically added to metadata.

#### `retrieve`

```python
def retrieve(self, params: dict[str, Any]) -> RunRecord | None
```

Look up a cached record by exact parameter match. Returns `None` on a miss.

#### `register`

```python
def register(
    self,
    params: dict[str, Any],
    result_path: str | Path,
    **metadata: Any,
) -> RunRecord
```

Index an externally-produced result file. Raises `FileNotFoundError` if `result_path` does not exist.

#### `list`

```python
def list(self, where: dict[str, Any] | None = None) -> list[RunRecord]
```

Return all records, or only those matching a partial parameter filter.

`where={"method": "rk4"}` returns every record where `method == "rk4"` regardless of other parameters.

#### `sweep`

```python
def sweep(
    self,
    params_iter: Iterable[dict[str, Any]],
    runner: Runner,
    **metadata: Any,
) -> list[RunRecord]
```

Run or retrieve results for each parameter set in the iterable. Returns a list of `RunRecord` objects in the same order as the input. Reuses cached results where possible — only calls the runner for parameter sets not already in the index.

Extra keyword arguments are stored as metadata on each new record.

#### `delete`

```python
def delete(self, params: dict[str, Any], remove_file: bool = False) -> bool
```

Delete a record by exact parameter match. If `remove_file=True`, also unlinks the result file. Returns `True` if a record was found and removed.

### Reserved parameter keys

The following keys are used internally and must not appear in your `params` dict:

- `params_hash`
- `result_path`
- `created_at`
- `metadata`

## `RunRecord`

```python
@dataclass(frozen=True)
class RunRecord:
    params: dict[str, Any]
    result_path: Path
    params_hash: str
    created_at: str
    metadata: dict[str, Any]
```

Immutable record of a completed run.

| Field | Type | Description |
|-------|------|-------------|
| `params` | `dict[str, Any]` | The simulation parameters. |
| `result_path` | `Path` | Path to the result file on disk. |
| `params_hash` | `str` | 16-character hex hash of the parameters. |
| `created_at` | `str` | ISO 8601 UTC timestamp. |
| `metadata` | `dict[str, Any]` | Optional user-defined key-value pairs (e.g. `elapsed_seconds`, git SHA). |

### `to_dict() -> dict[str, Any]`

Serialize to a flat dict. Params are merged at the top level alongside the reserved fields.

### `from_dict(data: dict[str, Any]) -> RunRecord`  *(classmethod)*

Reconstruct from a stored flat dict. Reserved keys are extracted; everything else becomes `params`.

## Runner contract

A runner is any callable with this signature:

```python
Runner = Callable[[dict[str, Any], Path], None]
```

The library generates the result path and passes it to the runner. The runner is responsible only for writing output to that path. entropic is format-agnostic — HDF5, NumPy, Parquet, CSV, anything works.

```python
def my_runner(params: dict, result_path: Path) -> None:
    # compute something using params
    # write results to result_path
    ...
```

## Custom index backends

Any class implementing the `IndexBackend` protocol can be passed as the `index` argument to `Store`:

```python
class IndexBackend(Protocol):
    def find_by_hash(self, params_hash: str) -> RunRecord | None: ...
    def find_by_params(self, params: dict[str, Any]) -> list[RunRecord]: ...
    def insert(self, record: RunRecord) -> None: ...
    def all(self) -> list[RunRecord]: ...
    def delete_by_hash(self, params_hash: str) -> bool: ...
```

Minimal example (in-memory, non-persistent):

```python
class MemoryIndex:
    def __init__(self) -> None:
        self._records: dict[str, RunRecord] = {}

    def find_by_hash(self, params_hash: str) -> RunRecord | None:
        return self._records.get(params_hash)

    def find_by_params(self, params: dict) -> list[RunRecord]:
        return [r for r in self._records.values() if all(r.params.get(k) == v for k, v in params.items())]

    def insert(self, record: RunRecord) -> None:
        self._records[record.params_hash] = record

    def all(self) -> list[RunRecord]:
        return list(self._records.values())

    def delete_by_hash(self, params_hash: str) -> bool:
        return self._records.pop(params_hash, None) is not None

store = Store(index=MemoryIndex())
```

## Parameter hashing

Parameters are normalized before hashing to ensure stability across Python runs:

- **Dict keys** are sorted recursively.
- **Floats** are rounded to 12 decimal digits (suppresses IEEE 754 noise).
- **Enums** are replaced by their `.value`.
- **Lists and tuples** preserve order; each element is normalized.
- **Everything else** falls back to `str()`.

The normalized structure is serialized to compact JSON and hashed with SHA-256. The hash is the first 16 hex characters (64 bits).

Two calls with `{"dt": 0.1, "n": 100}` and `{"n": 100, "dt": 0.1}` produce the same hash.
