def test_minimal():
    from minimal import Pipeline  # noqa: F401
    from entropic.results import Results

    assert Results.all
