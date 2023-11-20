import zlib
import base64
import io
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
        self.file_path = kwargs.get("file_path")
        self.raw = kwargs.get("raw")

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

    @staticmethod
    def _dump_data_frame(data_frame: pd.DataFrame) -> str:
        data_frame_bytes = data_frame.to_json().encode()
        compressed = zlib.compress(data_frame_bytes)
        compressed_b64 = base64.b64encode(compressed)
        compressed_b64_string = compressed_b64.decode()
        return compressed_b64_string

    @staticmethod
    def _load_data_frame(compressed: str) -> pd.DataFrame:
        compressed_b64_bytes = compressed.encode()
        compressed_b64 = base64.b64decode(compressed_b64_bytes)
        uncompressed = zlib.decompress(compressed_b64)
        data_frame = pd.read_json(io.BytesIO(uncompressed))
        return data_frame
