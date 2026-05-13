"""Store — the main entry point for managing simulation runs."""

from collections.abc import Iterable, Callable
from pathlib import Path
from time import time
from typing import Any, TypeVar, Generic
import json

from sqlalchemy import NullPool, create_engine, delete, insert, select, update
from sqlalchemy.orm import Session

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

        store.register(
            params={"n": 100, "dt": 0.01, "method": "rk4"},
            result_file="./results/my_run.h5",
        )

        all_rk4 = store.list(where={"method": "rk4"})
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

    def _hash_params(self, params: dict[str, Any]) -> str:
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
        self, params_iter: Iterable[dict[str, Any]], **custom_data: Any
    ) -> list[ModelT]:
        """Run or retrieve results for each parameter set in the iterable.

        Args:
            params_iter: Iterable of parameter dicts to sweep over.
            **custom_data: Forwarded to each ``run_or_retrieve`` call.

        Returns:
            List of model instances in the same order as the input.
        """
        # TODO: allow concurrent run_or_retrieve
        results = []
        for params in params_iter:
            results.append(self.run_or_retrieve(params, **custom_data))
        return results

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

    def list(self, where: dict[str, Any] | None = None) -> list[ModelT]:
        """List records, optionally filtered by exact column match.

        Args:
            where: If provided, only return records where all specified
                column-value pairs match (passed to SQLAlchemy
                ``filter_by``). Keys must be column names on ``result_cls``.

        Returns:
            List of matching model instances.
        """
        with self._get_session(self._db_url) as db:
            stmt = select(self._result_cls)
            if where is not None:
                stmt = stmt.filter_by(**where)
            return list(db.execute(stmt).scalars())

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
