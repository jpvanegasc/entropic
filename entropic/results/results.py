from typing import Sequence, Dict
from entropic.sources import Iteration
from entropic.db import default_database


class Results:
    database = default_database()
    iteration = Iteration

    def _load(self, document_list: Sequence[Dict]) -> Sequence[Iteration]:
        return [self.iteration.parse_obj(document) for document in document_list]

    @property
    def all(self) -> Sequence[Iteration]:
        return self._load(self.database.all())
