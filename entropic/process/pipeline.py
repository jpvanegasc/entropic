import os
import warnings
from typing import final, Callable
from pathlib import Path

from entropic.sources import Iteration, Sample
from entropic.sources.fields import DataSource

from entropic.process.exceptions import PipelineSetupError


class PipelineMeta(type):
    def __new__(cls, name, bases, attrs):
        if not bases:
            # Pipeline instantiation error handled in Pipeline.__init__
            return super().__new__(cls, name, bases, attrs)

        if not (attrs.get("source_paths") or attrs.get("get_source_paths")):
            raise PipelineSetupError(
                "either 'source_paths' or 'get_source_paths' must be defined"
            )
        if not (attrs.get("extract_with") or attrs.get("extract")):
            raise PipelineSetupError(
                "either 'extract_with' or 'extract' must be defined"
            )

        if attrs.get("source_paths") and attrs.get("get_source_paths"):
            warnings.warn(
                "both 'source_paths' and 'get_source_paths' defined, ignoring 'source_paths'",
                stacklevel=2,
            )
        if attrs.get("extract_with") and attrs.get("extract"):
            warnings.warn(
                "both 'extract_with' and 'extract' are defined, ignoring 'extract_with'",
                stacklevel=2,
            )

        if extract_with := attrs.get("extract_with"):
            attrs["extract_with"] = staticmethod(extract_with)

        return super().__new__(cls, name, bases, attrs)


class Pipeline(metaclass=PipelineMeta):
    iteration = Iteration
    source_paths: list[Path | str] = []
    extract_with: Callable

    def __init__(self):
        if type(self) == Pipeline:
            raise PipelineSetupError("can't instantiate Pipeline directly")

        if self.source_paths:
            error_message = "'source_paths' must be a list of path-like objects"
            if not isinstance(self.source_paths, list):
                raise TypeError(error_message)
            try:
                self.source_paths = [Path(path) for path in self.source_paths]
            except TypeError as ex:
                raise TypeError(error_message) from ex

    def get_source_paths(self):
        return self.source_paths

    def get_iteration(self):
        return self.iteration

    def get_files_from_path(self, path):
        return [Path(path, file) for file in os.listdir(path)]

    def extract(self, file_path) -> Sample:
        data_source_data = self.extract_with(file_path)
        return Sample(data=DataSource(file_path=file_path, raw=data_source_data))

    @final
    def extract_all_source_paths(self):
        for source_path in self.get_source_paths():
            instance = self.get_iteration().get_or_create(source_path=source_path)
            for file_path in self.get_files_from_path(source_path):
                sample = self.extract(file_path)
                instance.upsert_sample(sample=sample)
            instance.save()

    @final
    def run(self):
        self.extract_all_source_paths()
        # TODO: add load methods
        return
