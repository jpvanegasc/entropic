import os
import warnings
from typing import final, Optional, Callable
from pathlib import Path

from entropic.sources import Iteration, Sample
from entropic.sources.fields import DataSource

from entropic.process.exceptions import PipelineSetupError


def default_filepaths(self):
    return [
        os.path.join(self.source_path, file) for file in os.listdir(self.source_path)
    ]


class PipelineMeta(type):
    def __new__(cls, name, bases, attrs):
        if not bases:
            # Pipeline instantiation error handled in Pipeline.__init__
            return super().__new__(cls, name, bases, attrs)

        if not (attrs.get("source_path") or attrs.get("filepaths")):
            raise PipelineSetupError(
                "either 'source_path' or 'filepaths' must be defined"
            )
        if not (attrs.get("extract_with") or attrs.get("extract")):
            raise PipelineSetupError(
                "either 'extract_with' or 'extract' must be defined"
            )

        if attrs.get("source_path") and attrs.get("filepaths"):
            warnings.warn(
                "both 'source_path' and 'filepaths' defined, ignoring 'source_path'",
                stacklevel=2,
            )
        if attrs.get("extract_with") and attrs.get("extract"):
            warnings.warn(
                "both 'extract_with' and 'extract' are defined, ignoring 'extract_with'",
                stacklevel=2,
            )

        if extract_with := attrs.get("extract_with"):
            attrs["extract_with"] = staticmethod(extract_with)
        if not attrs.get("filepaths"):
            attrs["filepaths"] = default_filepaths
        if not attrs.get("source_path"):
            filepaths = attrs["filepaths"]
            attrs["source_path"] = f"<{filepaths.__qualname__}>"

        return super().__new__(cls, name, bases, attrs)


class Pipeline(metaclass=PipelineMeta):
    iteration = Iteration

    source_path: Optional[str | Path] = None
    filepaths: Optional[Callable] = None

    extract_with: Callable

    def __init__(self):
        if type(self) == Pipeline:
            raise PipelineSetupError("can't instantiate Pipeline directly")

    def extract(self, file_path) -> Sample:
        data_source_data = self.extract_with(file_path)
        return Sample(data=DataSource(file_path=file_path, raw=data_source_data))

    @final
    def run_sample_extraction(self):
        self.instance = self.iteration(
            **self.iteration.database.get_or_create(source_path=self.source_path)
        )
        for file_path in self.filepaths():
            sample = self.extract(file_path)
            self.instance.upsert_sample(sample=sample)

        return self.instance.save()

    @final
    def run(self):
        iteration_id = self.run_sample_extraction()
        # TODO: add load methods
        return iteration_id
