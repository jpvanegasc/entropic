from typing import Sequence, Optional, Generator
from entropic.sources import Iteration
from entropic.db import default_database


class Results:
    database = default_database()
    iteration = Iteration

    def _load(self, document_list: Sequence[dict]) -> Generator[Iteration, None, None]:
        for document in document_list:
            yield self.iteration.model_validate(document)

    @property
    def all(self) -> Generator[Iteration, None, None]:
        return self._load(self.database.all())

    def filter(self, **kwargs) -> Generator[Iteration, None, None]:
        return self._load(self.database.filter(**kwargs))

    def get(self, **kwargs) -> Optional[Iteration]:
        if item := self.database.get(**kwargs):
            return self.iteration.model_validate(item)
        return None

    def set_iteration(self, iteration_class):
        """Change the default iteration to be used for loading results"""
        self.iteration = iteration_class
