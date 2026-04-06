"""Store — the main entry point for managing simulation runs."""

from collections.abc import Iterable, Callable, Generator, Iterator
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Any

from entropic.hashing import hash_params
from entropic.index import IndexBackend, TinyDBIndex
from entropic.logging import logger
from entropic.record import RESERVED_KEYS, RunRecord

Runner = Callable[[dict[str, Any], Path], None]
MapFunction = Callable[[RunRecord], Any]


class Store:
    """Simulation-agnostic run cache.

    Manages the mapping: parameters → result file.

    Usage::

        store = Store("./results", "./runs.json")

        # Callable-based: run or retrieve
        def my_sim(params, result_path):
            # ... write results to result_path ...
            pass

        record = store.run_or_retrieve(
            params={"n": 100, "dt": 0.01, "method": "rk4"},
            runner=my_sim,
        )
        # record.result_path → Path("./results/a3f8c1d2e4b6f7a8.h5")

        # Manual registration
        store.register(
            params={"n": 100, "dt": 0.01, "method": "rk4"},
            result_path="./results/my_run.h5",
        )

        # Query
        all_rk4 = store.list(where={"method": "rk4"})
    """

    def __init__(
        self,
        results_dir: str | Path = "./results",
        db_path: str | Path = "./entropic.json",
        file_suffix: str = ".h5",
        index: IndexBackend | None = None,
    ) -> None:
        """Initialize a Store.

        Args:
            results_dir: Directory where result files are stored/created.
            db_path: Path to the index file (TinyDB JSON by default).
            file_suffix: Extension for auto-generated result filenames.
            index: Custom index backend. If None, uses TinyDB at db_path.
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.file_suffix = file_suffix
        self._index: IndexBackend = index or TinyDBIndex(db_path)

    def _validate_params(self, params: dict[str, Any]) -> None:
        conflicts = RESERVED_KEYS & params.keys()
        if conflicts:
            raise ValueError(
                f"params contains reserved key(s): {sorted(conflicts)}. "
                f"Reserved keys are: {sorted(RESERVED_KEYS)}."
            )

    def retrieve(self, params: dict[str, Any]) -> RunRecord | None:
        """Look up a cached run by exact parameter match.

        Args:
            params: The simulation parameters to look up.

        Returns:
            RunRecord if found, None otherwise.

        Raises:
            ValueError: If params contains a reserved key.
        """
        self._validate_params(params)
        h = hash_params(params)
        record = self._index.find_by_hash(h)
        if record is not None:
            logger.info("Cache hit for hash %s", h)
        return record

    def run(
        self,
        params: dict[str, Any],
        runner: Runner,
        **metadata: Any,
    ) -> RunRecord:
        """Always run the simulation (even if cached) and register the result.

        Args:
            params: Simulation parameters passed to the runner.
            runner: Callable(params, result_path) that executes the simulation.
            **metadata: Optional key-value pairs stored alongside the record
                        (e.g. wall_time, git_sha, notes).

        Returns:
            RunRecord for the completed run.

        Raises:
            ValueError: If params contains a reserved key.
        """
        self._validate_params(params)
        h = hash_params(params)
        result_path = self._generate_result_path(h)

        start = time()
        runner(params, result_path)
        elapsed = time() - start

        metadata.setdefault("elapsed_seconds", round(elapsed, 4))

        record = RunRecord(
            params=params,
            result_path=result_path,
            params_hash=h,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )
        self._index.insert(record)
        logger.info("Run completed in %.3fs → %s", elapsed, result_path)
        return record

    def run_or_retrieve(
        self,
        params: dict[str, Any],
        runner: Runner,
        **metadata: Any,
    ) -> RunRecord:
        """Retrieve from cache if available, otherwise run and cache.

        This is the main workhorse method.

        Args:
            params: Simulation parameters.
            runner: Callable(params, result_path) that executes the simulation.
            **metadata: Optional metadata for the run record.

        Returns:
            RunRecord (either from cache or freshly created).
        """
        existing = self.retrieve(params)
        if existing is not None:
            return existing
        return self.run(params, runner, **metadata)

    def sweep(
        self,
        params_iter: Iterable[dict[str, Any]],
        runner: Runner,
        **metadata: Any,
    ) -> Generator[RunRecord, None, None]:
        """Run or retrieve results for each parameter set in the iterable.

        Args:
            params_iter: Iterable of parameter dicts to sweep over.
            runner: Callable(params, result_path) that executes the simulation.
            **metadata: Optional metadata passed to each run.

        Returns:
            Generator of RunRecords in the same order as the input.
        """
        # TODO: allow concurrent run_or_retrieve
        for params in params_iter:
            yield self.run_or_retrieve(params, runner, **metadata)

    def map(
        self,
        function: MapFunction,
        params_iter: Iterable[dict[str, Any]],
        runner: Runner,
        **metadata: Any,
    ) -> Iterator[Any]:
        """Apply `function` to every result of run_or_retrieve for each parameter set in
        the iterable.

        Args:
            function: Callable(run_record) that performs a operation on top of a run
                record.
            params_iter: Iterable of parameter dicts to sweep over.
            runner: Callable(params, result_path) that executes the simulation.
            **metadata: Optional metadata passed to each run.

        Returns:
            Generator of the results of function(record) for each parameter set
        """
        # TODO: validate once concurrent sweep is in place
        return map(function, self.sweep(params_iter, runner, **metadata))

    def register(
        self,
        params: dict[str, Any],
        result_path: str | Path,
        **metadata: Any,
    ) -> RunRecord:
        """Manually register an externally-produced result file.

        Use this when you run simulations outside the library and want
        to index the results for later retrieval.

        Args:
            params: The parameters that produced this result.
            result_path: Path to the existing result file.
            **metadata: Optional metadata.

        Returns:
            RunRecord for the registered result.

        Raises:
            FileNotFoundError: If result_path does not exist.
            ValueError: If params contains a reserved key.
        """
        self._validate_params(params)
        result_path = Path(result_path)
        if not result_path.exists():
            raise FileNotFoundError(f"Result file not found: {result_path}")

        h = hash_params(params)
        record = RunRecord(
            params=params,
            result_path=result_path,
            params_hash=h,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )
        self._index.insert(record)
        logger.info("Registered %s → %s", h, result_path)
        return record

    def list(self, where: dict[str, Any] | None = None) -> list[RunRecord]:
        """List run records, optionally filtered by partial parameter match.

        Args:
            where: If provided, only return records where all specified
                   parameter key-value pairs match. Supports subset matching,
                   e.g. ``where={"street_length": 500}`` returns all runs
                   with that street length regardless of other parameters.

        Returns:
            List of matching RunRecord objects.
        """
        if where is None:
            return self._index.all()
        return self._index.find_by_params(where)

    def delete(self, params: dict[str, Any], remove_file: bool = False) -> bool:
        """Delete a run record by exact parameter match.

        Args:
            params: The exact parameters of the run to delete.
            remove_file: If True, also delete the result file from disk.

        Returns:
            True if a record was found and deleted.

        Raises:
            ValueError: If params contains a reserved key.
        """
        self._validate_params(params)
        h = hash_params(params)
        record = self._index.find_by_hash(h)
        success = self._index.delete_by_hash(h)
        if success and remove_file and record is not None:
            try:
                record.result_path.unlink(missing_ok=True)
                logger.info("Deleted result file: %s", record.result_path)
            except OSError as e:
                logger.warning("Could not delete result file: %s", e)
        return success

    def _generate_result_path(self, params_hash: str) -> Path:
        """Generate a unique result file path."""
        # Use timestamp + hash to avoid collisions while being human-readable
        ts = f"{time():.6f}"
        return self.results_dir / f"{ts}_{params_hash}{self.file_suffix}"
