"""Tests for parameter hashing."""

import enum

from entropic.hashing import hash_params


class Color(enum.Enum):
    RED = "red"
    BLUE = "blue"


def test_deterministic():
    """Same params always produce the same hash."""
    params = {"a": 1, "b": 2.0, "c": "hello"}
    assert hash_params(params) == hash_params(params)


def test_key_order_invariant():
    """Dict key order doesn't affect the hash."""
    h1 = hash_params({"a": 1, "b": 2})
    h2 = hash_params({"b": 2, "a": 1})
    assert h1 == h2


def test_float_normalization():
    """Small floating point noise doesn't change the hash."""
    h1 = hash_params({"x": 1.0})
    h2 = hash_params({"x": 1.0 + 1e-15})
    assert h1 == h2


def test_float_meaningful_difference():
    """Meaningful float differences produce different hashes."""
    h1 = hash_params({"x": 1.0})
    h2 = hash_params({"x": 1.001})
    assert h1 != h2


def test_enum_handling():
    """Enums are hashed by their value."""
    h1 = hash_params({"color": Color.RED})
    h2 = hash_params({"color": "red"})
    assert h1 == h2


def test_nested_dicts():
    """Nested dicts are normalized recursively."""
    h1 = hash_params({"cfg": {"z": 1, "a": 2}})
    h2 = hash_params({"cfg": {"a": 2, "z": 1}})
    assert h1 == h2


def test_list_order_matters():
    """List element order affects the hash (unlike dicts)."""
    h1 = hash_params({"items": [1, 2, 3]})
    h2 = hash_params({"items": [3, 2, 1]})
    assert h1 != h2


def test_different_params_different_hash():
    """Different parameters produce different hashes."""
    h1 = hash_params({"n": 10})
    h2 = hash_params({"n": 20})
    assert h1 != h2


def test_hash_length():
    """Hash is 16 hex characters."""
    h = hash_params({"x": 42})
    assert len(h) == 16
    assert all(c in "0123456789abcdef" for c in h)
