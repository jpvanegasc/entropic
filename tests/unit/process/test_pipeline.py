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

    with pytest.warns() as warnings:

        class TestSourceAndFilePaths(Pipeline):
            source_path = "test/path"
            extract_with = lambda x: x  # noqa: E731

            def filepaths(self):
                return []

        class Process(Pipeline):
            source_path = "test/path"
            extract_with = lambda x: x  # noqa: E731

            def extract(self):
                return 1

    assert len(warnings) == 2
    assert (
        str(warnings[0].message)
        == "both 'source_path' and 'filepaths' defined, ignoring 'source_path'"
    )
    assert (
        str(warnings[1].message)
        == "both 'extract_with' and 'extract' are defined, ignoring 'extract_with'"
    )


def test_default_functions():
    def my_extract_function(filename):
        return filename

    class TestDefaultExtract(Pipeline):
        source_path = "test/path"
        extract_with = my_extract_function

    assert TestDefaultExtract.extract_with == my_extract_function
    assert TestDefaultExtract.filepaths is not None

    class TestCustomFilepaths(Pipeline):
        extract_with = my_extract_function

        def filepaths(self):
            return ["file"]

    assert (
        TestCustomFilepaths.source_path
        == "<test_default_functions.<locals>.TestCustomFilepaths.filepaths>"
    )
