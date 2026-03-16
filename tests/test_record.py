"""Tests for RunRecord serialization."""

from pathlib import Path

from entropic.record import RunRecord


def test_roundtrip():
    """to_dict / from_dict is lossless."""
    record = RunRecord(
        params={"n": 10, "dt": 0.01},
        result_path=Path("./results/test.h5"),
        params_hash="abc123",
        created_at="2025-01-01T00:00:00+00:00",
        metadata={"elapsed_seconds": 1.23},
    )
    d = record.to_dict()
    restored = RunRecord.from_dict(d)
    assert restored.params == record.params
    assert restored.result_path == record.result_path
    assert restored.params_hash == record.params_hash
    assert restored.created_at == record.created_at
    assert restored.metadata == record.metadata


def test_to_dict_flattens_params():
    """Params are stored as top-level keys (not nested under 'params')."""
    record = RunRecord(
        params={"n": 10, "method": "rk4"},
        result_path=Path("./test.h5"),
        params_hash="xyz",
        created_at="2025-01-01T00:00:00+00:00",
    )
    d = record.to_dict()
    assert d["n"] == 10
    assert d["method"] == "rk4"
    assert d["params_hash"] == "xyz"


def test_reserved_keys_excluded_from_params():
    """from_dict doesn't leak reserved keys into params."""
    d = {
        "params_hash": "abc",
        "result_path": "./test.h5",
        "created_at": "2025-01-01",
        "metadata": {},
        "n": 10,
    }
    record = RunRecord.from_dict(d)
    assert "params_hash" not in record.params
    assert "n" in record.params
