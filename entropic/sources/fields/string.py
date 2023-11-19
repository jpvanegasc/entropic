from entropic.sources.fields.base import BaseField


class StringField(BaseField):
    def load(self, **kwargs):
        self.value = kwargs.get("value", "")

    def dump(self):
        return self.value
