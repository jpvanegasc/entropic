from pathlib import Path
from typing import ClassVar, TypeVar, Generic

from pydantic import BaseModel, Field, field_serializer, field_validator

from entropic.db import default_database

from entropic.sources.sample import Sample

SampleType = TypeVar("SampleType")


class Iteration(BaseModel, Generic[SampleType]):
    """
    The Iteration class is a generic class designed to represent iterations of data processing. It includes methods for serialization, validation, retrieval, and storage of data samples associated with a specific source path.

    - **source_path**: Path
        - Source path associated with the iteration. Will be used as primary key.

    - **database**: ClassVar
        - The database used for storage.

    - **sample**: ClassVar
        - The sample class associated with the iteration. Defaults to `Sample`.

    - **samples**: List[SampleType]
        - A list of samples associated with the iteration. Initialized as an empty list.
    """

    database: ClassVar = default_database()
    sample: ClassVar = Sample

    samples: list[SampleType] = Field(default_factory=list)
    source_path: Path

    @field_serializer("source_path")
    def serialize_source_path(self, source_path: Path):
        return str(source_path)

    @field_validator("samples")
    @classmethod
    def validate_samples(cls, value: list):
        return [cls.sample.model_validate(sample) for sample in value]

    @field_serializer("samples")
    def serialize_samples(self, samples):
        return [sample.model_dump() for sample in samples]

    @classmethod
    def get_or_create(cls, **kwargs):
        """
        Retrieves an existing iteration from the database or creates a new one based on the provided keyword arguments.
        """
        # TODO: this should be done automatically by the database
        if path := kwargs.get("source_path"):
            kwargs["source_path"] = str(path)
        return cls(**cls.database.get_or_create(**kwargs))

    def save(self):
        """
        Saves the iteration in the database using the serialized data.
        """
        return self.database.upsert(
            self.model_dump(),
            key={"key": "source_path", "value": str(self.source_path)},
        )

    def upsert_sample(self, sample):
        """
        Updates or inserts a sample into the iteration's sample list.
        """
        if sample in self.samples:
            index = self.samples.index(sample)
            self.samples[index] = sample
        else:
            self.samples.append(sample)
        return sample
