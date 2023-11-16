from typing import List, Iterator, overload


class ListFieldMixin:
    def __init__(self, *args, **kwargs):
        self._sequence = []

    def __iter__(self) -> Iterator:
        return self._sequence.__iter__()

    @overload
    def __getitem__(self, i: int) -> List:
        ...

    @overload
    def __getitem__(self, s: slice) -> List:
        ...

    def __getitem__(self, value) -> List:
        return self._sequence.__getitem__(value)

    def append(self, _object) -> None:
        return self._sequence.append(_object)
