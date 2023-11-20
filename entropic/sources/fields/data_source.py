import zlib
import json
from pathlib import Path

import pandas as pd

from entropic.sources.fields.base import BaseField

SUPPORTED_FILETYPES = [
    "csv",
]


class DataSource(BaseField):
    filetype: str
    file_path: str | Path
    raw: pd.DataFrame

    def __init__(self, filetype="csv", **kwargs):
        self.filetype = self._validate_filetype(filetype)
        self.file_path = None
        self.raw = None

    @staticmethod
    def _validate_filetype(filetype: str):
        clean = filetype.strip().replace(".", "").lower()
        if clean in SUPPORTED_FILETYPES:
            return clean
        raise ValueError(f"unsupported filetype '{filetype}'")

    def load(self, **kwargs):
        self.file_path = kwargs.get("file_path")
        self.raw = kwargs.get("raw")

    def dump(self):
        return {
            "file_path": self.file_path,
            "raw": self._dump_data_frame(self.raw),
        }

    @classmethod
    def from_dict(cls, document: dict) -> "DataSource":
        document["raw"] = cls._load_data_frame(document["raw"])
        return cls(**document)

    @staticmethod
    def _dump_data_frame(data_frame: pd.DataFrame) -> str:
        data_frame_bytes = data_frame.to_json().encode("ascii")
        compressed = zlib.compress(data_frame_bytes)
        return compressed.decode("ascii", errors="ignore")

    @staticmethod
    def _load_data_frame(compressed: str) -> pd.DataFrame:
        uncompressed = zlib.decompress(compressed.encode("ascii"))
        data_frame_dict = json.loads(uncompressed.decode("ascii", errors="ignore"))
        return pd.DataFrame.from_dict(data_frame_dict)
