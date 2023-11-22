from pydantic import BaseModel

from entropic.sources.fields import DataSource


class Sample(BaseModel):
    data: DataSource

    def __hash__(self):
        return hash(self.data.file_path)
