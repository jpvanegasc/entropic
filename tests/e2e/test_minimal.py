def test_minimal():
    from minimal import Process
    from entropic import results
    from entropic.sources import Iteration

    pipeline = Process()
    pipeline.run()

    assert len(results.all) == 1

    result = results.all[0]
    assert isinstance(result, Iteration)
    assert result.dump() == {
        "samples": [{"data": "kinematic1.csv"}, {"data": "kinematic1.csv"}],
        "source_path": "tests/mocks/",
    }
