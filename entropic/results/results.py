from typing import Iterable
from entropic.sources import Iteration
from entropic.db import default_database


class Results:
    database = default_database()
    iteration = Iteration

    def _load(self, document):
        return self.iteration(**document)

    @property
    def all(self) -> Iterable[Iteration]:
        return [self._load(item) for item in self.database.all()]
