from typing import Iterable
from entropic.sources import Iteration
from entropic.db import default_database


class Results:
    database = default_database()
    iteration = Iteration

    @property
    def all(self) -> Iterable[Iteration]:
        return [self.iteration(**item) for item in self.database.all()]
