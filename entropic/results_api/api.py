from typing import Sequence, Generator, Any
from entropic.sources import Iteration
from entropic.db import default_database


class Results:
    """
    The `Results` class provides a high-level interface for working with results stored in the default
    database. It is designed to work with the Entropic application and leverages an associated `Iteration`
    class for result validation.
    """

    database = default_database()
    iteration = Iteration

    def _load(self, document_list: Sequence[dict]) -> Generator[Any, None, None]:
        """Private method that loads and validates documents from a list using the default iteration class."""
        for document in document_list:
            yield self.iteration.model_validate(document)

    @property
    def all(self) -> Generator[Any, None, None]:
        """Retrieves and validates all results from the default database."""
        return self._load(self.database.all())

    def filter(self, **kwargs) -> Generator[Any, None, None]:
        """Filters and retrieves results from the default database based on the provided criteria."""
        return self._load(self.database.filter(**kwargs))

    def get(self, **kwargs):
        """Retrieves and validates a single result from the default database based on the provided criteria."""
        if item := self.database.get(**kwargs):
            return self.iteration.model_validate(item)
        return None

    def set_iteration(self, iteration_class):
        """Change the default iteration to be used for loading results."""
        self.iteration = iteration_class
