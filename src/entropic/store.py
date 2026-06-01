"""Store — the main entry point for managing simulation runs."""

from collections.abc import Callable
from pathlib import Path
from time import time
from typing import Any, TypeVar, Generic, TYPE_CHECKING
import json
import itertools

from sqlalchemy import NullPool, create_engine, delete, insert, select, update
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from dask.distributed import Client
else:
    try:
        from dask.distributed import Client
    except ImportError:
        Client = None

from entropic.hashing import hash_dict
from entropic.logging import logger
from entropic.db import Base

Runner = Callable[[dict[str, Any]], None]

ModelT = TypeVar("ModelT", bound=Base)


class Store(Generic[ModelT]):
    """Simulation-agnostic run cache.

    Manages the mapping: parameters → result file.

    Usage::

        from entropic import Store, Base, Mapped

        class SimResult(Base):
            __tablename__ = "results"
            n: Mapped[int]
            dt: Mapped[float]
            method: Mapped[str]

        def my_sim(params: dict) -> None:
            # params["result_file"] is the path to write to
            with open(params["result_file"], "w") as f:
                ...

        store = Store(
            runner=my_sim,
            result_cls=SimResult,
            results_dir="./results",
            db_url="sqlite:///./runs.sqlite3",
        )

        record = store.run_or_retrieve({"n": 100, "dt": 0.01, "method": "rk4"})
        # record.result_file → "./results/a3f8c1d2e4b6f7a8.h5"
    """

    def __init__(
        self,
        runner: Runner,
        result_cls: type[ModelT],
        results_dir: str | Path = "./results",
        file_suffix: str = ".h5",
        db_url: str = "sqlite:///db.sqlite3",
    ) -> None:
        """Initialize a Store.

        Args:
            runner: Callable invoked as ``runner(params)`` to produce a result file.
                The Store injects ``params["result_file"]`` (the target path) before
                the call; the runner is responsible for writing that file.
            result_cls: User-defined SQLAlchemy model subclassing ``entropic.Base``.
                Its column names must match the keys of the ``params`` dicts passed
                to the Store (the four reserved columns ``id``, ``result_file``,
                ``created_at``, ``custom_data`` come from ``Base``).
            results_dir: Directory where result files are stored/created.
            file_suffix: Extension for auto-generated result filenames.
            db_url: SQLAlchemy URL for the backing database.
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.file_suffix = file_suffix
        self._result_cls: type[ModelT] = result_cls
        self._runner = runner
        self._db_url = db_url

        engine = create_engine(db_url, poolclass=NullPool)
        self._result_cls.metadata.create_all(engine)

    @staticmethod
    def _hash_params(params: dict[str, Any]) -> str:
        """Compute the hash for a params dict without mutating the caller's copy.

        If ``params["id"]`` is present it is used verbatim; otherwise the
        reserved keys (see ``entropic.db.Base``) are stripped from a copy
        and the remainder is hashed.
        """
        if "id" in params:
            return str(params["id"])
        hashable = {
            k: v
            for k, v in params.items()
            if k not in ("result_file", "created_at", "custom_data")
        }
        return hash_dict(hashable)

    @staticmethod
    def _get_session(db_url: str) -> Session:
        engine = create_engine(db_url, poolclass=NullPool)
        return Session(engine)

    def _run(self, params: dict[str, Any], **custom_data: Any) -> str:
        hash = self._hash_params(params)
        result_file = self._generate_result_path(hash)

        runner_params = {**params, "id": hash, "result_file": str(result_file)}

        start = time()
        self._runner(runner_params)
        elapsed = time() - start

        custom_data.setdefault("elapsed_seconds", round(elapsed, 4))
        logger.info("Run completed in %.3fs → %s", elapsed, result_file)

        with open(self.results_dir / f"{hash}.json", "w+") as f:
            payload = {**runner_params, "custom_data": custom_data}
            f.write(json.dumps(payload))

        return hash

    def _ingest_to_db(self, *results_hash: Path | str, overwrite: bool = False) -> None:
        if not results_hash:
            results = tuple(Path(self.results_dir).glob("*.json"))
        else:
            results = tuple(
                Path(self.results_dir) / f"{hash}.json" for hash in results_hash
            )

        with self._get_session(self._db_url) as db:
            for r in results:
                with open(r) as f:
                    data = json.load(f)
                Path(r).unlink()

                filepath = Path(data["result_file"])
                if not filepath.exists() or filepath.stat().st_size == 0:
                    logger.warning(
                        "File for %s missing or broken. filepath=%s",
                        data["id"],
                        filepath,
                    )
                    continue

                existing = db.scalar(
                    select(self._result_cls).where(self._result_cls.id == data["id"])
                )

                if existing is not None and not overwrite:
                    logger.info("Result for %s already computed, ignoring", data["id"])
                elif existing is not None and overwrite:
                    logger.info(
                        "Result for %s already computed, overwriting cache", data["id"]
                    )
                    db.execute(
                        update(self._result_cls)
                        .where(self._result_cls.id == data["id"])
                        .values(**data)
                    )
                else:
                    db.execute(insert(self._result_cls).values(**data))
            db.commit()

    def _generate_result_path(self, params_hash: str) -> Path:
        """Generate a unique result file path."""
        return self.results_dir / f"{params_hash}{self.file_suffix}"

    @staticmethod
    def _grid_to_iterable(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
        combinations = itertools.product(*grid.values())

        param_map = []
        for combo in combinations:
            # Re-associate the values with their keys
            p_dict = dict(zip(grid.keys(), combo, strict=False))
            param_map.append(p_dict)

        return param_map

    # Public API
    # ==========

    def retrieve(self, params: dict[str, Any]) -> ModelT | None:
        """Look up a cached run by exact parameter match.

        Args:
            params: The simulation parameters to look up. Reserved keys
                (``result_file``, ``created_at``, ``custom_data``) are
                ignored; an explicit ``id`` short-circuits hashing.

        Returns:
            The model instance if found, ``None`` otherwise.
        """
        h = self._hash_params(params)
        with self._get_session(self._db_url) as db:
            record = db.execute(
                select(self._result_cls).where(self._result_cls.id == h)
            ).scalar_one_or_none()
        if record is not None:
            logger.info("Cache hit for hash %s", h)
        return record  # type:ignore

    def run(
        self,
        params: dict[str, Any],
        **custom_data: Any,
    ) -> ModelT:
        """Always run the simulation (even if cached) and persist the result.

        Args:
            params: Simulation parameters. The Store passes a copy to the
                runner with ``id`` and ``result_file`` injected.
            **custom_data: Optional key-value pairs stored on the record's
                ``custom_data`` JSON column (e.g. ``git_sha``, ``notes``).
                ``elapsed_seconds`` is added automatically.

        Returns:
            The persisted model instance for the completed run.
        """
        h = self._run(params, **custom_data)
        self._ingest_to_db(h, overwrite=True)
        with self._get_session(self._db_url) as db:
            record = db.execute(
                select(self._result_cls).where(self._result_cls.id == h)
            ).scalar_one_or_none()
        if record is None:
            raise RuntimeError("Failed to save record to cache")
        return record  # type:ignore

    def run_or_retrieve(
        self,
        params: dict[str, Any],
        **custom_data: Any,
    ) -> ModelT:
        """Retrieve from cache if available, otherwise run and cache.

        This is the main workhorse method.

        Args:
            params: Simulation parameters.
            **custom_data: Forwarded to ``run`` on cache miss; ignored on hit.

        Returns:
            The model instance, either from cache or freshly created.
        """
        existing = self.retrieve(params)
        if existing is not None:
            return existing
        return self.run(params, **custom_data)

    def sweep(
        self, grid: dict[str, list[Any]], client: "Client | None" = None
    ) -> list[ModelT]:
        """Run or retrieve results for all parameter combinations in the grid.

        Args:
            grid: Mapping of parameter names to lists of values. All combinations
                are expanded via ``itertools.product``. For a single-axis sweep,
                wrap fixed values in a one-element list.
            client: Optional Dask ``distributed.Client``. When provided, new runs
                are dispatched as futures; falls back to serial execution if the
                client raises.

        Returns:
            List of model instances for every combination in the grid.
            Order matches the ``itertools.product`` expansion of ``grid``.
        """
        hash_to_param_map: dict[str, dict[str, Any]] = {
            self._hash_params(p): p for p in self._grid_to_iterable(grid)
        }

        with self._get_session(self._db_url) as db:
            existing = set(
                db.execute(
                    select(self._result_cls.id).where(
                        self._result_cls.id.in_(hash_to_param_map.keys())
                    )
                ).scalars()
            )

        to_run = [p for h, p in hash_to_param_map.items() if h not in existing]

        logger.info(
            "Found %d results in cache, will run and cache %d runs",
            len(existing),
            len(to_run),
        )

        if client is not None:
            try:
                futures = client.map(self._run, to_run, pure=False)
                client.gather(futures)
            except Exception:
                logger.warning(
                    "Failed to run using distributed client, using naive implementation instead"
                )
                for p in to_run:
                    self._run(p)
        else:
            for p in to_run:
                self._run(p)

        self._ingest_to_db(
            *[h for h in hash_to_param_map.keys() if h not in existing], overwrite=True
        )

        with self._get_session(self._db_url) as db:
            return list(
                db.execute(
                    select(self._result_cls).where(
                        self._result_cls.id.in_(list(hash_to_param_map.keys()))
                    )
                ).scalars()
            )

    def register(
        self,
        params: dict[str, Any],
        result_file: str | Path,
        **custom_data: Any,
    ) -> ModelT:
        """Manually register an externally-produced result file.

        Use this when you run simulations outside the library and want
        to index the results for later retrieval.

        Args:
            params: The parameters that produced this result.
            result_file: Path to the existing result file.
            **custom_data: Optional key-value pairs stored on the record's
                ``custom_data`` JSON column.

        Returns:
            The persisted model instance.

        Raises:
            FileNotFoundError: If ``result_file`` does not exist.
        """
        hash = self._hash_params(params)
        result_file = Path(result_file)
        if not result_file.exists():
            raise FileNotFoundError(f"Result file not found: {result_file}")

        record_fields = {**params, "id": hash, "result_file": str(result_file)}

        with self._get_session(self._db_url) as db:
            record = self._result_cls(**record_fields, custom_data=custom_data)
            db.add(record)
            db.commit()
            db.refresh(record)
        logger.info("Registered %s → %s", hash, result_file)
        return record

    def delete(self, params: dict[str, Any], remove_file: bool = False) -> bool:
        """Delete a record by exact parameter match.

        Args:
            params: The parameters of the run to delete.
            remove_file: If True, also delete the result file from disk.

        Returns:
            True if a record was found and deleted, False otherwise.
        """
        hash = self._hash_params(params)
        with self._get_session(self._db_url) as db:
            existing = db.scalar(
                select(self._result_cls).where(self._result_cls.id == hash)
            )
            if existing is None:
                return False
            file_path = Path(existing.result_file) if remove_file else None
            db.execute(delete(self._result_cls).where(self._result_cls.id == hash))
            db.commit()

        if file_path is not None and file_path.exists():
            try:
                file_path.unlink(missing_ok=True)
                logger.info("Deleted result file: %s", file_path)
            except OSError as e:
                logger.warning("Could not delete result file: %s", e)
        return True
