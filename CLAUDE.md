# CLAUDE.md

## Project overview

`entropic` is a simulation-agnostic run cache library. It manages the mapping **parameters → result file** without knowing or caring what's inside the result files. The core workflow is `run_or_retrieve`: given a set of parameters and a runner callable, return a cached result or execute the simulation and cache it.

This is v2. The library is published on PyPI as `entropic`.

## Tech stack

- **Language**: Python 3.10+
- **Dependencies**: TinyDB (JSON-file database for metadata indexing)
- **Build system**: uv_build
- **Testing**: pytest
- **Linting**: ruff (pyflakes, pycodestyle, isort, bugbear)
- **Type checking**: mypy (strict mode)
- **Code quality (format, linting, type checking**: pre-commit

## Architecture

```
src/entropic/
├── __init__.py    # Public API: Store, RunRecord
├── store.py       # Store class — main entry point (run, retrieve, run_or_retrieve, sweep, register, list, delete)
├── record.py      # RunRecord frozen dataclass — serialization to/from flat dicts
├── hashing.py     # Deterministic parameter hashing (SHA-256 of normalized JSON)
├── index.py       # IndexBackend protocol + TinyDBIndex default implementation
├── logging.py     # Centralized logger (NullHandler default)
└── py.typed       # PEP 561 marker
```

### Key design decisions

- **Params are stored as flat TinyDB fields**, not nested under a `"params"` key. This enables field-by-field partial queries via `store.list(where={"method": "rk4"})`. Reserved keys (`params_hash`, `result_path`, `created_at`, `metadata`) are mixed in at the same level — user param names must not collide with these.
- **IndexBackend is a Protocol** (runtime_checkable). TinyDB ships as default, but any backend implementing 5 methods works. This is the extension point for SQLite, Postgres, S3, etc.
- **Parameter hashing** normalizes before hashing: sorts dict keys, rounds floats to 12 digits, converts enums to `.value`, falls back to `str()`. The hash is the first 16 hex chars of SHA-256 — deterministic across Python runs.
- **Runner contract**: `Callable[[dict, Path], None]`. The library generates the result path; the runner just writes to it. This keeps entropic format-agnostic (HDF5, NumPy, Parquet, CSV, whatever).
- **`run()` always creates a new record** (even for duplicate params). `run_or_retrieve()` deduplicates via hash lookup first. This distinction matters for stochastic simulations.

### Data flow

```
User params (dict)
    → hash_params() → 16-char hex hash
    → TinyDBIndex.find_by_hash()
        → cache hit: return RunRecord
        → cache miss: runner(params, generated_path)
            → TinyDBIndex.insert(RunRecord)
            → return RunRecord
```

### TinyDB document shape

```json
{
  "params_hash": "a3f8c1d2e4b6f7a8",
  "result_path": "./results/1769854174.763568_a3f8c1d2e4b6f7a8.h5",
  "created_at": "2025-06-15T10:30:00+00:00",
  "metadata": { "elapsed_seconds": 1.234 },
  "n": 100,
  "steps": 5000,
  "dt": 0.01
}
```

User params (`n`, `steps`, `dt`) are flattened alongside reserved fields.

## Commands

```bash
# Install (editable, with dev deps)
uv sync --group dev

# Run tests
uv run pytest tests/ -v

# Lint + format + type check
uv run pre-commit run --all-files
```

## Conventions

- All public API is exposed through `entropic/__init__.py` (`Store`, `RunRecord`).
- Use frozen dataclasses for data objects.
- Type hints everywhere — mypy strict mode is enabled.
- The `IndexBackend` protocol lives in `index.py` alongside the default `TinyDBIndex`.

## Testing

- **`test_e2e.py`** — one big end-to-end test using a self-contained logistic growth ODE runner. Exercises the full workflow (all Store methods, record serialization, index persistence, logging). This alone provides ≥70% coverage.
- **`test_hashing.py`** — unit tests for hashing edge cases (None, bools vs ints, empty dicts, tuples, str fallback, float normalization, enums).
- **`test_record.py`** — unit tests for RunRecord serialization (roundtrip, flattening, reserved keys, immutability).
- **`test_store.py`** — edge-case unit tests only (runner exceptions, delete on missing files, metadata forwarding, FileNotFoundError on register).
- **`test_logging.py`** — verifies logger name and that users can capture messages.
- All tests use `tmp_path` for filesystem isolation. Runner stubs write plain text or CSV (no numpy dependency in tests).
- Coverage threshold: 80% (enforced in CI).

## Roadmap / future work

- **Additional backends**: SQLiteIndex, PostgresIndex, S3-backed storage
- ~~**Parameter sweeps**~~: shipped as `store.sweep()` in v2
- **Async runners**: support for `async def runner(params, path)` and concurrent execution
- **CLI**: `entropic list`, `entropic run`, `entropic gc` for managing results from the terminal
- **Result comparison utilities**: diff two runs, plot parameter sensitivity
- **Provenance tracking**: git SHA, environment info, dependency versions auto-captured
- **Migration from v1**: helper to import existing v1 index files
