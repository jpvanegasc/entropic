import os

import pytest
import pandas as pd

DB_PATH = ".entropic-db"


def pytest_sessionfinish(session, exitstatus):
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_data_frame():
    return pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
