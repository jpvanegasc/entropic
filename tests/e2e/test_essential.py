import pytest
import pandas as pd

from entropic import results
from entropic.process import Pipeline
from entropic.sources import Iteration


@pytest.fixture
def run_essential_pipeline():
    class Process(Pipeline):
        source_path = "tests/mocks/"
        extract_with = pd.read_csv

    pipeline = Process()
    pipeline.run()


def test_essential(run_essential_pipeline):
    assert len(results.all) == 1

    result = results.all[0]
    assert isinstance(result, Iteration)
    assert len(result.samples) == 2

    for sample in result.samples:
        assert sample.data
        assert sample.data.file_path
        assert isinstance(sample.data.raw, pd.DataFrame)

    assert result.model_dump() == {
        "samples": [
            {
                "data": {
                    "file_path": "tests/mocks/kinematic2.csv",
                    "raw": "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",
                    "filetype": "csv",
                }
            },
            {
                "data": {
                    "file_path": "tests/mocks/kinematic1.csv",
                    "raw": "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",
                    "filetype": "csv",
                }
            },
        ],
        "source_path": "tests/mocks/",
    }
