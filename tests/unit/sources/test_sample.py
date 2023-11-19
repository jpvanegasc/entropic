from entropic.sources import Sample


def test_sample_data_source():
    data_field = {"file_path": "tests/mocks/kinematic1.csv", "raw": "raw-data"}
    sample = Sample(data=data_field)
    assert sample.data
    assert sample.data.file_path == data_field["file_path"]
    assert sample.data.filetype == "csv"
    assert sample.data.raw == data_field["raw"]
