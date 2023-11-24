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
