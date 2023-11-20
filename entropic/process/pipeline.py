import os
from typing import final, Optional, Callable
from pathlib import Path

from entropic.sources import Iteration

from entropic.process.exceptions import PipelineSetupError


class Pipeline:
    iteration = Iteration

    source_path: Optional[str | Path] = None
    filepaths: Optional[Callable] = None

    extract_with: Optional[Callable] = None
    extract: Optional[Callable] = None

    def __init__(self):
        self._validate_setup()
        if not self.extract_with:
            self.extract_with = self.extract
        if not self.filepaths:
            self.filepaths = self._default_filepaths

    def _validate_setup(self):
        if not (self.source_path or self.filepaths):
            raise PipelineSetupError(
                "either 'source_path' or 'filepaths' must be defined"
            )
        if not (self.extract_with or self.extract):
            raise PipelineSetupError(
                "either 'extract_with' or 'extract' must be defined"
            )

    def _default_filepaths(self):
        return [
            os.path.join(self.source_path, file)
            for file in os.listdir(self.source_path)
        ]

    @final
    def run(self):
        self.instance = self.iteration(
            **self.iteration.database.get_or_create(source_path=self.source_path)
        )
        for file_path in self.filepaths():
            self.instance.samples.add(
                **{
                    "data": {
                        "file_path": file_path,
                        "raw": self.extract_with(file_path),
                    },
                }
            )

        self.instance.save()
