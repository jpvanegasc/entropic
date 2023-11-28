from pathlib import Path
from typing import ClassVar, TypeAlias

from pydantic import BaseModel, Field, field_serializer

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

    @classmethod
    def get_or_create(cls, **kwargs):
        # TODO: this should be done automatically by the database
        if path := kwargs.get("source_path"):
            kwargs["source_path"] = str(path)
        return cls(**cls.database.get_or_create(**kwargs))

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
