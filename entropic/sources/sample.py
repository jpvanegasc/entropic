from entropic.sources.mixins import PandasReadMixin
from entropic.sources.fields import DataSource


class Sample(PandasReadMixin):
    data = DataSource()

    data_fields = {"data": data}

    def __init__(self, **kwargs):
        for field_name, field in self.data_fields.items():
            if field_data := kwargs.get(field_name):
                setattr(self, f"{field_name}_raw", field.load(**field_data))

    def dump(self) -> dict:
        document = {}
        for field_name, field in self.data_fields.items():
            field_data = getattr(self, f"{field_name}_raw", None)
            document[field_name] = field.dump(field_data) if field_data else None
        return document

    @classmethod
    def from_dict(cls, document: dict) -> "Sample":
        for field_name, field in cls.data_fields.items():
            if value := document.get(field_name):
                document[field_name]["raw"] = field._load_data_frame(value["raw"])

        instance = cls(**document)

        return instance
