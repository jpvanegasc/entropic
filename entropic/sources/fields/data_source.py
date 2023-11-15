from entropic.sources.fields.base import BaseField

SUPPORTED_FILETYPES = [
    "csv",
]


class DataSource(BaseField):
    def __init__(self, filetype="csv", **kwargs):
        self.filetype = self._validate_filetype(filetype)
        self.filename = None

    @staticmethod
    def _validate_filetype(filetype: str):
        clean = filetype.strip().replace(".", "").lower()
        if clean in SUPPORTED_FILETYPES:
            return clean
        raise ValueError(f"Unsupported filetype '{filetype}'")

    def load_field(self, **kwargs):
        self.filename = kwargs.get("filename")
        return self
