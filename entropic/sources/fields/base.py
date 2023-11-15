import abc


class BaseField(abc.ABC):
    @abc.abstractmethod
    def load_field(self, **kwargs):
        ...
