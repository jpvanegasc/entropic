import hashlib
import json
from typing import Any


def _normalize(value: Any) -> Any:
    """Recursively normalize a value for deterministic JSON serialization.

    - Enums → their .value
    - floats → rounded to 12 significant digits (avoids IEEE 754 noise)
    - dicts → sorted by key
    - lists/tuples → preserved order, each element normalized
    - Everything else → str() fallback
    """
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, (int, bool, str, type(None))):
        return value
    if hasattr(value, "value"):  # enum-like
        return _normalize(value.value)
    return str(value)


def hash_params(params: dict[str, Any]) -> str:
    """Compute a deterministic 16-char hex hash of simulation parameters.

    The hash is stable across Python runs (no random seed involved).
    Parameters are normalized before hashing: keys sorted, floats rounded,
    enums converted to values.

    Args:
        params: Arbitrary parameter dictionary.

    Returns:
        16-character hex string (first 64 bits of SHA-256).
    """
    normalized = _normalize(params)
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
