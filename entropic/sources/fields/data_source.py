from entropic.sources.fields.base import BaseField

SUPPORTED_FILETYPES = [
    "csv",
]


class DataSource(BaseField):
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
        self.filename = kwargs.get("file_path")
        self.raw = kwargs.get("raw")

    def dump(self):
        return {"file_path": self.file_path, "raw": self.raw}
