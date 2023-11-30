from pydantic import BaseModel

from entropic.sources.fields import DataSource


class Sample(BaseModel):
    data: DataSource

    def __eq__(self, other):
        if not isinstance(other, Sample):
            return False
        return self.data == other.data
