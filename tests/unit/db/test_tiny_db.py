import os

import pytest
from tinydb import TinyDB
from tinydb.queries import QueryInstance

from entropic.db import TinyDBHandler


@pytest.fixture
def database():
    DB_PATH = ".entropic-db-2"
    yield TinyDBHandler(path=DB_PATH)
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass


def test_initialization(database):
    assert isinstance(database.database, TinyDB)


def test_kwargs_to_db_filter():
    assert TinyDBHandler._kwargs_to_query({}) is None

    kwargs = {"field_1": "value_1"}
    query = TinyDBHandler._kwargs_to_query(kwargs)
    assert isinstance(query, QueryInstance)
    assert query == QueryInstance(test=None, hashval=("==", ("field_1",), "value_1"))

    kwargs["field_2"] = "value_2"
    query = TinyDBHandler._kwargs_to_query(kwargs)
    assert isinstance(query, QueryInstance)
    assert query == QueryInstance(
        test=None,
        hashval=(
            "and",
            frozenset(
                [("==", ("field_2",), "value_2"), ("==", ("field_1",), "value_1")]
            ),
        ),
    )


def test_db_operations(database):
    item = {"id": "1", "name": "item"}

    assert database.get(**item) is None

    database.get_or_create(**item)
    assert database.get(**item) == item

    filtered = database.filter(id="1")
    assert isinstance(filtered, list)
    assert len(filtered) == 1

    result = filtered[0]
    assert isinstance(result, dict)
    assert result == item

    assert database.all() == [item]
    assert database.filter()

    item["hello"] = "world"
    database.upsert(item)
    assert database.get(**item) == item
