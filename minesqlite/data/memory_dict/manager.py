# coding=utf-8
# Author: @hsiaoxychen
import typing

from minesqlite.data.base import DataManagerABC, CursorABC
from minesqlite.sysconf.manager import SysConfManager

_KeyType = str
_RowType = dict


class Cursor(CursorABC):
    pass


class MemoryDictDataManager(DataManagerABC):
    def __init__(self, sysconf: SysConfManager):
        super().__init__(sysconf)
        self._inner_data: typing.Dict[_KeyType, _RowType] = {}

    def _check_exists(self, pk: _KeyType) -> bool:
        if pk in self._inner_data:
            return True
        return False

    def create_one(self, pk: _KeyType, kvs: _RowType) -> _RowType:
        if self._check_exists(pk):
            raise ValueError("duplicate key: {}".format(pk))
        self._inner_data[pk] = kvs
        return self._inner_data[pk]

    def read_one(self, pk: _KeyType) -> _RowType:
        if not self._check_exists(pk):
            raise ValueError("no such row primary_key={}".format(pk))
        return self._inner_data[pk]

    def next_row(self, cursor: typing.Optional[Cursor] = None) \
            -> typing.Tuple[Cursor, _RowType]:
        raise NotImplementedError

    def update_one(self, pk: _KeyType, kvs: _RowType) -> _RowType:
        if not self._check_exists(pk):
            raise ValueError("no such row primary_key={}".format(pk))
        self._inner_data.setdefault(pk, {})
        self._inner_data[pk].update(kvs)
        return self._inner_data[pk]

    def delete_one(self, pk: _KeyType) -> _RowType:
        if not self._check_exists(pk):
            raise ValueError("no such row primary_key={}".format(pk))
        return self._inner_data.pop(pk)
