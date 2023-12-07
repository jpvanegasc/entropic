import pandas as pd

from entropic.sources import DefaultSample, BaseSample
from entropic.sources.fields import DataSource


def test_default_sample_data_source():
    data_field = {
        "file_path": "tests/mocks/kinematic1.csv",
        "raw": pd.read_csv("tests/mocks/kinematic1.csv"),
    }
    sample = DefaultSample(data=data_field)
    assert sample.data
    assert str(sample.data.file_path) == data_field["file_path"]
    assert not sample.data.raw.empty


def test_get_source_fields(mock_data_frame):
    class TestSample(BaseSample):
        data_field_1: DataSource
        data_field_2: DataSource
        int_field: int

    test = TestSample(
        data_field_1=DataSource(file_path="path", raw=mock_data_frame),
        data_field_2=DataSource(file_path="other/path", raw=mock_data_frame),
        int_field=1,
    )
    assert test._get_data_source_fields() == ["data_field_1", "data_field_2"]


def test_equality(mock_data_frame):
    class TestSample(BaseSample):
        data: DataSource

    sample = DefaultSample(data=DataSource(file_path="path", raw=mock_data_frame))

    assert sample != "not a sample"
    assert sample == DefaultSample(
        data=DataSource(file_path="path", raw=mock_data_frame)
    )
    assert sample != TestSample(data=DataSource(file_path="path", raw=mock_data_frame))
