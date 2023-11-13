from tinydb import TinyDB

from entropic.db.base import BaseHandler


class Handler(BaseHandler):
    PATH = "./.entropic-db"

    @property
    def database(self) -> TinyDB:
        return TinyDB(self.PATH)

    def find(self, **kwargs):
        if not kwargs:
            return self.database.all()
        return []

    def insert_one(self, document):
        self.database.insert(document)
