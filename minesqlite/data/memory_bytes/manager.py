# coding=utf-8
# Author: @hsiaoxychen
import typing

from minesqlite.data.base import DataManagerABC, CursorABC
from minesqlite.sysconf.manager import SysConfManager

_KeyType = str
_RowType = dict


class Cursor(CursorABC):
    pass


class MemoryBytesDataManager(DataManagerABC):
    def __init__(self, sysconf: SysConfManager):
        super().__init__(sysconf)
        self._inner_data = {}

    def create_one(self, pk: _KeyType, kvs: _RowType):
        pass

    def read_one(self, pk: _KeyType):
        pass

    def next_row(self, cursor: typing.Optional[Cursor] = None) \
            -> typing.Tuple[Cursor, _RowType]:
        pass

    def update_one(self, pk: _KeyType, kvs: _RowType):
        pass

    def delete_one(self, pk: _KeyType):
        pass
