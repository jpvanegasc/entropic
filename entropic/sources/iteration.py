from typing import ClassVar, TypeAlias

from pydantic import BaseModel, Field

from entropic.db import default_database

from entropic.sources.sample import Sample


class Iteration(BaseModel):
    database: ClassVar = default_database()
    sample: ClassVar[TypeAlias] = Sample

    samples: list[sample] = Field(default_factory=list)
    source_path: str

    @classmethod
    def get_or_create(cls, **kwargs):
        # TODO: this should be done automatically by the database
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
