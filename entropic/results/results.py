from typing import Iterable, Dict
from entropic.sources import Iteration
from entropic.db import default_database


class Results:
    database = default_database()
    iteration = Iteration

    def _load(self, document_list: Iterable[Dict]) -> Iterable[Iteration]:
        return [self.iteration.from_dict(document) for document in document_list]

    @property
    def all(self) -> Iterable[Iteration]:
        return self._load(self.database.all())
