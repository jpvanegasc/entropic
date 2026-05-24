from typing import Any
from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):  # type:ignore
    id: Mapped[str] = mapped_column(primary_key=True)
    result_file: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    custom_data: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict,
        nullable=False,
    )

    def _apply_custom_data_patch(self, patch: dict[str, Any]) -> None:
        """
        - {} clears all custom_data
        - {"key": value} sets or updates a key
        - {"key": None} removes a key
        """
        if patch == {}:
            self.custom_data = {}
            return

        current = dict(self.custom_data or {})

        for key, value in patch.items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = value

        self.custom_data = current

    def apply_patch(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if value is None and key != "custom_data":
                continue

            if key == "custom_data":
                self._apply_custom_data_patch(value)
            else:
                setattr(self, key, value)


__all__ = ["Base", "Mapped", "mapped_column"]
