from pydantic import BaseModel

from entropic.sources.fields import DataSource


class Sample(BaseModel):
    data: DataSource
