from typing import Optional

from tinydb import TinyDB, where, Query

from entropic.db.base import BaseHandler


class Handler(BaseHandler):
    """
    Provides a convenient interface for interacting with a TinyDB database in the context
    of the Entropic application.
    """

    PATH = "./.entropic-db"

    def __init__(self, path=None):
        if path:
            self.PATH = path

    @property
    def database(self) -> TinyDB:
        """Property method that returns a TinyDB instance connected to the specified or default path."""
        return TinyDB(self.PATH)

    @staticmethod
    def _kwargs_to_query(kwargs: dict) -> Optional[Query]:
        """Private method that converts keyword arguments to a TinyDB Query object."""
        if not (items := list(kwargs.items())):
            return None
        query = where(items[0][0]) == items[0][1]
        for field, value in items[1:]:
            query &= Query()[field] == value
        return query

    def get(self, **kwargs):
        """Retrieves a single document from the database based on the provided criteria."""
        id = kwargs.pop("id", None)
        query = self._kwargs_to_query(kwargs)
        return self.database.get(query, doc_id=id)

    def all(self):
        """Retrieves all documents from the database."""
        return self.database.all()

    def filter(self, **kwargs):
        """Filters and retrieves documents from the database based on the provided criteria."""
        if not kwargs:
            return self.all()
        query = self._kwargs_to_query(kwargs)
        return self.database.search(query)

    def insert_one(self, document):
        """Inserts a single document into the database."""
        return self.database.insert(document)

    def get_or_create(self, **kwargs):
        """Retrieves a document based on the provided criteria; if not found, creates and inserts a new document."""
        if not (item := self.get(**kwargs)):
            item = kwargs
            self.insert_one(item)

        return item

    def upsert(self, document, key: Optional[dict] = None):
        """Updates or inserts a document into the database based on a specified key."""
        if not key:
            key = {"key": "id", "value": document.get("id")}
        return self.database.upsert(document, where(key["key"]) == key["value"])
