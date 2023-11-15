from entropic.sources.mixins import PandasReadMixin
from entropic.sources.fields import DataSource


class Sample(PandasReadMixin):
    data = DataSource()

    def __init__(self, **kwargs):
        self.data = self.data.load_field(filename=kwargs.get("data"))
