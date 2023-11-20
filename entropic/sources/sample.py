from pydantic import BaseModel

from entropic.sources.mixins import PandasReadMixin
from entropic.sources.fields import DataSource


class Sample(BaseModel, PandasReadMixin):
    data: DataSource

    def __hash__(self):
        return hash(self.data.file_path)
