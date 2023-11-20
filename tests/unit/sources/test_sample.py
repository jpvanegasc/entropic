import pandas as pd

from entropic.sources import Sample


def test_sample_data_source():
    data_field = {
        "file_path": "tests/mocks/kinematic1.csv",
        "raw": pd.read_csv("tests/mocks/kinematic1.csv"),
    }
    sample = Sample(data=data_field)
    assert sample.data
    assert sample.data.file_path == data_field["file_path"]
    assert sample.data.filetype == "csv"
    assert not sample.data.raw.empty
