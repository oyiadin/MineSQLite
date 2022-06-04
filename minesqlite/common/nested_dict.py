# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import collections
import functools
import typing


_KT = typing.TypeVar('_KT')
_VT = typing.TypeVar('_VT')


class NestedDefaultDict(collections.MutableMapping):
    def __init__(self, default_factory):
        super().__init__()
        self._default_factory = default_factory
        self._data_factory = functools.partial(
            collections.defaultdict, default_factory)
        self._inner_data = self._data_factory()

    @staticmethod
    def split(key: _KT):
        return key.split('.')

    def __setitem__(self, k: _KT, v: _VT) -> None:
        data = self._inner_data
        parts = self.split(k)
        for part in parts[:-1]:
            data.setdefault(part, self._data_factory())
            data = data[part]

        data[parts[-1]] = v

    def __delitem__(self, k: _KT) -> None:
        parts = self.split(k)
        data = self['.'.join(parts[:-1])]
        data.__delitem__(parts[-1])

    def __getitem__(self, k: _KT) -> _VT:
        parts = self.split(k)
        data = self._inner_data
        for part in parts:
            data = data[part]
        return data

    def __len__(self) -> int:
        return len(self.keys())

    def __iter__(self) -> typing.Iterator:
        return NestedDefaultDictIterator(self)


class NestedDefaultDictIterator(collections.Iterator):
    def __init__(self, data: NestedDefaultDict):
        self.data = data

    def __iter__(self):
        return self

    def __next__(self) -> typing.Iterator[_KT]:
        yield from self.data.keys()
