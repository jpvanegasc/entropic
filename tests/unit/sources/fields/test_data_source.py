import pytest

from pydantic import ValidationError

from entropic.sources.fields import DataSource


def test_raw_validation_and_serialization():
    with pytest.raises(ValidationError) as error:
        DataSource(file_path="", raw="invalid df")
    assert "unable to load a `pandas.DataFrame` object from raw" in str(error.value)
