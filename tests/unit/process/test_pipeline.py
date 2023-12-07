from pathlib import Path

import pytest

from entropic.process import Pipeline, exceptions
from entropic.sources import Iteration, DefaultSample


def test_required_definitions():
    with pytest.raises(exceptions.PipelineSetupError) as error:
        Pipeline()
    assert str(error.value) == "can't instantiate Pipeline directly"

    with pytest.raises(exceptions.PipelineSetupError) as error:

        class TestNoExtract(Pipeline):
            source_paths = ["test/path"]

    assert str(error.value) == "either 'extract_with' or 'extract' must be defined"

    with pytest.raises(exceptions.PipelineSetupError) as error:

        class TestNoSource(Pipeline):
            extract_with = lambda x: x  # noqa: E731

    assert (
        str(error.value)
        == "either 'source_paths' or 'get_source_paths' must be defined"
    )

    with pytest.warns() as warnings:

        class TestSourceAndFilePaths(Pipeline):
            source_paths = ["test/path"]
            extract_with = lambda x: x  # noqa: E731

            def get_source_paths(self):
                return []

        class Process(Pipeline):
            source_paths = ["test/path"]
            extract_with = lambda x: x  # noqa: E731

            def extract(self):
                return 1

    assert len(warnings) == 2
    assert (
        str(warnings[0].message)
        == "both 'source_paths' and 'get_source_paths' defined, ignoring 'source_paths'"
    )
    assert (
        str(warnings[1].message)
        == "both 'extract_with' and 'extract' are defined, ignoring 'extract_with'"
    )

    with pytest.raises(TypeError) as error:

        class BadSourcePaths(Pipeline):
            source_paths = "not-a-list"
            extract_with = lambda x: x  # noqa: E731

        BadSourcePaths()

    assert str(error.value) == "'source_paths' must be a list of path-like objects"

    with pytest.raises(TypeError) as error:

        class BadSourcePaths(Pipeline):
            source_paths = [1, 2, 3]
            extract_with = lambda x: x  # noqa: E731

        BadSourcePaths()

    assert str(error.value) == "'source_paths' must be a list of path-like objects"


def test_default_functions():
    def my_extract_function(filename):
        return filename

    class TestDefaultExtract(Pipeline):
        source_paths = ["test/path"]
        extract_with = my_extract_function

    assert TestDefaultExtract.extract_with == my_extract_function

    class TestCustomFilepaths(Pipeline):
        extract_with = my_extract_function

        def get_source_paths(self):
            return ["file"]

    assert TestCustomFilepaths.source_paths == []


def test_helpers():
    def my_extract_function(filename):
        return filename

    class TestHelpers(Pipeline):
        source_paths = ["tests/mocks"]
        extract_with = my_extract_function

    pipeline = TestHelpers()

    assert pipeline.get_source_paths() == [Path("tests/mocks")]
    assert pipeline.get_iteration() is Iteration
    assert pipeline.get_sample() is DefaultSample
    assert pipeline.get_files_from_path("tests/mocks") == [
        Path("tests/mocks/kinematic2.csv"),
        Path("tests/mocks/kinematic1.csv"),
    ]
