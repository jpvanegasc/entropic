import pytest

from entropic.sources.fields import DataSource


def test_valid_filetypes():
    with pytest.raises(ValueError) as error:
        DataSource("txt")
    assert str(error.value) == "unsupported filetype 'txt'"
