import pytest
import pandas as pd
from pydantic import ValidationError

from entropic.sources.fields import DataSource

TEST_DATA_FRAME = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})


def test_raw_validation_and_serialization():
    with pytest.raises(ValidationError) as error:
        DataSource(file_path="", raw="invalid df")
    assert "unable to load a `pandas.DataFrame` object from raw" in str(error.value)

    valid = DataSource(file_path="some_path", raw=TEST_DATA_FRAME)
    assert isinstance(valid.model_dump()["raw"], str)


def test_comparisons():
    assert DataSource(file_path="some_path", raw=TEST_DATA_FRAME) == DataSource(
        file_path="some_path", raw=TEST_DATA_FRAME
    )
    assert DataSource(file_path="some_path", raw=TEST_DATA_FRAME) != DataSource(
        file_path="other_path", raw=TEST_DATA_FRAME
    )
    assert (
        DataSource(file_path="some_path", raw=TEST_DATA_FRAME)
        != "not a data source instance"
    )


def test_dump_and_load_compressed():
    compressed = DataSource._dump_data_frame(TEST_DATA_FRAME)
    assert compressed == "eJyrVkrOzzFUsqpWMlCyMtRRAjKNanVAgkZQQWOwoEltLQDyJQrM"

    decompressed = DataSource._load_data_frame(compressed)
    assert isinstance(decompressed, pd.DataFrame)
    assert (
        from_load.all() == from_test.all()
        for from_load, from_test in zip(decompressed.all(), TEST_DATA_FRAME.all())
    )
