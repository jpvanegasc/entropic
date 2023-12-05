import os
import warnings
from typing import final, Callable, TypeVar, Union
from pathlib import Path

from entropic.sources import Iteration
from entropic.sources.fields import DataSource

from entropic.process.exceptions import PipelineSetupError

IterationType = TypeVar("IterationType", bound=Iteration)


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
    """
    The Pipeline class is a base class designed to facilitate the creation of data processing pipelines. It enforces a structured approach to defining and executing data processing steps, such as extraction, transformation, and loading (ETL).

    - **iteration**: `Iteration`
      - Iteration to be used for processing. Defaults to `Iteration`

    - **source_paths**: List[Union[Path, str]]
      - A list of path-like objects or strings representing the source paths from which data will be extracted.

    - **extract_with**: Callable
      - A callable object or function responsible for extracting data from a given file path into samples for each iteration.
    """

    iteration = Iteration
    source_paths: list[Union[Path, str]] = []
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
        """Returns the list of source paths defined in the pipeline."""
        return self.source_paths

    def get_iteration(self):
        """
        Returns the iteration type associated with the pipeline.
        """
        return self.iteration

    def get_iteration_by_path(self, source_path):
        """
        Wrapper over `Iteration.get_or_create(source_path=source_path)`
        """
        return self.get_iteration().get_or_create(source_path=source_path)

    def get_sample(self):
        """
        Returns the sample associated with the iteration.
        """
        return self.iteration.sample

    def get_files_from_path(self, path):
        """
        Retrieves a list of `Path` objects representing files in the specified path.
        """
        return [Path(path, file) for file in os.listdir(path)]

    def extract(self, source_path):
        """Extracts data from the specified file using the defined extract_with method and returns an Iteration object."""
        iteration = self.get_iteration_by_path(source_path)
        for file_path in self.get_files_from_path(source_path):
            data_source_data = self.extract_with(file_path)
            sample = self.get_sample()(
                data=DataSource(file_path=file_path, raw=data_source_data)
            )
            iteration.upsert_sample(sample)
        return iteration

    def transform(self, iteration):
        """
        Transforms the given iteration and returns the transformed iteration.
        """
        return iteration

    def load(self, iteration):
        """
        Loads the specified iteration by saving it.
        """
        return iteration.save()

    @final
    def extract_all_iterations(self) -> list[IterationType]:
        """
        Extracts data from all specified source paths and returns a list of iterations.
        """
        iterations: list[IterationType] = []
        for source_path in self.get_source_paths():
            iteration: IterationType = self.extract(source_path)
            iterations.append(iteration)
        return iterations

    @final
    def transform_all_iterations(
        self, iterations: list[IterationType]
    ) -> list[IterationType]:
        """
        Transforms a list of iterations and returns the transformed list.
        """
        for iteration in iterations:
            iteration = self.transform(iteration)
        return iterations

    @final
    def load_all_iterations(self, iterations: list[IterationType]) -> list:
        """
        Loads a list of iterations by saving them, and returns the list of results.
        """
        saved = []
        for iteration in iterations:
            result = self.load(iteration)
            saved.append(result)
        return saved

    @final
    def run(self):
        """
        Executes the entire pipeline, including extraction, transformation, and loading, and returns the final results.
        """
        iterations = self.extract_all_iterations()
        iterations = self.transform_all_iterations(iterations)
        results = self.load_all_iterations(iterations)
        return results
