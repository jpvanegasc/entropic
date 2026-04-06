"""Index backends for storing run metadata.

The default backend uses TinyDB (a JSON-file database).
Custom backends can be created by implementing the IndexBackend protocol.
"""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from tinydb import Query, TinyDB

from entropic.record import RunRecord


@runtime_checkable
class IndexBackend(Protocol):
    """Protocol for metadata index backends.

    Implement this to swap TinyDB for SQLite, Postgres, etc.
    """

    def find_by_hash(self, params_hash: str) -> RunRecord | None:
        """Find a run by its exact parameter hash."""
        ...

    def find_by_params(self, params: dict[str, Any]) -> list[RunRecord]:
        """Find runs matching a partial parameter dict (subset match)."""
        ...

    def insert(self, record: RunRecord) -> None:
        """Insert a new run record."""
        ...

    def all(self) -> list[RunRecord]:
        """Return all stored run records."""
        ...

    def delete_by_hash(self, params_hash: str) -> bool:
        """Delete a record by its parameter hash. Returns True if found."""
        ...


class TinyDBIndex:
    """Default index backend using TinyDB (JSON file)."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def _open(self) -> TinyDB:
        return TinyDB(str(self._db_path))

    def find_by_hash(self, params_hash: str) -> RunRecord | None:
        q = Query()
        with self._open() as db:
            result = db.get(q.params_hash == params_hash)
            if result is None:
                return None
            return RunRecord.from_dict(result)

    def find_by_params(self, params: dict[str, Any]) -> list[RunRecord]:
        with self._open() as db:
            q = Query()
            # Build compound query: all provided params must match
            conditions = [(q[k] == v) for k, v in params.items()]
            if not conditions:
                return [RunRecord.from_dict(doc) for doc in db.all()]

            combined = conditions[0]
            for cond in conditions[1:]:
                combined = combined & cond

            results = db.search(combined)
            return [RunRecord.from_dict(doc) for doc in results]

    def insert(self, record: RunRecord) -> None:
        with self._open() as db:
            db.insert(record.to_dict())

    def all(self) -> list[RunRecord]:
        with self._open() as db:
            return [RunRecord.from_dict(doc) for doc in db.all()]

    def delete_by_hash(self, params_hash: str) -> bool:
        q = Query()
        with self._open() as db:
            removed = db.remove(q.params_hash == params_hash)
            return len(removed) > 0
