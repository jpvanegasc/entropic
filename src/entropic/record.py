"""RunRecord — immutable record of a completed simulation run."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MANDATORY_KEYS: frozenset[str] = frozenset({"params_hash", "result_path", "created_at"})
RESERVED_KEYS: frozenset[str] = frozenset(MANDATORY_KEYS | {"metadata"})


@dataclass(frozen=True)
class RunRecord:
    """A record of a completed simulation run.

    Attributes:
        params: The simulation parameters used for this run.
        result_path: Path to the result file on disk.
        params_hash: Deterministic hash of the parameters (hex string).
        created_at: ISO 8601 timestamp of when the record was created.
        metadata: Optional user-defined metadata (e.g. wall time, git hash).
    """

    params: dict[str, Any]
    result_path: Path
    params_hash: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for storage."""
        return {
            "params_hash": self.params_hash,
            "result_path": str(self.result_path),
            "created_at": self.created_at,
            "metadata": self.metadata,
            **self.params,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunRecord":
        """Reconstruct from a stored dict."""
        if missing := (MANDATORY_KEYS - set(data.keys())):
            raise ValueError(
                f"param 'data' must be a valid RunRecord:"
                f" fields {missing} have to be present"
            )

        params = {k: v for k, v in data.items() if k not in RESERVED_KEYS}
        return cls(
            params=params,
            result_path=Path(data["result_path"]),
            params_hash=data["params_hash"],
            created_at=data["created_at"],
            metadata=data.get("metadata", {}),
        )
