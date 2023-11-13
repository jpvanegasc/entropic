from typing import Iterable

from entropic.sources import Case
from entropic.db import default_database


class Results:
    database = default_database()

    @property
    def all(self) -> Iterable[Case]:
        return self.database.find()
