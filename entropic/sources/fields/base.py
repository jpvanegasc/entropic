import abc


class BaseField(abc.ABC):
    @abc.abstractmethod
    def load(self, **kwargs):
        ...

    @abc.abstractmethod
    def dump(self):
        ...
