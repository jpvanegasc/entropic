import os
from typing import final, Optional, Callable
from pathlib import Path

from entropic.db import default_database

from entropic.process.exceptions import PipelineSetupError


class Pipeline:
    database = default_database()

    source_path: Optional[str | Path] = None
    filepaths: Optional[Callable] = None

    extract_with: Optional[Callable] = None
    extract: Optional[Callable] = None

    def __init__(self):
        self._validate_setup()
        if not self.extract_with:
            self.extract_with = self.extract
        if not self.filepaths:
            self.filepaths = os.listdir(self.source_path)

    def _validate_setup(self):
        if not (self.source_path or self.filepaths):
            raise PipelineSetupError(
                "either 'source_path' or 'filepaths' must be defined"
            )
        if not (self.extract_with or self.extract):
            raise PipelineSetupError(
                "either 'extract_with' or 'extract' must be defined"
            )

    @final
    def run(self):
        self.database.insert_one({"path": self.source_path})
