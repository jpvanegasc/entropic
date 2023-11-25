from typing import ClassVar, TypeAlias

from pydantic import BaseModel, Field, field_serializer

from entropic.db import default_database

from entropic.sources.sample import Sample


class Iteration(BaseModel):
    database: ClassVar = default_database()
    sample_class: ClassVar[TypeAlias] = Sample

    samples: list[sample_class] = Field(default_factory=list)
    source_path: str

    @field_serializer("samples")
    def serialize_samples(self, samples):
        return list(samples)

    def save(self):
        return self.database.upsert(
            self.model_dump(),
            key={"key": "source_path", "value": self.source_path},
        )

    def upsert_sample(self, sample):
        try:
            if index := self.samples.index(sample):
                self.samples[index] = sample
        except ValueError:
            self.samples.append(sample)
        return sample
