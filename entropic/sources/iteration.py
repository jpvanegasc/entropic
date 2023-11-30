from pathlib import Path
from typing import ClassVar, TypeAlias

from pydantic import BaseModel, Field, field_serializer, field_validator

from entropic.db import default_database

from entropic.sources.sample import Sample


class Iteration(BaseModel):
    database: ClassVar = default_database()
    sample: ClassVar[TypeAlias] = Sample

    samples: list[sample] = Field(default_factory=list)
    source_path: Path

    @field_serializer("source_path")
    def serialize_source_path(self, source_path: Path):
        return str(source_path)

    @field_validator("samples", mode="before")
    @classmethod
    def validate_samples(cls, value: list):
        return [cls.sample.model_validate(sample) for sample in value]

    @field_serializer("samples")
    def serialize_samples(self, samples):
        return [sample.model_dump() for sample in samples]

    @classmethod
    def get_or_create(cls, **kwargs):
        # TODO: this should be done automatically by the database
        if path := kwargs.get("source_path"):
            kwargs["source_path"] = str(path)
        return cls(**cls.database.get_or_create(**kwargs))

    def save(self):
        return self.database.upsert(
            self.model_dump(),
            key={"key": "source_path", "value": str(self.source_path)},
        )

    def upsert_sample(self, sample):
        if sample in self.samples:
            index = self.samples.index(sample)
            self.samples[index] = sample
        else:
            self.samples.append(sample)
        return sample
