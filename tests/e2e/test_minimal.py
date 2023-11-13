def test_minimal():
    from minimal import Pipeline  # noqa: F401
    from entropic import results

    assert results.all == []
