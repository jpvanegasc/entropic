import os

DB_PATH = ".entropic-db"


def pytest_sessionfinish(session, exitstatus):
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass
