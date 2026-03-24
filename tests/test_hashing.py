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


def test_none_value():
    """None values produce a deterministic hash."""
    h1 = hash_params({"x": None})
    h2 = hash_params({"x": None})
    assert h1 == h2
    assert len(h1) == 16


def test_bool_vs_int():
    """True hashes differently from 1 (json: true vs 1)."""
    h_bool = hash_params({"flag": True})
    h_int = hash_params({"flag": 1})
    assert h_bool != h_int


def test_empty_dict():
    """Empty params produce a valid hash."""
    h = hash_params({})
    assert len(h) == 16
    assert all(c in "0123456789abcdef" for c in h)


def test_tuple_treated_as_list():
    """Tuples are normalized to lists before hashing."""
    h_tuple = hash_params({"x": (1, 2, 3)})
    h_list = hash_params({"x": [1, 2, 3]})
    assert h_tuple == h_list


def test_str_fallback():
    """Unknown types fall back to str()."""

    class Custom:
        def __str__(self) -> str:
            return "custom_value"

    h = hash_params({"x": Custom()})
    assert len(h) == 16
