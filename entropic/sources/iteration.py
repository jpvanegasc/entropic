from entropic.db import default_database

from entropic.sources.fields import SamplesField, StringField
from entropic.sources.sample import Sample


class Iteration:
    samples = SamplesField(Sample)
    source_path = StringField()

    database = default_database()

    fields = {"source_path": source_path, "samples": samples}

    def __init__(self, **kwargs):
        self.source_path = self.source_path.load(value=kwargs.get("source_path"))

    def dump(self) -> dict:
        obj = {}
        for name, field in self.fields.items():
            obj[name] = field.dump()
        return obj

    def save(self):
        self.database.upsert(
            self.dump(), key={"key": "source_path", "value": self.source_path.dump()}
        )
