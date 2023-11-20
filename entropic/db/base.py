import abc
from typing import Collection


class BaseHandler(abc.ABC):
    @property
    @abc.abstractmethod
    def database(self):
        ...

    @abc.abstractmethod
    def get(self, **kwargs):
        ...

    @abc.abstractmethod
    def all(self):
        ...

    @abc.abstractmethod
    def filter(self, **kwargs):
        ...

    @abc.abstractmethod
    def insert_one(self, document: Collection):
        ...

    @abc.abstractmethod
    def get_or_create(self, **kwargs):
        ...
