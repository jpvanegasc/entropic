import pytest

from entropic.process import Pipeline
from entropic.process import exceptions


def test_required_definitions():
    with pytest.raises(exceptions.PipelineSetupError) as error:
        Pipeline()
    assert str(error.value) == "can't instantiate Pipeline directly"

    with pytest.raises(exceptions.PipelineSetupError) as error:

        class TestNoExtract(Pipeline):
            source_path = "test/path"

    assert str(error.value) == "either 'extract_with' or 'extract' must be defined"

    with pytest.raises(exceptions.PipelineSetupError) as error:

        class TestNoSource(Pipeline):
            extract_with = lambda x: x  # noqa: E731

    assert str(error.value) == "either 'source_path' or 'filepaths' must be defined"
