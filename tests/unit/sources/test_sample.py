from entropic.sources import Sample


def test_sample_data_source():
    file = "tests/mocks/kinematic1.csv"
    sample = Sample(data=file)
    assert sample.data
    assert sample.data.filename == file
    assert sample.data.filetype == "csv"
