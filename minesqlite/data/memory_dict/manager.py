# coding=utf-8
# Author: @hsiaoxychen
import typing

from minesqlite.data.base import DataManagerABC, CursorABC
from minesqlite.minesqlite import MineSQLite
from minesqlite.sysconf.manager import SysConfManager

_KeyType = str
_RowType = dict


class Cursor(CursorABC):
    def __init__(self, keys: typing.List[str],
                 index: int = 0):
        self.keys = keys
        self.index = index

    def __bool__(self):
        return self.index < len(self.keys)

    def next_cursor(self):
        new_cursor = Cursor(self.keys)
        new_cursor.index = self.index + 1
        return new_cursor


class MemoryDictDataManager(DataManagerABC):
    def __init__(self, instance: MineSQLite):
        super().__init__(instance)
        self._inner_data: typing.Dict[_KeyType, _RowType] = {}

    def _check_exists(self, pk: _KeyType) -> bool:
        if pk in self._inner_data:
            return True
        return False

    def create_one(self, pk: _KeyType, kvs: _RowType) -> _RowType:
        if self._check_exists(pk):
            raise ValueError("duplicate key: {}".format(pk))
        self._inner_data[pk] = kvs
        ret = self._inner_data[pk].copy()
        ret[self.instance.schema.primary_key] = pk
        return ret

    def read_one(self, pk: _KeyType) -> _RowType:
        if not self._check_exists(pk):
            raise ValueError("no such row primary_key={}".format(pk))
        ret = self._inner_data[pk].copy()
        ret[self.instance.schema.primary_key] = pk
        return ret

    def build_cursor(self) -> Cursor:
        return Cursor(list(self._inner_data.keys()))

    def next_row(self, cursor: typing.Optional[Cursor] = None) \
            -> typing.Tuple[Cursor, _RowType]:
        # TODO: how does redis implement cursor?
        pk = cursor.keys[cursor.index]
        ret = self._inner_data[pk].copy()
        ret[self.instance.schema.primary_key] = pk
        return cursor.next_cursor(), ret

    def update_one(self, pk: _KeyType, kvs: _RowType) -> _RowType:
        if not self._check_exists(pk):
            raise ValueError("no such row primary_key={}".format(pk))
        self._inner_data.setdefault(pk, {})
        self._inner_data[pk].update(kvs)
        ret = self._inner_data[pk].copy()
        ret[self.instance.schema.primary_key] = pk
        return ret

    def delete_one(self, pk: _KeyType) -> _RowType:
        if not self._check_exists(pk):
            raise ValueError("no such row primary_key={}".format(pk))
        ret = self._inner_data.pop(pk)  # no need to copy
        ret[self.instance.schema.primary_key] = pk
        return ret
