from typing import List, Iterator, overload, Iterable


class ListFieldMixin:
    def __init__(self, *args, **kwargs):
        self._sequence = []

    def __iter__(self) -> Iterator:
        return self._sequence.__iter__()

    def __len__(self) -> int:
        return self._sequence.__len__()

    @overload
    def __getitem__(self, i: int) -> List:
        ...

    @overload
    def __getitem__(self, s: slice) -> List:
        ...

    def __getitem__(self, __value) -> List:
        return self._sequence.__getitem__(__value)

    def append(self, __object) -> None:
        return self._sequence.append(__object)

    def extend(self, __iterable: Iterable) -> None:
        return self._sequence.extend(__iterable)
