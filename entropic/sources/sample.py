from entropic.sources.mixins import PandasReadMixin
from entropic.sources.fields import DataSource


class Sample(PandasReadMixin):
    data = DataSource()

    fields = {"data": data}

    def __init__(self, **kwargs):
        self.data = self.data.load_field(filename=kwargs.get("data"))

    def dump(self):
        return {name: field.dump() for name, field in self.fields.items()}
