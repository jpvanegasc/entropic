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
    assert (
        compressed
        == "eJy1VsuO4kYUNWARImXRGsUIpF4gK0FZ0B3shplhNFmU6QZMgBnoaWwcRS2/2hhs4/jRhm7xB1lkkezzOVlmkUU+IB+SqjLvZiKNlC4h6ta5t849t1zX8nswYCiSKlBfdeBEvCCIk7cJIh7J1UwR1AsqW4L+EypNpU9zmbUnl1nHZolvjqBwfF5AMJlIpJLFvxOnFJmvEumTfI5UZxZDJbNk9o9E9s9EsVXMfApxHskhqCQSd0KhgMMqUqtI8qNVkBva1E6yp+hBFf+Q+1WwO1X8lSr+mvoU6mN15N9WiVzaV8e6LVMkBL5Oxse1NVkiS+ZP86XnPdLnLjX7SypLFjPZ31NfIncu7cqOJvu538hH2nQ0fX4Lc4a249NvCj880lOIQYv2ZMfQ6VKBdmRbh4ATWhZc+YHsBXBZxvbMhSaLTR2ZzPJHuIj5bjG5vqLdZ7kzdUu73cdiWbfBwkUgHTqmOtNiBaHtLjaOmTLR1QDhth7ImhzIEH2kdQeGm46BQm4+NM5e08sdMfsqEMjQhzo26IES0wleVp7q2MA7MlApy1JhLxF7NBH7PyTC5Xm6HMw8fASWqXiyt0B73IXsebMI7brXPd+cOQhlKuflc4ZeblPvONlz5vyCXhK5L8Bg8E54E7dG7ufMt2hE4BIA0Afx+B6ACuAM0ADAAHUDYxy354/QfLXxX0X1eL1mwX4ezRyejdV6HTRClNFIqE5HYheaN3A/94q3rVBqDisi27tXWsNAcbrmO5NT9EXbk2EsP5kZvNMeK7Zm8WZk8HZ1rAg3KCbUhLnfqQNTvRiMVacPMRCt1vdqnX/JX/I+X28/aM1hhHi6IqMh/4it+ZrAhCIb55bETc5wJDAWilWcoa/UUT7JlYT5VGSP5G024P7Gg3gxqKpN5AOmJlRdyD+VrnFuGMtE+rBW1kUO8/J2zZTt4USrY38giYMx5CiPrqHelm9KQnWisANXsVXMNxwOmp0Phnl3oF1dwPhG8Gp7HrGvG+e1ZWHoS43aph7ehud7eWV+TDc863Jv0sd+WHugtqw7rWVFEtJVb7uK02d7xzQ3q4zSnNc6de6pFvO/tPDPpkW8Rs+tt5CERlm54NEzg9rm7gjeI9WZ4hyQE9rte22BeVhJbD/IQi3E+iZX5c4EhN3rdm1fo2SpTs9V2Arm6JqVeWfSNe/666vO4fvOob/eJWyy1+j21/H954xtK2yahoPPOlrgZXcdD7j+iqSBSUewa0B3tXndjxwY49nY5IsH5sdnH0fifoSN1lqFbvnj8R2RK7iy91OoB2eq657hl0xh9RIpxK+XfOmUIOCP0D4jiPfwy+df7J032w=="
    )

    decompressed = DataSource._load_data_frame(compressed)
    assert isinstance(decompressed, pd.DataFrame)
    assert (
        from_load.all() == from_test.all()
        for from_load, from_test in zip(decompressed.all(), TEST_DATA_FRAME.all())
    )
