import zlib
import base64
import io
from pathlib import Path

import pandas as pd
from pydantic import (
    BaseModel,
    field_serializer,
    field_validator,
    ConfigDict,
)

SUPPORTED_FILETYPES = [
    "csv",
]


class DataSource(BaseModel):
    file_path: str | Path
    raw: str | pd.DataFrame
    filetype: str = "csv"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("raw")
    def serialize_raw(self, raw: pd.DataFrame):
        return self._dump_data_frame(raw)

    @field_validator("raw")
    @classmethod
    def validate_raw(cls, value: str | pd.DataFrame) -> pd.DataFrame:
        if isinstance(value, pd.DataFrame):
            return value
        try:
            return cls._load_data_frame(value)
        except Exception:
            raise ValueError("unable to load a `pandas.DataFrame` object from raw")

    @staticmethod
    def _dump_data_frame(data_frame: pd.DataFrame) -> str:
        data_frame_bytes = data_frame.to_parquet()
        compressed = zlib.compress(data_frame_bytes)
        compressed_b64 = base64.b64encode(compressed)
        compressed_b64_string = compressed_b64.decode()
        return compressed_b64_string

    @staticmethod
    def _load_data_frame(compressed: str) -> pd.DataFrame:
        compressed_b64_bytes = compressed.encode()
        compressed_b64 = base64.b64decode(compressed_b64_bytes)
        uncompressed = zlib.decompress(compressed_b64)
        data_frame = pd.read_parquet(io.BytesIO(uncompressed))
        return data_frame
