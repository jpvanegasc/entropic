from entropic.sources.fields.base import BaseField


class StringField(BaseField):
    def load_field(self, **kwargs):
        self.value = kwargs.get("value", "")
        return self

    def dump(self):
        return self.value
