def test_minimal():
    from minimal import Process
    from entropic import results

    pipeline = Process()
    pipeline.run()

    assert results.all
    assert results.all == [
        {
            "source_path": "tests/mocks/",
            "samples": [{"data": "kinematic1.csv"}, {"data": "kinematic1.csv"}],
        }
    ]
