import pytest

from entropic.process import Pipeline
from entropic.process import exceptions


def test_required_definitions():
    # Pipeline cant be instantiated
    with pytest.raises(exceptions.PipelineSetupError) as error:
        Pipeline()
    #  TODO: change
    # assert str(error.value) == "can't instantiate Pipeline directly"

    class TestNoExtract(Pipeline):
        source_path = "test/path"

    with pytest.raises(exceptions.PipelineSetupError) as error:
        TestNoExtract()
    assert str(error.value) == "either 'extract_with' or 'extract' must be defined"

    class TestNoSource(Pipeline):
        extract_with = lambda x: x  # noqa: E731

    with pytest.raises(exceptions.PipelineSetupError) as error:
        TestNoSource()
    assert str(error.value) == "either 'source_path' or 'filepaths' must be defined"
