def test_minimal():
    from minimal import Process
    from entropic import results

    pipeline = Process()
    pipeline.run()

    assert results.all
    assert results.all == [{"path": "tests/mocks/"}]
