from typing import List, ClassVar, TypeAlias

from pydantic import BaseModel

from entropic.db import default_database

from entropic.sources.sample import Sample


class Iteration(BaseModel):
    database: ClassVar = default_database()
    sample_class: ClassVar[TypeAlias] = Sample

    samples: List[sample_class]
    source_path: str

    def save(self):
        self.database.upsert(
            self.model_dump(),
            key={"key": "source_path", "value": self.source_path},
        )

    def add_sample(self, sample=None, **kwargs):
        if not sample:
            sample = self.sample_class(**kwargs)
        self.samples.append(sample)
        return sample
