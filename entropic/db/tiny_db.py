from typing import Optional

from tinydb import TinyDB, where, Query

from entropic.db.base import BaseHandler


class Handler(BaseHandler):
    PATH = "./.entropic-db"

    def __init__(self, path=None):
        if path:
            self.PATH = path

    @property
    def database(self) -> TinyDB:
        return TinyDB(self.PATH)

    @staticmethod
    def _kwargs_to_query(kwargs: dict) -> Optional[Query]:
        if not (items := list(kwargs.items())):
            return None
        query = where(items[0][0]) == items[0][1]
        for field, value in items[1:]:
            query &= Query()[field] == value
        return query

    def get(self, **kwargs):
        id = kwargs.pop("id", None)
        query = self._kwargs_to_query(kwargs)
        return self.database.get(query, doc_id=id)

    def all(self):
        return self.database.all()

    def filter(self, **kwargs):
        if not kwargs:
            return self.all()
        query = self._kwargs_to_query(kwargs)
        return self.database.search(query)

    def insert_one(self, document):
        return self.database.insert(document)

    def get_or_create(self, **kwargs):
        item = self.get(**kwargs)
        if not (item := self.get(**kwargs)):
            item = kwargs
            self.insert_one(item)

        return item

    def upsert(self, document, key: Optional[dict] = None):
        if not key:
            key = {"key": "id", "value": document.get("id")}
        return self.database.upsert(document, where(key["key"]) == key["value"])
