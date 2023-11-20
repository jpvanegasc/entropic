from entropic.sources.fields.mixins import ListFieldMixin


class SamplesField(ListFieldMixin):
    def __init__(self, sample_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sample_class = sample_cls

    def load(self, **kwargs):
        samples = kwargs.get("samples", [])
        self.extend(samples)
        return samples

    def add(self, sample=None, **kwargs):
        if not sample:
            sample = self.sample_class(**kwargs)
        self.append(sample)
        return sample

    def dump(self):
        return [sample.dump() for sample in self]
