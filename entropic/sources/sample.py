from typing import final

from pydantic import BaseModel

from entropic.sources.fields import DataSource


class BaseSample(BaseModel):
    def _get_data_source_fields(self):
        data_source_fields = []
        for field, field_info in self.model_fields.items():
            if field_info.annotation is DataSource:
                data_source_fields.append(field)
        return data_source_fields

    def __eq__(self, other):
        # Only equal type of samples can be compared. Even inherited types will be treated as different
        if type(self) is not type(other):
            return False
        # Equality between samples depends on equality between all of its internal data source fields
        return all(
            getattr(self, self_field) == getattr(other, other_field)
            for self_field, other_field in zip(
                self._get_data_source_fields(), other._get_data_source_fields()
            )
        )


@final
class DefaultSample(BaseSample):
    data: DataSource
