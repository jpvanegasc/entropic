import abc
from typing import Collection


class BaseHandler(abc.ABC):
    @property
    @abc.abstractmethod
    def database(self):
        ...

    @abc.abstractmethod
    def find(self, **kwargs):
        ...

    @abc.abstractmethod
    def insert_one(self, document: Collection):
        ...
