from entropic.sources.mixins import PandasReadMixin
from entropic.sources.fields import DataSource


class Sample(PandasReadMixin):
    data = DataSource()

    data_fields = {"data": data}
    fields = {**data_fields}

    def __init__(self, **kwargs):
        for field_name, field in self.data_fields.items():
            if field_data := kwargs.get(field_name):
                field.load(**field_data)

    def dump(self):
        return {name: field.dump() for name, field in self.fields.items()}

    @classmethod
    def from_dict(cls, document: dict) -> "Sample":
        for field_name, field in cls.data_fields.items():
            if value := document.get(field_name):
                document[field_name]["raw"] = field._load_data_frame(value["raw"])

        instance = cls(**document)

        return instance
