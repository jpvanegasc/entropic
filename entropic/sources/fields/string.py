class StringField:
    def load(self, **kwargs):
        self.value = kwargs.get("value", "")

    def dump(self):
        return self.value
