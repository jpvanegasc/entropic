import os
from unittest.mock import patch

import pytest

from entropic.db import TinyDBHandler
from entropic.sources import Iteration, DefaultSample
from entropic.sources.fields import DataSource


@pytest.fixture(scope="module")
def database():
    DB_PATH = ".entropic-iteration-test"
    yield TinyDBHandler(path=DB_PATH)
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass


def test_database_operations(database, mock_data_frame):
    with patch("entropic.sources.iteration.Iteration.database", database):
        assert database.get(source_path="some/path") is None

        iteration = Iteration.get_or_create(source_path="some/path")
        assert iteration

        iteration = Iteration.get_or_create(source_path="some/path")
        assert iteration
        assert len(database.all()) == 1

        new_iteration = Iteration(source_path="other/path")
        new_iteration.upsert_sample(
            DefaultSample(
                data=DataSource(file_path="other/path/file.csv", raw=mock_data_frame)
            )
        )
        new_iteration.upsert_sample(
            DefaultSample(
                data=DataSource(file_path="other/path/file.csv", raw=mock_data_frame)
            )
        )
        assert len(new_iteration.samples) == 1

        new_iteration.save()
        assert database.get(source_path="other/path")
        assert len(database.all()) == 2
